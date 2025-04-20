from psyflow import TaskSettings
from psyflow import SubInfo
from psyflow import StimBank
from psyflow import BlockUnit
from psyflow import TrialUnit
from psyflow import TriggerSender
from psyflow import TriggerBank
from psyflow import generate_balanced_conditions

from psychopy.visual import Window
from psychopy.hardware import keyboard
from psychopy import logging, core

from functools import partial
import yaml
import sys
import serial
import glob

from src import run_trial,Controller



# 1. Load config
with open('config/config.yaml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 2. collect subject info
subform_config = {
    'subinfo_fields': config.get('subinfo_fields', []),
    'subinfo_mapping': config.get('subinfo_mapping', {})
}

subform = SubInfo(subform_config)
subject_data = subform.collect()
if subject_data is None:
    print("Participant cancelled — aborting experiment.")
    sys.exit(0)


# 3. Load task settings
# Flatten the config
task_config = {
    **config.get('window', {}),
    **config.get('task', {}),
    **config.get('timing', {})  # ← don't forget this!
}

settings = TaskSettings.from_dict(task_config)
settings.add_subinfo(subject_data)


# 4. Set up window & input
win = Window(size=settings.size, fullscr=settings.fullscreen, screen=1,
             monitor=settings.monitor, units=settings.units, color=settings.bg_color,
             gammaErrorPolicy='ignore')
kb = keyboard.Keyboard()
logging.setDefaultClock(core.Clock())
logging.LogFile(settings.log_file, level=logging.DATA, filemode='a')
logging.console.setLevel(logging.INFO)
settings.frame_time_seconds =win.monitorFramePeriod
settings.win_fps = win.getActualFrameRate()
settings.save_path = './data'


# 6. Setup trigger
trigger_config = {
    **config.get('triggers', {})
}
triggerbank = TriggerBank(trigger_config)
ser = serial.serial_for_url("loop://", baudrate=115200, timeout=1)
triggersender = TriggerSender(
    trigger_func=lambda code: ser.write([1, 225, 1, 0, (code)]),
    post_delay=0,
    on_trigger_start=lambda: ser.open() if not ser.is_open else None,
    on_trigger_end=lambda: ser.close()
)

# 7. setup controller
controller_config = {
    **config.get('controller', {})
    }

files = sorted(glob.glob("assets/*.png"))
pairs = list(zip(files[::2], files[1::2]))

stim_config={
    **config.get('stimuli', {})
}
all_data = []
for block_i in range(settings.total_blocks):
    stim_bank=StimBank(win)
    stima_img, stimb_img = pairs[block_i]
    cfg = stim_config.copy()
    cfg['stima']['image'] = stima_img
    cfg['stimb']['image'] = stimb_img
    stim_bank.add_from_dict(cfg)
    stim_bank.preload_all()

    controller = Controller.from_dict(controller_config)
    # 8. setup block
    block = BlockUnit(
        block_id=f"block_{block_i}",
        block_idx=block_i,
        settings=settings,
        window=win,
        keyboard=keyboard
    )

    block.generate_conditions(func=generate_balanced_conditions)

    @block.on_start
    def _block_start(b):
        print("Block start {}".format(b.block_idx))
        # b.logging_block_info()
        triggersender.send(triggerbank.get("block_onset"))
    @block.on_end
    def _block_end(b):     
        print("Block end {}".format(b.block_idx))
        triggersender.send(triggerbank.get("block_end"))
        print(b.summarize())
        # print(b.describe())
    
    # 9. run block
    block.run_trial(
        partial(run_trial, stim_bank=stim_bank, controller=controller, trigger_sender=triggersender, trigger_bank=triggerbank)
    )
    
    block.to_dict(all_data)
    if block_i < settings.total_blocks - 1:
        TrialUnit(win, 'block').add_stim(stim_bank.get('block_break')).wait_and_continue()
    else:
        TrialUnit(win, 'block').add_stim(stim_bank.get_and_format('good_bye', reward=100)).wait_and_continue(terminate=True)
    
import pandas as pd
df = pd.DataFrame(all_data)
df.to_csv(settings.res_file, index=False)



