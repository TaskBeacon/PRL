from psyflow import TrialUnit
from functools import partial
from .utils import Controller  

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

    # 1) Fixation
    make_unit(unit_label="fixation") \
        .add_stim(stim_bank["fixation"]) \
        .show(
            duration=settings.fixDuration,
            onset_trigger=trigger_bank["fixation_onset"]
        ) \
        .to_dict(trial_data)

    # 2) Cue + response collection
    if condition == "AB":
        stima = stim_bank.get("stima").position(4,0)
        stimb = stim_bank.get("stimb").position(-4,0)
    else:
        stima = stim_bank.get("stimb").position(4,0)
        stimb = stim_bank.get("stima").position(-4,0)

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
        onset_trigger=trigger_bank[f"{condition}_cue_onset"],
        response_trigger=trigger_bank[f"{condition}_key_press"],
        timeout_trigger=trigger_bank[f"{condition}_no_response"],
        terminate_on_response=False,
        highlight_stim = {'left': stim_bank.get('highlight_left'), 'right': stim_bank.get('highlight_right')},
        dynamic_highligt=False,
    )
    cue.to_dict(trial_data)

    # 4) Probabilistic feedback
    win_prob = controller.get_win_prob()
    rand_val = np.random.rand()
    if chosen_side is None:
        outcome = "lose"   # treat no-response as loss
        delta = -10
    else:
        if hit:
            outcome = "win" if rand_val < win_prob else "lose"
            delta = 10 if rand_val < win_prob else -10
        else:
            outcome = "win" if rand_val < (1 - win_prob) else "lose"
            delta = 10 if rand_val < (1 - win_prob) else -10

    # update controller (may flip mapping & increment reversal_count)
    controller.update(hit)

    # 5) Feedback display
    fb = make_unit(unit_label="feedback") \
        .add_stim(stim_bank[f"{outcome}_feedback"]) \
        .show(
            duration=settings.fbDuration,
            onset_trigger=trigger_bank[f"{outcome}_fb_onset"]
        )
    fb.set_state(
        chosen_side=chosen_side,
        correct_side=correct_side,
        hit=hit,
        win_prob=win_prob,
        rand_val=rand_val,
        delta=delta,
        reversal_count=controller.reversal_count
    ).to_dict(trial_data)

    # 6) ITI
    make_unit(unit_label="iti") \
        .add_stim(stim_bank["fixation"]) \
        .show(
            duration=settings.ITI,
            onset_trigger=trigger_bank["iti_onset"]
        ) \
        .to_dict(trial_data)

    return trial_data
