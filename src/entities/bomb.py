import pygame


class BombSprite(pygame.sprite.Sprite):
    """Static bomb image sprite; hazard behavior is not implemented."""

    def __init__(self, image: pygame.Surface, x: int, y: int) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
