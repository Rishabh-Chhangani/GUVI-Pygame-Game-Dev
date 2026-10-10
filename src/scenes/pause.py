import pygame

from src.scenes.base import BaseScene


class PauseScene(BaseScene):
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_p):
            self.game.state = "PLAYING"
            self.game.audio_manager.unpause_bgm()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.game.handle_pause_click(event.pos)

    def update(self, dt: float) -> None:
        del dt

    def draw(self, screen: pygame.Surface) -> None:
        del screen
        self.game.draw_pause_menu()
