from psychopy import logging

class Controller:
    """
    Manages probabilistic reversal learning:
      – Tracks current mapping ('stima' vs 'stimb')
      – Uses a sliding window of recent hits to decide when to flip
      – Logs each reversal when enable_logging=True
    """

    def __init__(
        self,
        win_prob: float,
        rev_win_prob: float,
        enable_logging: bool = True,
        sliding_window: int = 10,
        sliding_window_hits: int = 9,
    ):
        self.win_prob = win_prob
        self.rev_win_prob = rev_win_prob
        self.current_correct = "stima"
        self.reversal_count = 0
        self.phase_hits: list[bool] = []
        self.sliding_window = sliding_window
        self.sliding_window_hits = sliding_window_hits
        self.enable_logging = enable_logging

    @classmethod
    def from_dict(cls, config: dict) -> "Controller":
        """
        Create a Controller from a flat config dict.

        Required:
          - win_prob

        Optional:
          - rev_win_prob         (defaults to win_prob)
          - enable_logging       (default True)
          - sliding_window       (default 10)
          - sliding_window_hits  (default 9)
        """
        allowed = {
            "win_prob",
            "rev_win_prob",
            "enable_logging",
            "sliding_window",
            "sliding_window_hits",
        }
        extra = set(config) - allowed
        if extra:
            raise ValueError(f"[Controller.from_dict] Unknown config keys: {extra}")

        if "win_prob" not in config:
            raise ValueError("[Controller.from_dict] Missing required key: 'win_prob'")

        win_prob = config["win_prob"]
        rev_win_prob = config.get("rev_win_prob", win_prob)

        return cls(
            win_prob=win_prob,
            rev_win_prob=rev_win_prob,
            enable_logging=config.get("enable_logging", True),
            sliding_window=config.get("sliding_window", 10),
            sliding_window_hits=config.get("sliding_window_hits", 9),
        )

    def get_win_prob(self) -> float:
        """Return the current probability of winning."""
        return self.win_prob if self.reversal_count == 0 else self.rev_win_prob

    def update(self, hit: bool):
        """
        Record a hit (True/False), check sliding window,
        and flip the rule if threshold is reached.
        """
        self.phase_hits.append(hit)
        if len(self.phase_hits) > self.sliding_window:
            self.phase_hits.pop(0)

        if (
            len(self.phase_hits) == self.sliding_window
            and sum(self.phase_hits) >= self.sliding_window_hits
        ):
            old = self.current_correct
            self.current_correct = "stimb" if old == "stima" else "stima"
            self.reversal_count += 1
            self.phase_hits.clear()
            if self.enable_logging:
                logging.data(
                    f"[Controller] Reversal #{self.reversal_count}: "
                    f"{old} → {self.current_correct}"
                )


import os
from PIL import Image, ImageDraw, ImageFont
# Stroke count to Unicode range mapping (inclusive)
stroke_to_unicode_range = {
    1:  (0x1B170, 0x1B170),
    2:  (0x1B171, 0x1B177),
    3:  (0x1B178, 0x1B18A),
    4:  (0x1B18B, 0x1B1A7),
    5:  (0x1B1A8, 0x1B1D5),
    6:  (0x1B1DE, 0x1B215),
    7:  (0x1B216, 0x1B243),
    8:  (0x1B244, 0x1B283),
    9:  (0x1B284, 0x1B2AF),
    10: (0x1B2B0, 0x1B2D5),
    11: (0x1B2CE, 0x1B2E0),
    12: (0x1B2E1, 0x1B2ED),
    13: (0x1B2EE, 0x1B2F3),
    14: (0x1B2F4, 0x1B2F6),
    15: (0x1B2F7, 0x1B2F9),
}

def generate_nushu_symbols(
font_path,
output_dir,
stroke,
stroke_range_dict,
bg_color="gray",
fill_color="white",
img_size=100,
font_size=72
):
    """
    Generate Nüshu symbol images for a specific stroke count.

    Args:
        font_path (str): Path to the NotoSansNushu-Regular.ttf file.
        output_dir (str): Directory to save the generated images.
        stroke (int): Stroke count (1–15).
        stroke_range_dict (dict): Dict mapping stroke count → (start, end) Unicode range.
        bg_color (str or tuple): Background color (e.g., "white" or (255,255,255)).
        img_size (int): Width and height of the image in pixels.
        font_size (int): Size of the character font.
    """
    if stroke not in stroke_range_dict:
        raise ValueError(f"Stroke count {stroke} not valid. Choose from: {list(stroke_range_dict.keys())}")

    os.makedirs(output_dir, exist_ok=True)
    font = ImageFont.truetype(font_path, font_size)
    
    start, end = stroke_range_dict[stroke]
    for i, code in enumerate(range(start, end + 1)):
        char = chr(code)
        img = Image.new("RGB", (img_size, img_size), bg_color)
        draw = ImageDraw.Draw(img)

        # Center character on image
        # Center character on image using textbbox
        bbox = draw.textbbox((0, 0), char, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (img_size - w) // 2
        y = (img_size - h) // 2
        draw.text((x, y), char, font=font, fill=fill_color)

        filename = f"nushu_stroke{stroke}_{i:03d}_U{code:04X}.png"
        img.save(os.path.join(output_dir, filename))

# generate_nushu_symbols(
#     font_path="E:/xhmhc/TaskBeacon/PRL/assets/NotoSansNushu-Regular.ttf",
#     output_dir="E:/xhmhc/TaskBeacon/PRL/assets",
#     stroke=5,
#     stroke_range_dict=stroke_to_unicode_range,
#     bg_color="gray",
#     img_size=512,
#     font_size=300
# )