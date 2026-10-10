import pygame

from src.scenes.base import BaseScene


class OptionsScene(BaseScene):
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.state = "PAUSED"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.game.handle_options_click(event.pos)
            
        # Slider events
        if self.game.bgm_slider.handle_event(event):
            self.game.audio_manager.bgm_volume = self.game.bgm_slider.value
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(self.game.audio_manager.bgm_volume)
        if self.game.sfx_slider.handle_event(event):
            self.game.audio_manager.sfx_volume = self.game.sfx_slider.value

    def update(self, dt: float) -> None:
        del dt

    def draw(self, screen: pygame.Surface) -> None:
        del screen
        self.game.draw_options_menu()
