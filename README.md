# Monetary Incentive Delay (MID) Task

| Field                | Value                        |
|----------------------|------------------------------|
| Name                 | Monetary Incentive Delay (MID) Task |
| Version              | main (1.0)                          |
| URL / Repository     |https://github.com/TaskBeacon/MID  |
| Short Description    | A task measuring reward anticipation and feedback processing using adaptive timing |
| Created By           |Zhipeng Cao (zhipeng30@foxmail.com)   |
| Date Updated         |2025/06/21                |
| PsyFlow Version      |0.1.0                     |
| PsychoPy Version     |2025.1.1                  |
| Modality     |Behavior/EEG                  |


## 1. Task Overview

The Monetary Incentive Delay (MID) Task is designed to assess reward processing and motivational control. Participants respond to brief target stimuli that follow cues indicating potential monetary gain, loss, or neutral outcomes. By analyzing reaction times and success rates, the task evaluates anticipatory and feedback-related cognitive processes. An adaptive timing algorithm adjusts target durations based on participant performance, maintaining consistent task difficulty.

## 2. Task Flow

### Block-Level Flow

| Step                       | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| Load Config                | Load task configuration and subject form                                   |
| Collect Subject Info       | Collect demographic/subject info using `SubInfo` form                      |
| Setup Triggers             | Initialize trigger sender using serial port (COM3)                          |
| Initialize Window/Input    | Create PsychoPy window and keyboard handler                                |
| Load Stimuli               | Load all stimuli via `StimBank`, convert instructions to voice, preload    |
| Setup Controller           | Create adaptive controller from config                                     |
| Show Instructions          | Present text and voice instruction before starting                         |
| Loop Over Blocks           | For each block: countdown, run 60 trials, compute and show block feedback  |
| Show Goodbye               | Present final feedback with total score                                    |
| Save Data                  | Save all trial data to CSV                                                 |
| Close                      | Close serial port and quit PsychoPy                                        |

### Trial-Level Flow

| Step                | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| Cue                 | Show condition-specific cue (win/lose/neutral) with trigger                 |
| Anticipation        | Display fixation; allow response (early keypress logged)                   |
| Target              | Show target with adaptive duration; record response                        |
| Pre-feedback Fixation | Display fixation before feedback                                          |
| Feedback            | Present hit/miss feedback based on performance                             |
| Adaptive Update     | Update target duration based on hit/miss outcome                           |

### Controller Logic

| Feature             | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| Adaptive Duration   | Target duration adjusts between 0.04 and 0.37 seconds                       |
| Step Size           | ±0.03 seconds                                                               |
| Accuracy Target     | 66% accuracy threshold                                                      |
| Condition Specific  | Tracks performance separately by condition (win/lose/neutral)               |
| Logging             | Performance logs are printed to PsychoPy console                            |

## 3. Configuration Summary

### a. Subject Info

| Field       | Meaning                    |
|-------------|----------------------------|
| subject_id  | Unique participant number (101–999, 3 digits) |
| subname     | Participant name (pinyin)  |
| age         | Participant age (5–60)     |
| gender      | Participant gender (Male/Female) |

### b. Window Settings

| Parameter             | Value       |
|-----------------------|-------------|
| size                  | [1920, 1080]|
| units                 | deg         |
| screen                | 1           |
| bg_color              | gray        |
| fullscreen            | True        |
| monitor_width_cm      | 60          |
| monitor_distance_cm   | 72          |

### c. Stimuli

