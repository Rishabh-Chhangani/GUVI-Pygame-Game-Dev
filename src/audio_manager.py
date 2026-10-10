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
            self.sfx['coin'] = pygame.mixer.Sound(str(self.assets_dir / "audio" / "coin_pickup.wav"))
            self.sfx['hit'] = pygame.mixer.Sound(str(self.assets_dir / "audio" / "ninja_hit.wav"))
            self.sfx['game_over'] = pygame.mixer.Sound(str(self.assets_dir / "audio" / "game_over.wav"))
            self.sfx['click'] = pygame.mixer.Sound(str(self.assets_dir / "audio" / "click.wav"))
        except (FileNotFoundError, pygame.error) as e:
            print(f"[Audio] Missing sound files. SFX will be silent. ({e})")

        self.bgm_path = self.assets_dir / "audio" / "bgm.wav"

        self.bgm_volume = 0.5
        self.sfx_volume = 1.0

    def play_sfx(self, name: str):
        if self.is_muted:
            return

        sound = self.sfx.get(name)
        if isinstance(sound, pygame.mixer.Sound):
            sound.set_volume(self.sfx_volume)
            sound.play()
            
    def play_bgm(self):
        if self.is_muted: return
        if self.bgm_path.exists():
            try:
                pygame.mixer.music.load(str(self.bgm_path))
                pygame.mixer.music.set_volume(self.bgm_volume)
                pygame.mixer.music.play(-1) # Loop infinitely
            except pygame.error:
                print("[Audio] BGM load failed.")
                
    def stop_bgm(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def pause_bgm(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.pause()

    def unpause_bgm(self):
        if not self.is_muted and pygame.mixer.get_init():
            pygame.mixer.music.unpause()

    def cycle_bgm_volume(self):
        """Cycles BGM volume through 1.0, 0.75, 0.5, 0.25, 0.0"""
        self.bgm_volume -= 0.25
        if self.bgm_volume < 0.0:
            self.bgm_volume = 1.0
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.bgm_volume)

    def cycle_sfx_volume(self):
        """Cycles SFX volume through 1.0, 0.75, 0.5, 0.25, 0.0"""
        self.sfx_volume -= 0.25
        if self.sfx_volume < 0.0:
            self.sfx_volume = 1.0

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.stop_bgm()
        else:
            self.play_bgm()
