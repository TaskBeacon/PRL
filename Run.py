from psyflow.screenflow import  *
from task.expsetup import exp_setup
from task.trialcontrol import generate_trial_seq
from task.expcontrol import exp_run
# all
subdata = get_subject_info()
subdata = ['144', '23', 'Male', 'Caucasian']
win, kb, settings = exp_setup(subdata)
trialseq = generate_trial_seq(settings)
print(trialseq.conditions)
print(trialseq.stims)
intro_test = (
        'You will perform a stop signal task. \n'
        'Press "q" for left arrow and "p" for right arrow as fast as possible! \n'
        'Sometimes the arrow color will turn red. \n'
        'If that happens, please withhold your response. \n'
        'Both fast responding and successful stopping are important. \n\n'
        'Press SPACE to continue.'
    )
show_instructions(win,intro_text=intro_test)
show_realtime_countdown(win)
exp_run(win, kb, settings, trialseq, subdata)
show_goodbye(win)