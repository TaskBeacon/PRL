import os
import numpy as np
import pandas as pd
from psychopy import visual, event, core, logging
from psyflow.screenflow import show_static_countdown

def exp_run(win, kb, settings, trialseq, subdata):
    """
    Runs the Probabilistic Reversal Learning (PRL) task.
    
    Trial procedure:
      1. Fixation cross for settings.fixDuration.
      2. Two stimulus images (left/right) are displayed for settings.cueDuration.
      3. A response is collected (using settings.keyList). 
         The cue and images are displayed for a fixed duration, but as soon as the key is pressed,
         a red rectangle is drawn around the chosen image for the remainder of the cue period.
      4. Feedback is provided for settings.fbDuration:
            - If the response is correct (matches the stimulus on the currently rewarded side),
              a reward (+10) is given with a certain probability (settings.win_prob during acquisition,
              settings.rev_win_prob after reversal); otherwise, points are deducted.
            - The random value (rand_val) used for deciding feedback and the win probability are logged.
      5. An inter-trial interval (ITI) is shown.
      
    Additionally, after each trial the code checks (using a sliding window of the last 10 trials)
    whether the reversal criterion is met (if 9 out of 10 trials are correct). If so, it reverses
    the reinforcement contingency by swapping settings.current_correct and increments settings.reversal_count.
    
    Block-level data is accumulated in a temporary container (blockdata). At the end of each block,
    block-wise feedback is shown, and the block data is saved.
    """
    # Setup logging
    log_filename = settings.outfile.replace('.csv', '.log')
    logging.LogFile(log_filename, level=logging.DATA, filemode='a')
    logging.console.setLevel(logging.INFO)
    event.globalKeys.clear()
    event.globalKeys.add(key='q', modifiers=['ctrl'], func=core.quit)
    event.Mouse(visible=False)

    # Prepare common visual components
    fix = visual.TextStim(win, text="+", height=1, color='black', pos=[0, 0])
    feedback_text = visual.TextStim(win, height=0.8, wrapWidth=25, color='black', pos=[0, 0])
    BlockFeedback = visual.TextStim(win, height=0.8, wrapWidth=25, color='black', pos=[0, 0])
    
    total_points = 0
    phase_hits = []

    # Initialize reinforcement contingency if not already present.
    if not hasattr(settings, 'current_correct'):
        settings.current_correct = "stima"  # default during acquisition
    if not hasattr(settings, 'reversal_count'):
        settings.reversal_count = 0

    # ---------------------------
    # Temporary container for block-level data
    class blockdata:
        pass

    # Initialize empty block-level arrays:
    blockdata.blockNum = np.array([], dtype=object)
    blockdata.cond = np.array([], dtype=object)       # conditions ("AB" / "BA")
    blockdata.stimAssign = np.array([], dtype=object)   # dictionary of stimulus assignment (using just basenames)
    blockdata.response = np.array([], dtype=object)     # chosen side
    blockdata.RT = np.array([], dtype=object)           # reaction times (ms)
    blockdata.points_trial = np.array([], dtype=object)   # trial points
    blockdata.acc = np.array([], dtype=object)          # accuracy (1=hit, 0=miss)

    # Extra fields to log:
    blockdata.correctSide = np.array([], dtype=object)  # the correct side for the trial
    blockdata.winProb = np.array([])                    # win probability used for the trial
    blockdata.randVal = np.array([])                    # random number used for feedback decision
    blockdata.isReversal = np.array([])                 # reversal flag (1 if reversal occurred on that trial)

    blockdata.DATA = None  # will hold stacked data for the block

    # Loop through all trials
    n_trials = len(trialseq.conditions)
    for i in range(n_trials):
        kb.clock.reset()
        event.clearEvents()
        trial_onset = core.getTime()

        # --- 1. Fixation ---
        fix.draw()
        win.flip()
        core.wait(settings.fixDuration)
        
        # --- 2. Stimulus presentation ---
        # Get stimulus assignment for this trial from trialseq.stims (a dict with keys "left" and "right")
        stim_assign = trialseq.stims[i]
        # stim_size can be in the window's units (e.g., norm, deg, or pix)
        stim_size = (5, 5)
        leftStim = visual.ImageStim(win, image=stim_assign["left"], pos=(-2, 0), size=stim_size)
        rightStim = visual.ImageStim(win, image=stim_assign["right"], pos=(2, 0), size=stim_size)

        # Start the cue display and response collection:
        cue_clock = core.Clock()
        chosen_side = None
        response_key = None
        RT = None

        # Draw the initial cue
        leftStim.draw()
        rightStim.draw()
        win.flip()

        # During the cue duration, monitor for a response.
        while cue_clock.getTime() < settings.cueDuration:
            keys = event.getKeys(keyList=settings.keyList, timeStamped=cue_clock)
            # When a response is received, record it if it hasn't been recorded yet.
            if keys and chosen_side is None:
                response_key, RT = keys[0]
                if response_key == settings.left_key:
                    chosen_side = "left"
                elif response_key == settings.right_key:
                    chosen_side = "right"
                
                # Prepare a highlight box (slightly larger than the stimulus)
                box_width = stim_size[0] * 0.6
                box_height = stim_size[1] * 0.8
                if chosen_side == "left":
                    highlight = visual.Rect(win, width=box_width, height=box_height, pos=(-2, 0),
                                            lineColor='red', lineWidth=3)
                elif chosen_side == "right":
                    highlight = visual.Rect(win, width=box_width, height=box_height, pos=(2, 0),
                                            lineColor='red', lineWidth=3)
                # Redraw the cue with the highlight overlaid.
                leftStim.draw()
                rightStim.draw()
                highlight.draw()
                win.flip()
        # If no response was made, record RT as full cueDuration.
        if RT is None:
            RT = settings.cueDuration

        # --- 4. Determine Correctness ---
        cond = trialseq.conditions[i]
        if settings.current_correct == "stima":
            correct_side = "left" if cond == "AB" else "right"
        elif settings.current_correct == "stimb":
            correct_side = "left" if cond == "BA" else "right"
        else:
            correct_side = None
        
        hit = (chosen_side == correct_side) if (chosen_side is not None) else False

        # Append hit for reversal checking.
        phase_hits.append(hit)
        if len(phase_hits) > 10:
            phase_hits.pop(0)

        # --- 5. Feedback (Probabilistic) ---
        if settings.reversal_count == 0:
            win_prob = settings.win_prob
        else:
            win_prob = settings.rev_win_prob

        rand_val = np.random.rand()  # Use one random value per trial
        if hit:
            outcome = "Correct" if rand_val < win_prob else "Prob Error"
            points_trial = 10 if rand_val < win_prob else -10
        else:
            outcome = "Lucky" if rand_val < (1 - win_prob) else "Incorrect"
            points_trial = 10 if rand_val < (1 - win_prob) else -10

        total_points += points_trial

        # Log trial information including the new parameters.
        logging.data(
            f"Trial {i+1}: Block={trialseq.blocknum[i]}, Condition={cond}, "
            f"ChosenSide={chosen_side}, CorrectSide={correct_side}, "
            f"Hit={hit}, RT={int(RT*1000)}ms, Points={points_trial}, TotalPoints={total_points}, "
            f"RandVal={rand_val:.4f}, WinProb={win_prob:.2f}, Outcome={outcome}, "
            f"Reversals={settings.reversal_count}, CurrentCorrect={settings.current_correct}"
        )

        # --- 6. Display feedback ---
        feedback_text.text = f"{outcome}\nTotal points: {total_points}"
        feedback_text.draw()
        win.flip()
        core.wait(settings.fbDuration)
        
        # --- 7. ITI ---
        fix.draw()
        win.flip()
        core.wait(settings.ITI)
        
        # Append block-level data
        blockdata.blockNum = np.hstack((blockdata.blockNum, trialseq.blocknum[i]))
        blockdata.cond = np.hstack((blockdata.cond, cond))
        short_stim_assign = {side: os.path.basename(path) for side, path in stim_assign.items()}
        blockdata.stimAssign = np.hstack((blockdata.stimAssign, [short_stim_assign]))
        blockdata.response = np.hstack((blockdata.response, chosen_side if chosen_side is not None else 0))
        blockdata.RT = np.hstack((blockdata.RT, int(RT * 1000)))
        blockdata.points_trial = np.hstack((blockdata.points_trial, points_trial))
        blockdata.acc = np.hstack((blockdata.acc, 1 if hit else 0))
        blockdata.correctSide = np.hstack((blockdata.correctSide, correct_side))
        blockdata.winProb = np.hstack((blockdata.winProb, win_prob))
        blockdata.randVal = np.hstack((blockdata.randVal, rand_val))
        # Mark reversal flag as 0 by default; it will be set to 1 if reversal is triggered.
        blockdata.isReversal = np.hstack((blockdata.isReversal, 0))
        
        # --- 8. Check Reversal Criterion ---
        if len(phase_hits) >= 10 and sum(phase_hits) >= 9:
            old_correct = settings.current_correct
            settings.current_correct = "stima" if settings.current_correct == "stimb" else "stimb"
            settings.reversal_count += 1
            phase_hits = []  # Reset window after reversal
            # Update reversal flag for this trial in blockdata:
            blockdata.isReversal[-1] = 1
            logging.data(f"Reversal triggered at trial {i+1}: {old_correct} -> {settings.current_correct}")
            # reversal_msg = visual.TextStim(win, text="Rule Change!", height=1.2, color="blue", pos=[0,0])
            # reversal_msg.draw()
            # win.flip()
            # core.wait(1.0)
        
        # --- 9. End-of-Block Processing ---
        if trialseq.BlockEndIdx[i] == 1:
            # Calculate block feedback: mean RT for go trials and accuracy.
            go_trials = np.where(blockdata.response != 0)[0]
            mean_RT = np.mean(blockdata.RT[go_trials]) if len(go_trials) > 0 else 0
            accuracy = np.mean(blockdata.acc) * 100 if len(blockdata.acc) > 0 else 0
            block_points = np.sum(blockdata.points_trial)
            
            BlockFeedback.text = (f"End of Block #{trialseq.blocknum[i]}\n"
                                  f"Mean RT: {mean_RT:.0f} ms\n"
                                  f"Accuracy: {accuracy:.1f}%\n"
                                  f"Block Points: {block_points}\n"
                                  "Press SPACE to continue...")
            BlockFeedback.draw()
            win.flip()
            event.waitKeys(keyList=['space'])
            
            # Stack block-level data into a matrix for saving.
            blockdata_np = {
                "Block": blockdata.blockNum.reshape(-1, 1),
                "Condition": blockdata.cond.reshape(-1, 1),
                "StimAssign": np.array(blockdata.stimAssign).reshape(-1, 1),
                "Response": blockdata.response.reshape(-1, 1),
                "RT": blockdata.RT.reshape(-1, 1),
                "TrialPoints": blockdata.points_trial.reshape(-1, 1),
                "Accuracy": blockdata.acc.reshape(-1, 1),
                "CorrectSide": blockdata.correctSide.reshape(-1, 1),
                "WinProb": blockdata.winProb.reshape(-1, 1),
                "RandVal": blockdata.randVal.reshape(-1, 1),
                "IsReversal": blockdata.isReversal.reshape(-1, 1)
            }
            temp = np.hstack(list(blockdata_np.values()))
            if trialseq.blocknum[i] == 1:
                blockdata.DATA = temp
            else:
                blockdata.DATA = np.vstack([blockdata.DATA, temp])
            
            df = pd.DataFrame(blockdata.DATA, columns=[
                "Block", "Condition", "StimAssign", "Response", "RT", 
                "TrialPoints", "Accuracy", "CorrectSide", "WinProb", "RandVal", "IsReversal"
            ])
            df.to_csv(settings.outfile, index=False)
            with open(settings.outfile, 'a') as f:
                f.write('\n' + ','.join(subdata))
            
            if trialseq.blocknum[i] < settings.TotalBlocks:
                # Reset block-level data arrays for the next block.
                blockdata.blockNum = np.array([], dtype=object)
                blockdata.cond = np.array([], dtype=object)
                blockdata.stimAssign = np.array([], dtype=object)
                blockdata.response = np.array([], dtype=object)
                blockdata.RT = np.array([], dtype=object)
                blockdata.points_trial = np.array([], dtype=object)
                blockdata.acc = np.array([], dtype=object)
                blockdata.correctSide = np.array([], dtype=object)
                blockdata.winProb = np.array([])
                blockdata.randVal = np.array([])
                blockdata.isReversal = np.array([])
                phase_hits = []
                
                # Optional: countdown before next block.
                show_static_countdown(win)
