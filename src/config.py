import os
from pathlib import Path

# Paths
SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent
ASSETS_DIR = ROOT_DIR / "assets"

# Window & Display
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
FPS = 60
CAPTION = "Ninja Collector"
ICON_FILE = "coin1.png"
BG_IMAGE_FILE = "bg1.png"

# Player Settings
PLAYER_SIZE = (64, 64)
PLAYER_SPEED = 6
PLAYER_BOTTOM_OFFSET = 40  # Pixels from the bottom of the screen
PLAYER_ANIMATION_DELAY = 100  # milliseconds
PLAYER_FRAME_NAMES = [
    "Ninja1.jpg",
    "Ninja2.jpg",
    "Ninja3.jpg",
    "Ninja4.jpg",
    "Ninja5.jpg"
]

# Coin Settings
COIN_SIZE = (50, 50)
COIN_FRAME_NAMES = [f"coin{i}.png" for i in range(1, 8)]
COIN_ANIMATION_DELAY = 125  # milliseconds for smooth natural rotation
COIN_COUNT = 4  # Number of concurrent falling coins
