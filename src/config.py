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
PLAYER_SPEED = 360  # pixels per second
PLAYER_BOTTOM_OFFSET = 70  # Pixels from the bottom of the screen
PLAYER_ANIMATION_DELAY = 0.1  # seconds
PLAYER_INVULNERABILITY_DURATION = 1.2  # seconds
PLAYER_COMBO_WINDOW = 2.5  # seconds before combo resets
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
COIN_ANIMATION_DELAY = 0.125  # seconds for smooth natural rotation
COIN_COUNT = 2  # Number of concurrent falling coins

# Bomb Settings
BOMB_IMAGE_FILE = "bomb.png"
BOMB_SIZE = (32, 32)
BOMB_DAMAGE = 25
STAR_DAMAGE = 25
COINS_PER_BOMB = 7

# Star Settings
STAR_IMAGE_FILE = "star1.png"
STAR_SIZE = (32, 32)
STAR_VALUE = 10
COINS_PER_STAR = 10
COIN_VALUE = 1

# Player Health
PLAYER_MAX_HEALTH = 100

# HUD Settings
SCORE_FONT_SIZE = 28
GAME_OVER_FONT_SIZE = 64
FONT_FILE: str | None = None
HUD_COLOR = (255, 255, 255)
GAME_OVER_COLOR = (255, 70, 70)
SCORE_POSITION = (20, 20)
HEALTH_POSITION = (20, 60)
HEALTH_BAR_POSITION = (20, 94)
HEALTH_BAR_SIZE = (200, 16)
HEALTH_BAR_BACKGROUND_COLOR = (75, 35, 35)
HEALTH_BAR_COLOR = (70, 190, 95)

# Main Menu Settings
MENU_BACKGROUND_COLOR = (18, 30, 25)
MENU_TITLE_COLOR = (233, 236, 229)
MENU_BUTTON_COLOR = (36, 72, 60)
MENU_BUTTON_HOVER_COLOR = (58, 110, 90)
MENU_BUTTON_TEXT_COLOR = (245, 245, 245)
MENU_TITLE_FONT_SIZE = 62
MENU_BUTTON_FONT_SIZE = 28
MENU_BUTTON_WIDTH = 180
MENU_BUTTON_HEIGHT = 52
MENU_BUTTON_SPACING = 26
