
from typing import Dict, List, Optional
from psychopy import logging


class Controller:
    """
    AdaptiveController dynamically adjusts stimulus duration based on participant performance,
    aiming to maintain a target accuracy rate (e.g., 66%).

    It supports both general (pooled) or condition-specific tracking,
    and is suitable for use across multiple blocks of trials.
    """

    def __init__(
        self,
        initial_duration: float = 0.25,
        min_duration: float = 0.1,
        max_duration: float = 0.4,
        step: float = 0.02,
        target_accuracy: float = 0.66,
        condition_specific: bool = True,
        enable_logging: bool = True
    ):
        self.initial_duration = initial_duration
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.step = step
        self.target_accuracy = target_accuracy
        self.condition_specific = condition_specific
        self.enable_logging = enable_logging

        self.durations: Dict[Optional[str], float] = {}
        self.histories: Dict[Optional[str], List[bool]] = {}

    @classmethod
    def from_dict(cls, config: dict) -> 'Controller':
        """
        Create an AdaptiveController instance from a flattened config dictionary.

        - Missing keys are filled with defaults.
        - Raises an error if unsupported keys are included.
        """
        allowed_keys = {
            'initial_duration': 0.25,
            'min_duration': 0.1,
            'max_duration': 0.4,
            'step': 0.02,
            'target_accuracy': 0.66,
            'condition_specific': True,
            'enable_logging': True
        }

        # Check for unsupported keys
        extra_keys = set(config.keys()) - set(allowed_keys)
        if extra_keys:
            raise ValueError(f"[AdaptiveController] Unsupported config keys: {extra_keys}")

        # Fill in config with defaults
        final_config = {k: config.get(k, default) for k, default in allowed_keys.items()}

        return cls(**final_config)

    def _get_key(self, condition: Optional[str]) -> Optional[str]:
        return condition if self.condition_specific else None

    def update(self, hit: bool, condition: Optional[str] = None):
        key = self._get_key(condition)

        if key not in self.durations:
            self.durations[key] = self.initial_duration
            self.histories[key] = []

        self.histories[key].append(bool(hit))
        acc = sum(self.histories[key]) / len(self.histories[key])

        old_duration = self.durations[key]
        if acc > self.target_accuracy:
            new_duration = max(self.min_duration, old_duration - self.step)
        else:
            new_duration = min(self.max_duration, old_duration + self.step)

        self.durations[key] = new_duration

        if self.enable_logging:
            label = f"[{condition}]" if condition else ""
            logging.data(f"[Controller📢]Adaptive{label} — Trials: {len(self.histories[key])}, "
                         f"[Controller📢]Accuracy: {acc:.2%}, Duration updated: {old_duration:.3f} → {new_duration:.3f}")

    def get_duration(self, condition: Optional[str] = None) -> float:
        key = self._get_key(condition)
        if key not in self.durations:
            self.durations[key] = self.initial_duration
            self.histories[key] = []
        return self.durations[key]


    def describe(self):
        print("Adaptive Controller Status")
        for key, history in self.histories.items():
            label = f"[{key}]" if key else "[All]"
            acc = sum(history) / len(history)
            print(f"{label} — Accuracy: {acc:.2%} ({len(history)} trials), Duration: {self.durations[key]:.3f}")
