import pygame
from src.scenes.base import BaseScene

class PlayScene(BaseScene):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_p):
            self.game.state = "PAUSED"
            self.game.audio_manager.pause_bgm()

    def update(self, dt):
        self.game._update_playing(dt)

    def draw(self, screen):
        self.game._draw_playing()
