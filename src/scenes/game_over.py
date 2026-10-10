import pygame
from src.scenes.base import BaseScene

class GameOverScene(BaseScene):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.game._restart_playing_session()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.game._handle_game_over_click(event.pos)

    def update(self, dt):
        pass

    def draw(self, screen):
        self.game._draw_game_over()
