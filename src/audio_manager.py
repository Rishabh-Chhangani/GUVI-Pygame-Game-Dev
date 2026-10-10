import pygame
from pathlib import Path
from typing import Any


class AudioManager:
    """Handles sound effects and background music playback."""

    def __init__(self, assets_dir: str | Path):
        self.assets_dir = Path(assets_dir)
        self.is_muted = False

        # Initialize mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init(buffer=512)

        self.sfx: dict[str, Any] = {}
        self._load_sounds()

    def _load_sounds(self):
        # We wrap in try/except so the game doesn't crash if files are missing
        try:
            self.sfx['coin'] = pygame.mixer.Sound(str(self.assets_dir / "coin_pickup.wav"))
            self.sfx['hit'] = pygame.mixer.Sound(str(self.assets_dir / "ninja_hit.wav"))
            self.sfx['game_over'] = pygame.mixer.Sound(str(self.assets_dir / "game_over.wav"))
        except (FileNotFoundError, pygame.error) as e:
            print(f"[Audio] Missing sound files. SFX will be silent. ({e})")

        # Optional BGM
        self.bgm_path = self.assets_dir / "bgm.ogg"

    def play_sfx(self, name: str):
        if self.is_muted:
            return

        sound = self.sfx.get(name)
        if isinstance(sound, pygame.mixer.Sound):
            sound.play()
            
    def play_bgm(self):
        if self.is_muted: return
        if self.bgm_path.exists():
            try:
                pygame.mixer.music.load(str(self.bgm_path))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1) # Loop infinitely
            except pygame.error:
                print("[Audio] BGM load failed.")
                
    def stop_bgm(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.stop_bgm()
        else:
            self.play_bgm()
