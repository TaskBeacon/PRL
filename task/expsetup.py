from psychopy import visual
from psychopy.hardware import keyboard
from psychopy.visual import ShapeStim
from types import SimpleNamespace
from datetime import datetime
from psyflow.seedcontrol import setup_seed_for_settings

def exp_setup(
    subdata,
    left_key='q',
    right_key='p',
    win_size=(1920, 1080),
    bg_color='white',
    TotalBlocks=2,
    TotalTrials=20,
    twoArrows=False,
    useUpArrowStop=False,
    initSSD=200,
    staircase=50,
    arrowDuration=1.0,
    trialDuration=3.0,
    seed_mode='indiv',
):
    """
    Initializes the PsychoPy window, stimuli, experimental settings, and keyboard input handler.

    Parameters
    ----------
    subdata : list
        Subject information, with the first element typically being the subject ID.
    left_key : str, optional
        Response key for left-arrow trials. Ignored if `twoArrows` is False (default: 'q').
    right_key : str, optional
        Response key for right-arrow trials (default: 'p').
    win_size : tuple of int, optional
        Size of the experiment window in pixels (default: (1920, 1080)).
    bg_color : str or tuple, optional
        Background color of the window (default: 'white').
    TotalBlocks : int, optional
        Number of blocks in the experiment (default: 2).
    TotalTrials : int, optional
        Total number of trials in the experiment (default: 20).
    twoArrows : bool, optional
        Whether to include both 'left' and 'right' arrow stimuli (default: False).
    useUpArrowStop : bool, optional
        Whether to use ↑ as the stop signal (default: False).
    initSSD : int, optional
        Initial stop-signal delay in milliseconds (default: 200).
    staircase : int, optional
        Step size for adjusting SSD (default: 50).
    arrowDuration : float, optional
        Duration of arrow presentation in seconds (default: 1.0).
    trialDuration : float, optional
        Maximum duration of a trial in seconds (default: 3.0).
    seed_mode : str, optional
            One of 'random', 'same', or 'indiv'.

    Returns
    -------
    win : visual.Window
        The PsychoPy window object used for stimulus presentation.
    kb : keyboard.Keyboard
        PsychoPy keyboard object for collecting keypresses.
    settings : SimpleNamespace
        Object containing all experimental parameters and stimulus objects.
    """
    win = visual.Window(
        size=win_size,
        monitor="testMonitor",
        units="deg",
        screen=1,
        color=bg_color,
        fullscr=True,
        gammaErrorPolicy='ignore'
    )

    # Define settings
    settings = SimpleNamespace()
    settings.TotalBlocks = TotalBlocks
    settings.TotalTrials = TotalTrials
    settings.TrialsPerBlock = TotalTrials // TotalBlocks

    # Seed setup
    settings = setup_seed_for_settings(settings, subdata, mode=seed_mode)

    # Arrow vertices
    LarrowVert = [(0.2, 0.05), (0.2, -0.05), (0, -0.05), (0, -0.1), (-.2, 0), (0, 0.1), (0, 0.05)]
    RarrowVert = [(-0.2, 0.05), (-0.2, -0.05), (0, -0.05), (0, -0.1), (.2, 0), (0, 0.1), (0, 0.05)]
    UparrowVert = [(-0.05, -0.2), (0.05, -0.2), (0.05, 0), (0.1, 0), (0, 0.2), (-0.1, 0), (-0.05, 0)]

    # Stimuli
    settings.Larrow = ShapeStim(win, vertices=LarrowVert, fillColor='black', size=8, lineColor=None)
    settings.Rarrow = ShapeStim(win, vertices=RarrowVert, fillColor='black', size=8, lineColor=None)
    settings.LarrowSTOP = ShapeStim(win, vertices=LarrowVert, fillColor='red', size=8, lineColor=None)
    settings.RarrowSTOP = ShapeStim(win, vertices=RarrowVert, fillColor='red', size=8, lineColor=None)
    settings.UparrowSTOP = ShapeStim(win, vertices=UparrowVert, fillColor='black', size=8, lineColor=None)

    # Arrow types
    settings.twoArrows = twoArrows
    settings.useUpArrowStop = useUpArrowStop
    settings.arrowTypes = ['left', 'right'] if twoArrows else ['right']

    # Key settings
    settings.left_key = left_key
    settings.right_key = right_key
    settings.keyList = [left_key, right_key] if twoArrows else [right_key]

    # Timing and staircase settings
    settings.initSSD = initSSD
    settings.staircase = staircase
    settings.arrowDuration = arrowDuration
    settings.trialDuration = trialDuration

    # Output file naming
    dt_string = datetime.now().strftime("%H%M%d%m")
    settings.outfile = f"Subject{subdata[0]}_{dt_string}.csv"

    # Keyboard
    kb = keyboard.Keyboard()

    return win, kb, settings
