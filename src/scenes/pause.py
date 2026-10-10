import pygame
from src.scenes.base import BaseScene

class PauseScene(BaseScene):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_p):
            self.game.state = "PLAYING"
            self.game.audio_manager.unpause_bgm()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.game._handle_pause_click(event.pos)

    def update(self, dt):
        pass

    def draw(self, screen):
        self.game._draw_pause_menu()
