
from psychopy import logging
import numpy as np

class Controller:
    """
    Manages probabilistic reversal:
      – Tracks current mapping (‘stima’ vs ‘stimb’)
      – Uses a sliding window of the last 10 hits
      – Flips rule when ≥9/10 correct and logs the flip
    """
    def __init__(self, win_prob: float, rev_win_prob: float, 
                 enable_logging: bool = True, sliding_window: int = 10,
                 sliding_window_hits: int = 9):
        self.win_prob = win_prob
        self.rev_win_prob = rev_win_prob
        self.current_correct = "stima"
        self.reversal_count = 0
        self.phase_hits: list[bool] = []
        self.sliding_window = sliding_window
        self.sliding_window_hits = sliding_window_hits
        self.enable_logging = enable_logging

    def get_win_prob(self) -> float:
        return self.win_prob if self.reversal_count == 0 else self.rev_win_prob

    def update(self, hit: bool):
        # record hit
        self.phase_hits.append(hit)
        if len(self.phase_hits) > self.sliding_window:
            self.phase_hits.pop(0)

        # check and perform reversal
        if len(self.phase_hits) == self.sliding_window and sum(self.phase_hits) >= self.sliding_window_hits:
            old = self.current_correct
            self.current_correct = "stimb" if old == "stima" else "stima"
            self.reversal_count += 1
            self.phase_hits = []

            if self.enable_logging:
                logging.data(
                    f"[Controller] Reversal #{self.reversal_count}"
                    f"[Controller] {old} → {self.current_correct}"
                )

