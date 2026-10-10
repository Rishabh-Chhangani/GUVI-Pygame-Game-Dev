import pygame

from src.scenes.base import BaseScene


class GameOverScene(BaseScene):
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.game.restart_playing_session()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.game.handle_game_over_click(event.pos)

    def update(self, dt: float) -> None:
        del dt

    def draw(self, screen: pygame.Surface) -> None:
        del screen
        self.game.draw_game_over()
