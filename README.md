# Probabilistic Reversal Learning (PRL) Task – PsyFlow Version

This task implements a probabilistic reversal learning (PRL) paradigm to measure flexible decision-making and adaptation to changing reward contingencies. Participants must learn to choose the better option based on probabilistic feedback and adapt when the reward contingencies reverse. The task is built using the [PsyFlow](https://taskbeacon.github.io/psyflow/) framework.

---

## Task Overview

Participants are presented with two visual stimuli and must select one on each trial. One option initially yields a higher probability of winning points. However, across the task, the correct option will occasionally reverse. Participants must track feedback and flexibly adjust their choices based on observed outcomes.

This task is useful for studying reinforcement learning, flexibility, decision-making under uncertainty, and neuropsychiatric conditions like OCD, addiction, and depression.

---

## Task Flow

| Step        | Description |
|-|-|
| Instruction | A textbox (`instruction_text`) presents task instructions in Chinese. Participants press the **space bar** to start. |
| Fixation    | A fixation cross "+" is shown before each trial. |
| Cue Display | Two options appear; participants choose using the left/right arrow keys. |
| Feedback    | Feedback is probabilistic: +10 points (win) or -10 points (loss), with a chance of reversal. |
| Block Break | After each block, participants are given feedback on total score and allowed to rest. |
| Goodbye     | A final thank-you and score screen is displayed.

---

## Configuration Summary

All key settings are stored in the `config/config.yaml` file.

### Subject Info (`subinfo_fields`)
Participants are registered with:
- **Subject ID** (3-digit number from 101–999)
- **Session Name**
- **Experimenter Name**
- **Gender** (Male or Female)

Localized prompts are available via `subinfo_mapping`.

---

### Window Settings (`window`)
- Resolution: `1920 × 1080`
- Units: `deg`
- Fullscreen: `True`
- Monitor: `testMonitor`
- Background color: `gray`

---

### Stimuli (`stimuli`)
| Stimulus Name          | Type     | Description |
|-|-|-|
| `fixation`             | `text`   | Central fixation cross |
| `stima`, `stimb`       | `image`  | Left and right selectable stimuli |
| `highlight_left`, `highlight_right` | `rect` | Highlight box drawn around selected option |
| `win_feedback`         | `text`   | +10 points feedback |
| `lose_feedback`        | `text`   | -10 points feedback |
| `no_response_feedback` | `text`   | Penalty for missing a response |
| `block_break`          | `text`   | Mid-task rest break screen |
| `instruction_text`     | `textbox`| Detailed task instructions |
| `good_bye`             | `text`   | Final thank-you and score display |

---

### Timing (`timing`)
| Phase                 | Duration |
|-|-|
| Fixation              | 0.6–0.8 seconds (randomized) |
| Cue Display           | 1.5 seconds |
| Feedback Display      | 0.8 seconds |

---

### Conditions (`task.conditions`)
Participants are randomly assigned two option orders:
- `AB`: Stimulus A (left) vs Stimulus B (right)
- `BA`: Stimulus B (left) vs Stimulus A (right)

Choices and correct sides depend dynamically on the reversal controller.

---

### Probabilistic Feedback and Reversals (`controller`)
| Parameter              | Value |
|-|-|
| Initial Win Probability | 0.8 |
| Reversed Win Probability | 0.9 |
| Sliding Window Size     | 10 trials |
| Sliding Window Hits for Reversal | 9 |

Participants must maintain high accuracy within a moving window to trigger a reversal.

- Feedback is **probabilistic**: even correct choices sometimes lose points.
- After sufficient correct trials, **reward mappings flip**.

---

### Triggers (`triggers`)
Trigger events are sent for synchronization:

| Event                | Code |
|-|-|
| Experiment start     | 98 |
| Experiment end       | 99 |
| Block start          | 100 |
| Block end            | 101 |
| Fixation onset       | 1 |
| Cue onset            | 2 |
| Key press            | 3 |
| No response          | 4 |
| Win feedback onset   | 5 |
| Lose feedback onset  | 6 |
| No response feedback onset | 7 |

A marker padding system (multiplying reversal count) is used to differentiate reversal stages.

---

## Running the Task

```python
python main.py
```
