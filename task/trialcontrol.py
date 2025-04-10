import numpy as np
import random
from types import SimpleNamespace
import warnings


def generate_trial_seq(settings):
    """
    Generates a trial sequence for the stop-signal task using string-based labels.

    Each trial is labeled with:
        - Condition: 'go' or 'stop'
        - Stimulus: typically 'left' or 'right'
        - Block number and block end flag

    Parameters
    ----------
    settings : SimpleNamespace
        Experiment settings, must include:
            - TotalBlocks (int): number of blocks
            - TotalTrials (int): total number of trials
            - TrialsPerBlock (int): trials per block
            - arrowTypes (list[str]): e.g., ['left', 'right']
            - blockSeed (list[int] or None): optional list of random seeds for reproducibility

    Returns
    -------
    trialseq : SimpleNamespace
        Structured output with the following fields:
            - blocknum (np.ndarray): Block index for each trial
            - BlockEndIdx (np.ndarray): Binary array marking end of blocks
            - condition (np.ndarray): 'go' or 'stop' for each trial
            - stim (np.ndarray): stimulus label (e.g., 'left', 'right') for each trial
    """
    TotalBlocks = settings.TotalBlocks
    TotalTrials = settings.TotalTrials
    TrialsPerBlock = settings.TrialsPerBlock
    stimTypes = settings.arrowTypes  # ['left', 'right']

    ALLconditions = np.empty(TotalTrials, dtype=object)
    ALLstims = np.empty(TotalTrials, dtype=object)
    ALLblocknum = np.zeros(TotalTrials, dtype=int)
    ALLblockEndIdx = np.zeros(TotalTrials, dtype=int)

    for block_i in range(TotalBlocks):
        block_start = block_i * TrialsPerBlock
        block_end = (block_i + 1) * TrialsPerBlock

        blocknum = np.full(TrialsPerBlock, block_i + 1, dtype=int)
        blockEndIdx = np.zeros(TrialsPerBlock, dtype=int)
        blockEndIdx[-1] = 1  # Mark end of block

        block_seed = None
        if settings.blockSeed is not None:
            block_seed = int(settings.blockSeed[block_i])


        # Step 1: Generate valid trial types ('go'/'stop')
        conditions = generate_valid_conditions(
            n_trials=TrialsPerBlock,
            stop_ratio=1/3,
            max_stop_run=4,
            min_go_start=3,
            seed=block_seed  # Don't pass seed inside the loop, already seeded above
        )

        # Step 2: Assign stimulus directions ('left'/'right')
        stim_seq = assign_stimType(conditions, stimTypes, seed=block_seed)

        # Step 3: Store in full arrays
        ALLconditions[block_start:block_end] = conditions
        ALLstims[block_start:block_end] = stim_seq
        ALLblocknum[block_start:block_end] = blocknum
        ALLblockEndIdx[block_start:block_end] = blockEndIdx

    if not (len(ALLconditions) == len(ALLblocknum) == len(ALLstims) == TotalTrials):
        warnings.warn("Trial sequence size mismatch!")

    # Return as structured object
    trialseq = SimpleNamespace()
    trialseq.blocknum = ALLblocknum
    trialseq.BlockEndIdx = ALLblockEndIdx
    trialseq.conditions = ALLconditions
    trialseq.stims = ALLstims

    return trialseq


def generate_valid_conditions(n_trials, stop_ratio=1/3, max_stop_run=4, min_go_start=3, seed=None):
    """
    Generate a valid trial sequence of 'go' and 'stop' conditions for a stop-signal task.

    This function creates a randomized sequence of trial types ('go' and 'stop') while enforcing
    important constraints:
        1. The first `min_go_start` trials must be all 'go'.
        2. No more than `max_stop_run` 'stop' trials are allowed in any sliding window of 5 trials.
        3. The total number of 'go' and 'stop' trials matches the given stop ratio.
        4. If a seed is provided, the result is reproducible.

    Parameters
    ----------
    n_trials : int
        Total number of trials in the sequence.
    stop_ratio : float, optional
        Proportion of 'stop' trials in the sequence (default is 1/3).
    max_stop_run : int, optional
        Maximum allowed number of 'stop' trials in any 5-trial sliding window (default is 4).
    min_go_start : int, optional
        Number of initial trials that must all be 'go' (default is 3).
    seed : int or None, optional
        Optional random seed for reproducibility (default is None).

    Returns
    -------
    conditions : np.ndarray of str
        An array of length `n_trials`, with each entry being either 'go' or 'stop', satisfying all constraints.

    Notes
    -----
    - The function may loop multiple times to find a valid sequence that meets all constraints.
    - If the constraints are too tight (e.g., too high a `stop_ratio` with a low `max_stop_run`),
      the function may take longer to succeed.
    """

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # import random
    # random.seed(123)
    # for _ in range(5):
    #     lst = [1, 2, 3, 4, 5]
    #     random.shuffle(lst)
    #     print(lst)
    # [3, 2, 5, 1, 4]
    # [2, 3, 1, 5, 4]
    # [5, 1, 4, 2, 3]
    # [3, 1, 2, 5, 4]
    # [2, 1, 4, 3, 5]

    

    n_stop = int(n_trials * stop_ratio)
    n_go = n_trials - n_stop

    sflag = False
    attempt = 0
    while not sflag:
        attempt += 1
        trial_types = ['go'] * n_go + ['stop'] * n_stop
        random.shuffle(trial_types)
        conditions = np.array(trial_types)

        if any(r != 'go' for r in conditions[:min_go_start]):
            continue

        window_sums = [sum(r == 'stop' for r in conditions[i:i+5]) for i in range(n_trials - 4)]
        if any(w > max_stop_run for w in window_sums):
            continue

        sflag = True

    return conditions



def assign_stimType(conditions, stimTypes, seed=None):
    """
    Assign randomized stimulus directions ('left' or 'right') for 'go' and 'stop' trials.

    Each trial receives a stimulus direction independently, while ensuring a balanced and shuffled
    distribution of the provided stimTypes (e.g., ['left', 'right']) across 'go' and 'stop' trials.

    Parameters
    ----------
    conditions : np.ndarray of str
        Array of trial types ('go' or 'stop') for each trial.
    stimTypes : list of str
        List of possible stimulus directions (e.g., ['left', 'right']).

    Returns
    -------
    stim_seq : np.ndarray of str
        Array of stimulus directions corresponding to each trial, aligned with the condition array.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    n_trials = len(conditions)
    stim_seq = np.empty(n_trials, dtype=object)

    stop_idx = np.where(conditions == 'stop')[0]
    go_idx = np.where(conditions == 'go')[0]

    # Ensure stimTypes are long enough to cover all trials (repeats + shuffle)
    # np.resize(['left', 'right'], 5)
    # → ['left', 'right', 'left', 'right', 'left']
    stop_stims = np.resize(stimTypes, len(stop_idx))
    go_stims = np.resize(stimTypes, len(go_idx))

    np.random.shuffle(stop_stims)
    np.random.shuffle(go_stims)

    stim_seq[stop_idx] = stop_stims
    stim_seq[go_idx] = go_stims

    return stim_seq
