import pygame
from src.scenes.base import BaseScene
from src import config

class MenuScene(BaseScene):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.game._start_game_play()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.game._handle_menu_click(event.pos)

    def update(self, dt):
        pass

    def draw(self, screen):
        self.game._draw_main_menu()
