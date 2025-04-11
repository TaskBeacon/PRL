import numpy as np
import random
from types import SimpleNamespace


def generate_trial_seq(settings, seed=None):
    """
    Generates the trial sequence for the PRL task.
    
    For each block, using the balanced condition generator we create a counterbalanced
    array of condition labels ("AB" and "BA"). Then stimulus assignments are generated
    based on the image pair for that block.
    
    Parameters
    ----------
    settings : SimpleNamespace
        Experiment settings. Must contain:
            - TotalBlocks (int)
            - TotalTrials (int)
            - TrialsPerBlock (int)
            - imagePairs (dict): keys (1-indexed) mapping to dicts with "stima" and "stimb"
    seed : int or None, optional
        Optional seed, used as a base to generate block-specific seeds.
    
    Returns
    -------
    trialseq : SimpleNamespace
        Contains:
          - blocknum: Array of block numbers per trial.
          - BlockEndIdx: Array with a 1 marking the last trial of each block.
          - conditions: Array of condition labels ("AB", "BA").
          - stims: Array of dictionaries; each dict has keys "left" and "right" with image paths.
    """
    TotalBlocks = settings.TotalBlocks
    TotalTrials = settings.TotalTrials
    TrialsPerBlock = settings.TrialsPerBlock

    ALLconditions = np.empty(TotalTrials, dtype=object)
    ALLblocknum = np.zeros(TotalTrials, dtype=int)
    ALLblockEndIdx = np.zeros(TotalTrials, dtype=int)
    ALLstims = np.empty(TotalTrials, dtype=object)

    base_seed = seed if seed is not None else random.randint(0, 10000)

    for block_i in range(1, TotalBlocks + 1):
        block_start = (block_i - 1) * TrialsPerBlock
        block_end = block_i * TrialsPerBlock

        blocknum = np.full(TrialsPerBlock, block_i, dtype=int)
        blockEndIdx = np.zeros(TrialsPerBlock, dtype=int)
        blockEndIdx[-1] = 1  # Mark end of block

        block_seed = base_seed + block_i
        # Use generate_balanced_conditions with condition_labels ["AB", "BA"]
        conditions = generate_balanced_conditions(TrialsPerBlock, ["AB", "BA"], seed=block_seed)
        # Get the image pair for the current block from settings.imagePairs
        stimPair = settings.imagePairs[block_i]
        stim_seq = assign_stimType(conditions, stimPair, seed=block_seed)

        ALLconditions[block_start:block_end] = conditions
        ALLblocknum[block_start:block_end] = blocknum
        ALLblockEndIdx[block_start:block_end] = blockEndIdx
        ALLstims[block_start:block_end] = stim_seq

    if not (len(ALLconditions) == len(ALLblocknum) == len(ALLstims) == TotalTrials):
        raise ValueError("Trial sequence size mismatch!")

    trialseq = SimpleNamespace()
    trialseq.blocknum = ALLblocknum
    trialseq.BlockEndIdx = ALLblockEndIdx
    trialseq.conditions = ALLconditions
    trialseq.stims = ALLstims
    return trialseq


def generate_balanced_conditions(n_trials, condition_labels, seed=None):
    """
    Generates a balanced and shuffled sequence of conditions.
    
    Parameters
    ----------
    n_trials : int
        Total number of trials in the block.
    condition_labels : list of str
        List of condition labels (e.g., ["AB", "BA"]).
    seed : int or None, optional
        Optional seed for reproducibility.
    
    Returns
    -------
    np.ndarray
        An array of condition labels balanced over n_trials.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    n_conditions = len(condition_labels)
    trials_per_condition = n_trials // n_conditions
    remainder = n_trials % n_conditions

    condition_list = []
    for label in condition_labels:
        condition_list.extend([label] * trials_per_condition)

    if remainder > 0:
        extras = random.choices(condition_labels, k=remainder)
        condition_list.extend(extras)

    random.shuffle(condition_list)
    return np.array(condition_list)


def assign_stimType(conditions, stimPair, seed=None):
    """
    Assigns stimulus positions on each trial based on the condition labels.
    
    For "AB": assign stimPair["stima"] to left and stimPair["stimb"] to right.
    For "BA": swap the assignments.
    
    Parameters
    ----------
    conditions : np.ndarray of str
        Array of condition labels ("AB" or "BA") for each trial.
    stimPair : dict
        Dictionary with keys "stima" and "stimb" (file paths).
    seed : int or None, optional
        Seed for reproducibility (unused here but provided for consistency).
    
    Returns
    -------
    np.ndarray of dict
        An array where each entry is a dict with keys "left" and "right".
    """
    stim_seq = []
    for cond in conditions:
        if cond == "AB":
            stim_seq.append({"left": stimPair["stima"], "right": stimPair["stimb"]})
        elif cond == "BA":
            stim_seq.append({"left": stimPair["stimb"], "right": stimPair["stima"]})
        else:
            raise ValueError("Condition must be 'AB' or 'BA'.")
    return np.array(stim_seq)