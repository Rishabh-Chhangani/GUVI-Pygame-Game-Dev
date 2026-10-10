import pygame


class MagnetSprite(pygame.sprite.Sprite):
    """Falling magnet power-up."""

    def __init__(self, image: pygame.Surface, x: int, y: int, speed: float = 220.0) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos_y = float(self.rect.y)
        self.speed = speed
        self.respawned_this_update = False

    def update(self, screen_width: int, screen_height: int, dt: float = 1 / 60, difficulty: float = 1.0) -> None:
        """Moves the magnet down and removes it after leaving the playable area."""
        assert self.rect is not None
        del screen_width
        self.respawned_this_update = False
        self.pos_y += self.speed * difficulty * dt
        self.rect.y = int(self.pos_y)
        if self.rect.top > screen_height:
            self.respawned_this_update = True
            self.kill()
