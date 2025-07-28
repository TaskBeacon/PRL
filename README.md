# Probabilistic Reversal Learning (PRL) Task

| Field                | Value                        |
|----------------------|------------------------------|
| Name                 | Probabilistic Reversal Learning (PRL) Task |
| Version              | main (1.0)                          |
| URL / Repository     |https://github.com/TaskBeacon/PRL     |
| Short Description    | A task where participants learn stimulus-reward associations that reverse unpredictably. |
| Created By           |Zhipeng Cao (zhipeng30@foxmail.com)                       |
| Date Updated         | 2025-07-23                   |
| PsyFlow Version      |0.1.0                    |
| PsychoPy Version     |2025.1.1                   |
| Modality     |Behavior/EEG                  |
| Language | Chinese |
| Voice Name | zh-CN-YunyangNeural |

## 1. Task Overview
This task implements a probabilistic reversal learning paradigm designed for EEG studies. Participants are presented with two visual stimuli (images) and must learn which one has a higher probability of yielding a reward (+10 points). The reward contingencies are not fixed; after a certain number of correct choices, the probabilities reverse, requiring participants to adapt their strategy. The goal is to maximize the total score by tracking these changes and consistently choosing the more advantageous stimulus. The task consists of multiple blocks, and within each block, a new pair of stimuli is used.

## 2. Task Flow

### Block-Level Flow (`main.py`)

| Step | Description |
|---|---|
| 1. **Initialization** | Load configuration, collect subject information, and set up the PsychoPy window, keyboard, and trigger sender. |
| 2. **Instructions** | Display the task instructions text and play the corresponding voiceover. Wait for a spacebar press to continue. |
| 3. **Block Loop** | Iterate through the total number of blocks (`total_blocks`: 6). |
| 4. **Countdown** | Display a 3-second countdown before each block begins. |
| 5. **Stimulus Setup** | For each block, select a new pair of images (`stima` and `stimb`) from the `assets` folder. |
| 6. **Controller Reset** | A new `Controller` instance is created for each block, resetting the learning and reversal logic. |
| 7. **Run Trials** | Execute the trial-level logic (`run_trial.py`) for the number of trials in the block (`trial_per_block`: 40). |
| 8. **Block Break** | After each block, display a break screen showing the score for that block. Wait for a spacebar press to proceed to the next block. |
| 9. **End of Task** | After all blocks are completed, display a "good bye" screen with the total score. |
| 10. **Data Saving** | Save all recorded data to a CSV file. |
| 11. **Cleanup** | Close the serial port and quit the PsychoPy application. |

### Trial-Level Flow (`run_trial.py`)

| Step | Description |
|---|---|
| 1. **Fixation** | A fixation cross (`+`) is displayed for a random duration between 0.6 and 0.8 seconds. |
| 2. **Cue Presentation** | Two images (`stima` and `stimb`) are presented on the left and right sides of the screen. The positions are determined by the `condition` (`AB` or `BA`). |
| 3. **Response Collection** | The participant has 1.5 seconds (`cue_duration`) to choose one of the images by pressing 'f' for the left or 'j' for the right. A highlight box appears around the selected image. |
| 4. **Feedback Logic** | The outcome is determined probabilistically. If the correct stimulus is chosen, there is an 80% (`win_prob`) chance of winning +10 points and a 20% chance of losing 10 points. If the incorrect stimulus is chosen, the probabilities are reversed. No response results in a loss of 10 points. |
| 5. **Blank Screen** | A blank screen is shown for a random duration between 0.4 and 0.6 seconds. |
| 6. **Feedback Display** | The feedback ("+10分", "-10分", or "未反应：-10分") is displayed for 0.8 seconds (`feedback_duration`). |
| 7. **Controller Update** | The `Controller` is updated with the outcome of the trial (`hit` or `miss`). |

### Controller Logic (`utils.py`)

