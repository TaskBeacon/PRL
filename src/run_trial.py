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
            duration=settings.fixDuration,
            onset_trigger=trigger_bank.get("fixation_onset")+marker_pad,
        ) \
        .to_dict(trial_data)

    # 2) Cue + response collection
    if condition == "AB":
        stima = stim_bank.get("stima").pos(4,0)
        stimb = stim_bank.get("stimb").pos(-4,0)
    else:
        stima = stim_bank.get("stimb").pos(4,0)
        stimb = stim_bank.get("stima").pos(-4,0)

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
        onset_trigger=trigger_bank.get(f"{condition}_cue_onset")+marker_pad,
        response_trigger=trigger_bank.get(f"{condition}_key_press")+marker_pad,
        timeout_trigger=trigger_bank.get(f"{condition}_no_response")+marker_pad,
        terminate_on_response=False,
        highlight_stim = {'left': stim_bank.get('highlight_left'), 'right': stim_bank.get('highlight_right')},
        dynamic_highligt=False,
    )
    cue.to_dict(trial_data)

    # 4) Probabilistic feedback
    respond = cue.get_state('key_pressed', False)
    if respond:
        rand_val = np.random.rand()
        hit = cue.get_state('hit', False)
        if hit:
            outcome = "win" if rand_val < settings.win_prob else "lose"
            delta = + settings.delta if rand_val < settings.win_prob else - settings.delta
        else:
            outcome = "win" if rand_val < (1 - settings.win_prob) else "lose"
            delta = + settings.delta if rand_val < (1 - settings.win_prob) else - settings.delta
    else:
        outcome = "no_response"
        delta = 0



    # update controller (may flip mapping & increment reversal_count)
    controller.update(hit)

    # 5) Feedback display
    fb = make_unit(unit_label="feedback") \
        .add_stim(stim_bank.get(f"{outcome}_feedback")) \
        .show(
            duration=settings.fbDuration,
            onset_trigger=trigger_bank.get(f"{condition}_feedback_onset")+marker_pad,
        )
    fb.to_dict(trial_data)


    return trial_data
