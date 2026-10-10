from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from src.game import Game


class BaseScene:
    def __init__(self, game: Game) -> None:
        self.game = game

    def handle_event(self, event: pygame.event.Event) -> None:
        del event

    def update(self, dt: float) -> None:
        del dt

    def draw(self, screen: pygame.Surface) -> None:
        del screen
