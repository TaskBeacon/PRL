import os, glob
from psychopy import visual
from psychopy.hardware import keyboard
from datetime import datetime
from types import SimpleNamespace
from psyflow.seedcontrol import setup_seed_for_settings

def exp_setup(
    subdata,
    left_key='q',
    right_key='p',
    win_size=(1920, 1080),
    bg_color='gray',
    TotalBlocks=2,
    TotalTrials=20,
    img_path="E:/xhmhc/TaskBeacon/PRL/img",
    fixDuration=0.5,
    ITI=0.5,
    cueDuration=1.5,
    fbDuration=0.95,
    seed_mode='same'
):
    """
    Initializes the PsychoPy window, experimental settings, and keyboard input handler 
    for the Probabilistic Reversal Learning (PRL) task.
    
    For this PRL task, two stimulus images (stima, stimb) are assigned uniquely per block,
    and timing parameters for fixation, cue (stimulus presentation), inter-trial interval (ITI), 
    and feedback are defined.
    
    Parameters
    ----------
    subdata : list
        Subject information, where the first element is typically the subject ID.
    left_key : str, optional
        Response key for the left stimulus (default: 'q').
    right_key : str, optional
        Response key for the right stimulus (default: 'p').
    win_size : tuple of int, optional
        Size of the experiment window in pixels (default: (1920, 1080)).
    bg_color : str or tuple, optional
        Background color of the window (default: 'white').
    TotalBlocks : int, optional
        Number of blocks in the experiment (default: 2).
    TotalTrials : int, optional
        Total number of trials in the experiment (default: 20).
    img_path : str, optional
        Directory where the PRL stimulus images (PNG files) are located.
    fixDuration : float, optional
        Duration of the fixation period in seconds (default: 0.5).
    ITI : float, optional
        Inter-trial interval duration in seconds (default: 0.5).
    cueDuration : float, optional
        Duration of the stimulus cue presentation in seconds (default: 1.5).
    fbDuration : float, optional
        Duration of the feedback display in seconds (default: 0.95).
    seed_mode : str, optional
        Determines the seed mode ('random', 'same', or 'indiv') for reproducibility.
    
    Returns
    -------
    win : visual.Window
        The PsychoPy window object.
    kb : keyboard.Keyboard
        The PsychoPy keyboard object for response collection.
    settings : SimpleNamespace
        An object containing all experimental parameters and stimulus properties.
    """
    # Create the window
    win = visual.Window(
        size=win_size,
        monitor="testMonitor",
        units="norm",
        screen=1,
        color=bg_color,
        fullscr=True,
        gammaErrorPolicy='ignore'
    )

    # Create the settings namespace
    settings = SimpleNamespace()
    settings.TotalBlocks = TotalBlocks
    settings.TotalTrials = TotalTrials
    settings.TrialsPerBlock = TotalTrials // TotalBlocks

    # Seed setup for reproducibility
    settings = setup_seed_for_settings(settings, subdata, mode=seed_mode)

    # Save timing parameters (all times in seconds)
    settings.fixDuration = fixDuration
    settings.ITI = ITI
    settings.cueDuration = cueDuration
    settings.fbDuration = fbDuration

    # Save image stimulus path
    settings.img_path = img_path

    # Key settings for responses
    settings.left_key = left_key
    settings.right_key = right_key
    settings.keyList = [left_key, right_key]
    settings.current_correct = 'stima'
    settings.win_prob = 0.8
    settings.rev_win_prob = 0.8

    # Output file naming based on subject ID and current datetime
    dt_string = datetime.now().strftime("%H%M%d%m")
    settings.outfile = f"Subject{subdata[0]}_{dt_string}.csv"

    # -----------------------------
    # Build image pairs for each block
    # -----------------------------
    # List all PNG files in the specified img_path directory (sorted order)
    img_files = sorted(glob.glob(os.path.join(settings.img_path, "*.png")))
    required_files = TotalBlocks * 2  # Each block uses one pair (2 images)
    if len(img_files) < required_files:
        raise ValueError(f"Not enough image files to form pairs for each block. "
                         f"Required: {required_files}, found: {len(img_files)}.")
    
    settings.imagePairs = {}
    for block in range(1, TotalBlocks + 1):
        stima_file = img_files[2 * (block - 1)]
        stimb_file = img_files[2 * (block - 1) + 1]
        settings.imagePairs[block] = {"stima": stima_file, "stimb": stimb_file}
    # Initialize the keyboard
    kb = keyboard.Keyboard()

    return win, kb, settings