| Component | Description |
|---|---|
| **Reversal Mechanism** | The `Controller` uses a sliding window approach to determine when to reverse the stimulus-reward contingencies. |
| **Sliding Window** | The controller tracks the last 10 trials (`sliding_window`). |
| **Reversal Trigger** | If the participant correctly identifies the higher-probability stimulus in at least 9 of the last 10 trials (`sliding_window_hits`), the reward probabilities are reversed. |
| **State Tracking** | The controller tracks the `current_correct` stimulus ('stima' or 'stimb'), the `reversal_count`, and the history of hits within the current phase (`phase_hits`). |
| **Win Probability** | The initial win probability is 80% (`win_prob`). After the first reversal, it changes to 90% (`rev_win_prob`). |

## 3. Configuration Summary

### a. Subject Info

| Field | Description |
|---|---|
| `subject_id` | The unique identifier for the subject (3 digits, 101-999). |
| `subname` | The subject's name in Pinyin. |
| `age` | The subject's age (5-60). |
| `gender` | The subject's gender ('Male' or 'Female'). |

### b. Window Settings

| Parameter | Value |
|---|---|
| `size` | [1920, 1080] |
| `units` | deg |
| `screen` | 1 |
| `bg_color` | gray |
| `fullscreen` | True |
| `monitor_width_cm` | 60 |
| `monitor_distance_cm`| 72 |

### c. Stimuli

| Name | Type | Description |
|---|---|---|
| `fixation` | text | A white '+' symbol. |
| `win_feedback` | text | "+10分" in white. |
| `lose_feedback` | text | "-10分" in white. |
| `no_response_feedback`| text | "未反应：-10分" in white. |
| `blank` | text | An empty text stimulus. |
| `stima` | image | The first image in a pair, with a size of [5, 5] degrees. |
| `stimb` | image | The second image in a pair, with a size of [5, 5] degrees. |
| `highlight_left` | rect | A white rectangle to highlight the left stimulus. |
| `highlight_right` | rect | A white rectangle to highlight the right stimulus. |
| `block_break` | text | A multi-line text displaying the score at the end of a block. |
| `instruction_text` | textbox | The initial instructions for the task. |
| `good_bye` | text | The final message at the end of the experiment, showing the total score. |

### d. Timing

| Phase | Duration (seconds) |
|---|---|
| `fixation_duration` | [0.6, 0.8] (randomized) |
| `cue_duration` | 1.5 |
| `feedback_duration` | 0.8 |
| `blank_duration` | [0.4, 0.6] (randomized) |

### e. Triggers

| Event | Code |
|---|---|
| `exp_onset` | 98 |
| `exp_end` | 99 |
| `block_onset` | 100 |
| `block_end` | 101 |
| `fixation_onset` | 1 |
| `cue_onset` | 2 |
| `key_press` | 3 |
| `no_response` | 4 |
| `win_feedback_onset` | 5 |
| `lose_feedback_onset` | 6 |
| `no_response_feedback_onset` | 7 |

### f. Adaptive Controller

| Parameter | Value |
|---|---|
| `win_prob` | 0.8 |
| `rev_win_prob` | 0.9 |
| `sliding_window` | 10 |
| `sliding_window_hits` | 9 |

## 4. Methods (for academic publication)

In this experiment, participants performed a probabilistic reversal learning task. Each trial began with a central fixation cross, displayed for a variable duration of 600 to 800 ms. Subsequently, two distinct images were presented simultaneously on the left and right sides of the screen for 1500 ms. Participants were instructed to select one of the two images by pressing the 'f' key for the left image or the 'j' key for the right image. Following their response, a blank screen was shown for 400 to 600 ms, after which feedback was provided for 800 ms.

The task was structured into 6 blocks of 40 trials each. Within each block, one of the two images was designated as the "correct" stimulus, associated with an 80% probability of reward (+10 points) and a 20% probability of punishment (-10 points). The "incorrect" stimulus had the inverse probabilities. The reward contingencies were subject to reversal based on the participant's performance. A reversal was triggered when the participant chose the correct stimulus in at least 9 of the last 10 trials. Upon reversal, the previously "incorrect" stimulus became the "correct" one, and its associated win probability was increased to 90% for the remainder of the block to facilitate the learning of the new rule. This design allows for the examination of cognitive flexibility and reinforcement learning under changing environmental conditions.
