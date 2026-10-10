import pygame

from src.scenes.base import BaseScene


class SceneManager:
    def __init__(self, initial_scene: BaseScene) -> None:
        self.scene = initial_scene

    def switch_to(self, new_scene: BaseScene) -> None:
        self.scene = new_scene

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.scene:
            self.scene.handle_event(event)

    def update(self, dt: float) -> None:
        if self.scene:
            self.scene.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        if self.scene:
            self.scene.draw(screen)
