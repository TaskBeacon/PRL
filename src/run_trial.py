from psyflow import TrialUnit
from functools import partial
from .utils import Controller  
import numpy as np
def run_trial(
    win,
    kb,
    settings,
    condition: str,           # 'AB' or 'BA'
    stim_bank: dict,          
    controller: Controller,
    trigger_bank: dict,  
    trigger_sender = None,
          
):
    """
    Single PRL trial:
      1. fixation
      2. cue display + response highlight (via capture_response)
      3. stochastic feedback (+10/–10 based on rand < win_prob)
      4. ITI
    Returns a dict with all trial data (including rand_val, win_prob, reversal_count).
    """
    trial_data = {"condition": condition}
    make_unit = partial(TrialUnit, win=win, triggersender=trigger_sender)
    marker_pad = controller.reversal_count * 10
    # 1) Fixation
    make_unit(unit_label="fixation") \
        .add_stim(stim_bank.get("fixation")) \
        .show(
            duration=settings.fixation_duration,
            onset_trigger=trigger_bank.get("fixation_onset")+marker_pad,
        ) \
        .to_dict(trial_data)

    # 2) Cue + response collection
    if condition == "AB":
        stima = stim_bank.rebuild('stima',pos=(-4,0))
        stimb = stim_bank.rebuild('stimb',pos=(4,0))
    elif condition == "BA":
        stimb = stim_bank.rebuild('stimb',pos=(-4,0))
        stima = stim_bank.rebuild('stima',pos=(4,0))

    if controller.current_correct == "stima":
        correct_side = "left" if condition == "AB" else "right"
    else:
        correct_side = "left" if condition == "BA" else "right"

    cue = make_unit(unit_label="cue") \
        .add_stim(stima) \
        .add_stim(stimb)
    cue.capture_response(
        keys=settings.key_list,
        correct_keys = correct_side,
        duration=settings.cue_duration,
        onset_trigger=trigger_bank.get("cue_onset")+marker_pad,
        response_trigger=trigger_bank.get("key_press")+marker_pad,
        timeout_trigger=trigger_bank.get("no_response")+marker_pad,
        terminate_on_response=False,
        highlight_stim = {'left': stim_bank.get('highlight_left'), 'right': stim_bank.get('highlight_right')},
        dynamic_highlight=False,
    )
    

    # 4) Probabilistic feedback
    respond = cue.get_state('key_press', False)
    win_prob = controller.get_win_prob()
    if respond:
        rand_val = np.random.rand()
        hit = cue.get_state('hit', False)
        if hit:
            outcome = "win" if rand_val < win_prob else "lose"
            delta = settings.delta if rand_val < win_prob else settings.delta*-1
        else:
            outcome = "win" if rand_val < (1 - win_prob) else "lose"
            delta = settings.delta if rand_val < (1 - win_prob) else settings.delta*-1
    else:
        outcome = "no_response"
        delta = 0
        hit = False
        rand_val = np.nan

    cue.set_state(outcome=outcome, 
                  hit=hit, 
                  delta=delta,
                  win_prob=win_prob,
                  rand_val=rand_val)

    cue.to_dict(trial_data)



    # update controller (may flip mapping & increment reversal_count)
    controller.update(hit)

    # 5) Feedback display
    fb = make_unit(unit_label="feedback") \
        .add_stim(stim_bank.get(f"{outcome}_feedback")) \
        .show(
            duration=settings.feedback_duration,
            onset_trigger=trigger_bank.get(f"{outcome}_feedback_onset")+marker_pad,
        )
    fb.to_dict(trial_data)

    return trial_data
