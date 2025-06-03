from psyflow import BlockUnit,StimBank, StimUnit,SubInfo,TaskSettings,TriggerSender
from psyflow import load_config,count_down, initialize_exp
import pandas as pd
from psychopy import core
from functools import partial
import serial
from src import run_trial, Controller

from functools import partial
import serial
import glob



# 1. Load config
cfg = load_config()

# 2. Collect subject info
subform = SubInfo(cfg['subform_config'])
subject_data = subform.collect()

# 3. Load task settings
settings = TaskSettings.from_dict(cfg['task_config'])
settings.add_subinfo(subject_data)

# 4. setup triggers
settings.triggers = cfg['trigger_config']
ser = serial.serial_for_url("loop://", baudrate=115200, timeout=1)
# ser = serial.Serial("COM3", baudrate=115200, timeout=1)
trigger_sender = TriggerSender(
    trigger_func=lambda code: ser.write([1, 225, 1, 0, (code)]),
    post_delay=0.001,
    on_trigger_start=lambda: ser.open() if not ser.is_open else None,
    on_trigger_end=lambda: ser.close()
)

# 5. Set up window & input
win, kb = initialize_exp(settings)
# 6. Setup stimulus bank
tmp_stim_bank = StimBank(win,cfg['stim_config'])\
                .convert_to_voice('instruction_text')\
                .preload_all()
# stim_bank.preview_all() 


# 7. Setup controller across blocks
settings.controller=cfg['controller_config']
settings.save_to_json() # save all settings to json file


files = sorted(glob.glob("assets/*.png"))
pairs = list(zip(files[::2], files[1::2])) # create pairs of images

trigger_sender.send(settings.triggers.get("exp_onset"))
# 8. Run experiment
StimUnit('instruction_text', win, kb)\
    .add_stim(tmp_stim_bank.get('instruction_text'))\
    .add_stim(tmp_stim_bank.get('instruction_text_voice'))\
    .wait_and_continue()

all_data = []
for block_i in range(settings.total_blocks):
    count_down(win, 3, color='white')
    stim_bank=StimBank(win)
    stima_img, stimb_img = pairs[block_i]
    block_stim= cfg['stim_config'].copy()
    block_stim['stima']['image'] = stima_img
    block_stim['stimb']['image'] = stimb_img
    stim_bank.add_from_dict(block_stim)
    stim_bank.preload_all()

    controller = Controller.from_dict(settings.controller) # controller is reset every block
    # 8. setup block
    block = BlockUnit(
        block_id=f"block_{block_i}",
        block_idx=block_i,
        settings=settings,
        window=win,
        keyboard=kb
    ).generate_conditions()\
    .on_start(lambda b: trigger_sender.send(settings.triggers.get("block_start")))\
    .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end")))\
    .run_trial(partial(run_trial, stim_bank=stim_bank, controller=controller, trigger_sender=trigger_sender))\
    .to_dict(all_data)

    block_trials = block.get_all_data()
    score = sum(trial.get('cue_delta', 0) for trial in block_trials)
    StimUnit('block',win,kb).add_stim(stim_bank.get_and_format('block_break', 
                                                                block_num=block_i+1, 
                                                                total_blocks=settings.total_blocks,
                                                                score=score)).wait_and_continue()

total_score = sum(trial.get('cue_delta', 0) for trial in all_data)
StimUnit('block',win,kb).add_stim(stim_bank.get_and_format('good_bye',total_score=total_score)).wait_and_continue(terminate=True)
trigger_sender.send(settings.triggers.get("exp_end"))
# 9. Save data
df = pd.DataFrame(all_data)
df.to_csv(settings.res_file, index=False)

# 10. Close everything
win.close()
core.quit()



