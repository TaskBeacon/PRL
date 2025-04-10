from psychopy import visual, event, core, logging
import numpy as np
import pandas as pd
from psyflow.screenflow import show_static_countdown

def exp_run(win, kb, settings, trialseq, subdata):
    log_filename = settings.outfile.replace('.csv', '.log')
    logging.LogFile(log_filename, level=logging.DATA, filemode='a')
    logging.console.setLevel(logging.INFO)
    event.globalKeys.clear()
    event.globalKeys.add(key='q', modifiers=['ctrl'], func=core.quit)
    event.Mouse(visible=False)  # hide mouse cursor
    # Prepare visual components
    fix = visual.TextStim(win, height=1, text="+", wrapWidth=10, color='black', pos=[0, 0])
    warning = visual.TextStim(win, text="TOO SLOW!!!", height=.6, wrapWidth=10, color='red', pos=[0, 0])
    BlockFeedback = visual.TextStim(win, height=.6, wrapWidth=25, color='black', pos=[0, 0])

    # Extract shortcut parameters from settings
    LeftSSD = settings.initSSD     # Initial stop-signal delay for left trials
    RightSSD = settings.initSSD    # Initial stop-signal delay for right trials
    stairsize = settings.staircase # Step size for staircase SSD adjustment
    keyList = settings.keyList     # Allowed response keys
    left_key = settings.left_key   # Key for left arrow
    right_key = settings.right_key # Key for right arrow

    # Temporary container for block-level data
    class blockdata:
        pass

    # Initialize empty data fields
    blockdata.arrow = []      # Presented arrow direction (1=left, 2=right)
    blockdata.resp = []       # Response key (1=left_key, 2=right_key, 0=none)
    blockdata.LeftSSD = []    # Left SSD
    blockdata.RightSSD = []   # Right SSD   
    blockdata.RT = []         # Reaction time
    blockdata.acc = []        # Accuracy (1=correct, 0=wrong, -1=miss, 3=successful stop, 4=failed stop)
    blockdata.DATA = []       # Matrix for saving after each block
    blockdata.GOidx = []      # 1=Go trial, 0=Stop trial
    blockdata.blockNum = []   # Block number

    # Loop through all trials
    for i in range(len(trialseq.conditions)):
        kb.clock.reset()
        kb.clearEvents()
        StopSignal = []

        # Choose stimulus type for this trial
        if trialseq.stims[i] == 'left':  # left arrow
            arrow = settings.Larrow
            if trialseq.conditions[i] == 'stop':
                if settings.useUpArrowStop:
                    StopSignal = settings.UparrowSTOP
                else:
                    StopSignal = settings.LarrowSTOP
        else:  # right arrow
            arrow = settings.Rarrow
            if trialseq.conditions[i] == 'stop':
                if settings.useUpArrowStop:
                    StopSignal = settings.UparrowSTOP
                else:
                    StopSignal = settings.RarrowSTOP

        trial_onset = core.getTime()

        # Fixation cross
        fix.draw()
        win.flip()
        core.wait(0.5)

        # Show black arrow (Go stimulus)
        arrow.draw()
        win.flip()
        arrow_onset = core.getTime()

        # -------------------------
        # ▶️ Go Trial
        # -------------------------
        if trialseq.conditions[i] == 'go':
            blockdata.GOidx = np.hstack((blockdata.GOidx, 1))  # Mark as Go trial
            event.clearEvents()
            resp = event.waitKeys(maxWait=settings.arrowDuration, keyList=keyList)

            if resp:  # A response was made
                RT = core.getTime() - arrow_onset
                key = resp[0]
                if trialseq.stims[i] == 'left' and key == left_key:
                    acc = 1  # correct
                elif trialseq.stims[i] == 'right' and key == right_key:
                    acc = 1  # correct
                else:
                    acc = 0  # wrong key
            else:  # No response
                acc = -1
                RT = 0
                warning.draw()
                win.flip()
                core.wait(settings.trialDuration - (core.getTime() - trial_onset))

        # -------------------------
        # ⛔ Stop Trial
        # -------------------------
        else:
            blockdata.GOidx = np.hstack((blockdata.GOidx, 0))  # Mark as Stop trial
            event.clearEvents()

            # Wait for SSD (delay before showing StopSignal)
            if trialseq.stims[i] == 'left':
                core.wait(LeftSSD / 1000)
            else:
                core.wait(RightSSD / 1000)

            # Show red arrow (Stop signal)
            StopSignal.draw()
            win.flip()
            arrow_onset = core.getTime()

            # Wait for remaining response time
            if trialseq.stims[i] == 'left': # left arrow
                resp = event.waitKeys(maxWait=settings.arrowDuration - LeftSSD / 1000, keyList=keyList)
                if resp:
                    acc = 4  # failed to stop
                    RT = core.getTime() - arrow_onset
                    LeftSSD = max(LeftSSD - stairsize, 0)
                else:
                    acc = 3  # successfully stopped
                    RT = 0
                    LeftSSD += stairsize
            else:
                resp = event.waitKeys(maxWait=settings.arrowDuration - RightSSD / 1000, keyList=keyList)
                if resp:
                    acc = 4 # failed to stop
                    RT = core.getTime() - arrow_onset
                    RightSSD = max(RightSSD - stairsize, 0)
                else:
                    acc = 3 # successfully stopped
                    RT = 0
                    RightSSD += stairsize
            
        # save resp_code
        if resp and resp[0] == left_key:
            resp_code = left_key
        elif resp and resp[0] == right_key:
            resp_code = right_key
        else:
            resp_code = 0
        logging.data(f"Trial {i+1}: Block={trialseq.blocknum[i]}, Type={'GO' if trialseq.conditions[i]=='go' else 'STOP'}, "
            f"Arrow={trialseq.stims[i]}, Resp={resp_code}, ACC={acc}, RT={int(RT*1000)}ms")
        # Save data for this trial
        blockdata.RT = np.hstack((blockdata.RT, int(RT * 1000)))  # Convert to ms
        blockdata.arrow = np.hstack((blockdata.arrow, [trialseq.stims[i]]))
        blockdata.resp = np.hstack((blockdata.resp, resp_code))
        blockdata.blockNum = np.hstack((blockdata.blockNum, trialseq.blocknum[i]))
        blockdata.acc = np.hstack((blockdata.acc, acc))
        blockdata.LeftSSD = np.hstack((blockdata.LeftSSD, LeftSSD))
        blockdata.RightSSD = np.hstack((blockdata.RightSSD, RightSSD))

        # Inter-trial interval (only if not a miss)
        if acc != -1:
            fix.draw()
            win.flip()
            core.wait(2.5 - (core.getTime() - trial_onset))

        # -------------------------------------
        # End of block → compute feedback
        # -------------------------------------
        if trialseq.BlockEndIdx[i] == 1:
            STOPidx = blockdata.GOidx == 0
            MISSidx = blockdata.acc == -1
            RJTidx = STOPidx + MISSidx
            GOrtOnly = np.delete(blockdata.RT, np.where(RJTidx), 0)
            meanGOrt = np.mean(GOrtOnly)
            GOtrials = np.sum(blockdata.GOidx == 1)
            CorrectGO = np.sum(blockdata.acc == 1)
            STOPtrials = np.sum(blockdata.GOidx == 0)
            SuccesfulStop = np.sum(blockdata.acc == 3)

            # Create feedback text
            BlockFeedback.text = f"End of Block #{trialseq.blocknum[i]}\n"
            BlockFeedback.text += f"Mean GO RT : {meanGOrt:.2f} ms\n"
            BlockFeedback.text += f"Accuracy : {CorrectGO / GOtrials * 100:.2f} %\n"
            BlockFeedback.text += f"p(STOP) : {SuccesfulStop / STOPtrials * 100:.2f} %\n"
            BlockFeedback.text += "Press SPACE to continue..."

            # Stack trial data into a single matrix
            blockdata_np = {
                        "Block": np.array(blockdata.blockNum, dtype=object).reshape(-1, 1),
                        "TrialType": np.array(['go' if v == 1 else 'stop' for v in blockdata.GOidx], dtype=object).reshape(-1, 1),
                        "Arrow": np.array(blockdata.arrow, dtype=object).reshape(-1, 1),
                        "Response": np.array(blockdata.resp, dtype=object).reshape(-1, 1),
                        "leftSSD": np.array(blockdata.LeftSSD, dtype=object).reshape(-1, 1),
                        "rightSSD": np.array(blockdata.RightSSD, dtype=object).reshape(-1, 1),
                        "ResponseType": np.array([{1: 'correct', 0: 'wrong_key', -1: 'miss', 3: 'success_stop', 4: 'fail_stop'}.get(a, 'unknown')
                                                    for a in blockdata.acc
                                                ], dtype=object).reshape(-1, 1),
                        "RT": np.array(blockdata.RT, dtype=object).reshape(-1, 1)}
            
            temp = np.hstack(list(blockdata_np.values()))

            # Save data to block-level matrix
            if trialseq.blocknum[i] == 1:
                blockdata.DATA = temp
            else:
                blockdata.DATA = np.vstack([blockdata.DATA, temp])

            # Save to CSV
            df = pd.DataFrame(blockdata.DATA, columns=["Block", "TrialType", "Arrow", "Response", "leftSSD", "rightSSD", "ResponseType", "RT"])
            df.to_csv(settings.outfile, index=False)
            with open(settings.outfile, 'a') as f:
                f.write('\n' + ','.join(subdata))

            # Display block feedback (wait for key)
            while not event.getKeys(keyList=['space']):
                BlockFeedback.draw()
                win.flip()

            # Optional feedback based on stopping performance
            if trialseq.blocknum[i] < settings.TotalBlocks:
                PerformanceFeedback = visual.TextStim(win, height=.6, wrapWidth=25, color='black', pos=[0, 0])
                stop_rate = SuccesfulStop / STOPtrials
                if stop_rate <= .45:
                    PerformanceFeedback.text = (
                        "You're fast, but not stopping well.\n"
                        "Focus more on stopping in the next block.\nThanks."
                    )
                elif stop_rate >= .55:
                    PerformanceFeedback.text = (
                        "You're stopping well, but responding slowly.\n"
                        "Try to respond faster in the next block.\nThanks."
                    )
                else:
                    PerformanceFeedback.text = "You're doing great!\nKeep it up!"
                PerformanceFeedback.text+= "Press SPACE to continue..."

                while not event.getKeys(keyList=['space']):
                    PerformanceFeedback.draw()
                    win.flip()

                # Reset data containers for next block
                blockdata.arrow = []
                blockdata.resp = []
                blockdata.LeftSSD = []
                blockdata.RightSSD = []
                blockdata.RT = []
                blockdata.acc = []
                blockdata.GOidx = []
                blockdata.blockNum = []

                # Countdown before next block
                show_static_countdown(win)