| Name                     | Type      | Description                                           |
|--------------------------|-----------|-------------------------------------------------------|
| fixation                 | text      | Central cross "+"                                     |
| win_cue                  | circle    | Magenta circle (reward)                               |
| lose_cue                 | rect      | Yellow square (punishment)                            |
| neut_cue                 | triangle  | Cyan triangle (neutral)                               |
| win_target               | circle    | Black circle target                                   |
| lose_target              | rect      | Black square target                                   |
| neut_target              | triangle  | Black triangle target                                 |
| win_hit_feedback         | textbox   | “击中 +10 分” (black text, SimHei)                    |
| win_miss_feedback        | textbox   | “未击中 +0 分”                                       |
| lose_hit_feedback        | textbox   | “击中 -0 分”                                         |
| lose_miss_feedback       | textbox   | “未击中 -10 分”                                      |
| neut_hit_feedback        | textbox   | “击中 +0 分”                                         |
| neut_miss_feedback       | textbox   | “未击中 -0 分”                                       |
| instruction_text         | textbox   | Multi-line Chinese instructions (includes scoring rules) |
| block_break              | text      | Inter-block message showing block, accuracy, and score |
| good_bye                 | text      | End screen showing final score                        |

### d. Timing

| Phase                 | Duration (s)        |
|------------------------|--------------------|
| cue                   | 0.3                |
| anticipation          | random 1.0–1.2     |
| target                | adaptive (0.04–0.37)|
| prefeedback fixation  | random 0.6–0.8     |
| feedback              | 1.0                |

### e. Triggers

| Event                    | Code  |
|--------------------------|-------|
| exp_onset                | 98    |
| exp_end                  | 99    |
| block_onset              | 100   |
| block_end                | 101   |
| win_cue_onset            | 10    |
| win_anti_onset           | 11    |
| win_target_onset         | 12    |
| win_hit_fb_onset         | 13    |
| win_miss_fb_onset        | 14    |
| win_key_press            | 15    |
| win_no_response          | 16    |
| lose_cue_onset           | 20    |
| lose_anti_onset          | 21    |
| lose_target_onset        | 22    |
| lose_hit_fb_onset        | 23    |
| lose_miss_fb_onset       | 24    |
| lose_key_press           | 25    |
| lose_no_response         | 26    |
| neut_cue_onset           | 30    |
| neut_anti_onset          | 31    |
| neut_target_onset        | 32    |
| neut_hit_fb_onset        | 33    |
| neut_miss_fb_onset       | 34    |
| neut_key_press           | 35    |
| neut_no_response         | 36    |
| fixation_onset           | 1     |

### f. Adaptive Controller

| Parameter          | Value    |
|--------------------|----------|
| initial_duration   | 0.2      |
| min_duration       | 0.04     |
| max_duration       | 0.37     |
| step               | 0.03     |
| target_accuracy    | 0.66     |
| condition_specific | true     |

## 4. Methods

Participants performed a computerized Monetary Incentive Delay (MID) task to assess motivational processing under different reward contingencies. The task consisted of **3 blocks**, each comprising **60 trials**, totaling **180 trials**. Each trial began with a cue, a colored shape (circle, square, or triangle), signaling whether the trial was a reward, punishment, or neutral condition. Following a variable anticipation phase (1.0–1.2 s), a black target appeared briefly. Participants were instructed to press the spacebar as quickly as possible upon target onset.

The target's presentation duration was controlled by an adaptive algorithm that updated the duration after each trial based on performance. Initial target duration was set to 0.2 s and was adjusted between 0.04 and 0.37 s using ±0.03 s increments to stabilize performance at a target accuracy of 66%, tracked separately by condition.

Feedback followed the target phase, based on whether participants responded within the target duration. “击中” (“hit”) and “未击中” (“miss”) messages were shown with point gain/loss specific to the cue type. After each block, a break screen summarized the participant's accuracy and cumulative score. The task began with audio-visual instructions and ended with a final message displaying total score. 

## 5. References
The task is originally developed by Knutson 2000:
>Knutson, B., Westdorp, A., Kaiser, E., & Hommer, D. (2000). FMRI visualization of brain activity during a monetary incentive delay task. Neuroimage, 12(1), 20-27.

Here, we adopted the ABCD Study design of the task:
>Casey, B. J., Cannonier, T., Conley, M. I., Cohen, A. O., Barch, D. M., Heitzeg, M. M., ... & Dale, A. M. (2018). The adolescent brain cognitive development (ABCD) study: imaging acquisition across 21 sites. Developmental cognitive neuroscience, 32, 43-54.