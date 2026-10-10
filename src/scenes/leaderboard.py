import pygame
from src.scenes.base import BaseScene

class LeaderboardScene(BaseScene):
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.game._handle_leaderboard_click(event.pos)

    def update(self, dt):
        pass

    def draw(self, surface):
        self.game._draw_leaderboard_menu()
