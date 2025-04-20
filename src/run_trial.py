from psyflow import TrialUnit
from functools import partial

def run_trial(win, kb, settings, condition, stim_bank, controller, trigger_sender, trigger_bank):
    """
    Run a single MID trial sequence (fixation → cue → anticipation → target → feedback).
    See full docstring above...
    """

    trial_data = {"condition": condition}
    make_unit = partial(TrialUnit, win=win, trigger_sender=trigger_sender)

    # --- Fixation ---
    make_unit(unit_label='fixation').add_stim(stim_bank.get("fixation")) \
        .show(duration=settings.fixation_duration, onset_trigger=trigger_bank.get("fixation_onset")) \
        .to_dict(trial_data)

    # --- Cue ---
    make_unit(unit_label='cue').add_stim(stim_bank.get(f"{condition}_cue")) \
        .show(duration=settings.cue_duration, onset_trigger=trigger_bank.get(f"{condition}_cue_onset")) \
        .to_dict(trial_data)


    # --- Anticipation ---
    anti=make_unit(unit_label='anticipation') \
        .add_stim(stim_bank.get("fixation")) 
    anti.capture_response(
            keys=settings.key_list,
            duration=settings.anticipation_duration,
            onset_trigger=trigger_bank.get(f"{condition}_anti_onset"),
            terminate_on_response=False)
        
    
    early_response = anti.get_state("response", False)
    anti.set_state(early_response=early_response)
    anti.to_dict(trial_data)

    # --- Target ---
    duration = controller.get_duration(condition)
    target = make_unit(unit_label="target") \
        .add_stim(stim_bank.get(f"{condition}_target"))
    target.capture_response(
            keys=settings.key_list,
            duration=duration,
            onset_trigger=trigger_bank.get(f"{condition}_target_onset"),
            response_trigger=trigger_bank.get(f"{condition}_key_press"),
            timeout_trigger=trigger_bank.get(f"{condition}_no_response"),
)
    target.to_dict(trial_data)

    
    # --- Feedback ---
    if early_response:
        delta = -10
        hit=False
    else:
        hit = target.get_state("hit", False)
        if condition == "win":
            delta = 10 if hit else 0
        elif condition == "lose":
            delta = 0 if hit else -10
        else:
            delta = 0
    controller.update(condition, hit)

    hit_type = "hit" if hit else "miss"
    fb_stim = stim_bank.get(f"{condition}_{hit_type}_feedback")
    fb = make_unit(unit_label="feedback") \
        .add_stim(fb_stim) \
        .show(duration=settings.feedback_duration, onset_trigger=trigger_bank.get(f"{condition}_{hit_type}_fb_onset"))
    fb.set_state(hit=hit, delta=delta).to_dict(trial_data)
    return trial_data

