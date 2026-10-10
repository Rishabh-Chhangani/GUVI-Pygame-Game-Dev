import pygame

from src.scenes.base import BaseScene


class LeaderboardScene(BaseScene):
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.game.handle_leaderboard_click(event.pos)

    def update(self, dt: float) -> None:
        del dt

    def draw(self, screen: pygame.Surface) -> None:
        del screen
        self.game.draw_leaderboard_menu()
