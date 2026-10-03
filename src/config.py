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
PLAYER_SIZE = (79, 82)  # display widhth and height in pixels
PLAYER_SPEED = 6
PLAYER_BOTTOM_OFFSET = 70  # Pixels from the bottom of the screen
PLAYER_ANIMATION_DELAY = 100  # milliseconds
PLAYER_FRAME_NAMES = [
    "idle_anim/idle1.png",
    "idle_anim/idle2.png",
    "idle_anim/idle3.png",
    "idle_anim/idle4.png",
    "idle_anim/idle5.png"
]
PLAYER_RUN_FRAME_NAMES = [
    f"Runing/Run{i}.png" for i in range(1, 7)
]
PLAYER_CATCH_FRAME_NAMES = [
    f"Catch/Catch{i}.png" for i in range(1, 4)
]

# Coin Settings
COIN_SIZE = (32,32) # display width and height in pixels 
COIN_FRAME_NAMES = [f"coin{i}.png" for i in range(1, 8)]
COIN_ANIMATION_DELAY = 125  # milliseconds for smooth natural rotation
COIN_COUNT = 4  # Number of concurrent falling coins
MAX_MISSED_COINS = 5

# HUD Settings
SCORE_FONT_SIZE = 28
GAME_OVER_FONT_SIZE = 64
HUD_COLOR = (255, 255, 255)
GAME_OVER_COLOR = (255, 70, 70)
SCORE_POSITION = (20, 20)
