import random
import pygame


class BombSprite(pygame.sprite.Sprite):
    """Falling bomb hazard; collision effects are handled by Game."""

    def __init__(self, image: pygame.Surface, x: int, y: int, speed: float = 220.0) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos_y = float(self.rect.y)
        self.speed = speed
        self.respawned_this_update = False

    def reset(self, screen_width: int) -> None:
        """Respawns the bomb above the screen at a randomized horizontal position."""
        assert self.rect is not None
        rect_height = int(self.rect.height)
        self.pos_y = float(-random.randint(rect_height, rect_height + 250))
        max_x = max(10, screen_width - int(self.rect.width) - 10)
        self.rect.x = random.randint(10, max_x)
        self.rect.y = int(self.pos_y)
        self.speed = random.uniform(180.0, 260.0)

    def update(self, screen_width: int, screen_height: int, dt: float = 1 / 60) -> None:
        """Moves the bomb down and removes it after leaving the playable area."""
        assert self.rect is not None
        self.respawned_this_update = False
        self.pos_y += self.speed * dt
        self.rect.y = int(self.pos_y)
        if self.rect.top > screen_height:
            self.respawned_this_update = True
            self.kill()
