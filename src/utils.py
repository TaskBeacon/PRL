
from psychopy import logging
import numpy as np

class Controller:
    """
    Manages probabilistic reversal:
      – Tracks current mapping (‘stima’ vs ‘stimb’)
      – Uses a sliding window of the last 10 hits
      – Flips rule when ≥9/10 correct and logs the flip
    """
    def __init__(self, win_prob: float, rev_win_prob: float, enable_logging: bool = True):
        self.win_prob = win_prob
        self.rev_win_prob = rev_win_prob
        self.current_correct = "stima"
        self.reversal_count = 0
        self.phase_hits: list[bool] = []
        self.enable_logging = enable_logging

    def get_win_prob(self) -> float:
        return self.win_prob if self.reversal_count == 0 else self.rev_win_prob

    def update(self, hit: bool):
        # record hit
        self.phase_hits.append(hit)
        if len(self.phase_hits) > 10:
            self.phase_hits.pop(0)

        # check and perform reversal
        if len(self.phase_hits) == 10 and sum(self.phase_hits) >= 9:
            old = self.current_correct
            self.current_correct = "stimb" if old == "stima" else "stima"
            self.reversal_count += 1
            self.phase_hits = []

            if self.enable_logging:
                logging.data(
                    f"[PRLController] Reversal #{self.reversal_count}: "
                    f"{old} → {self.current_correct}"
                )