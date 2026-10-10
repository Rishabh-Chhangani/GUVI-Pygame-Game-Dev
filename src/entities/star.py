import random
import pygame


class StarSprite(pygame.sprite.Sprite):
    """Falling star hazard/obstacle entity."""

    def __init__(self, image: pygame.Surface, x: int, y: int, speed: float = 220.0) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos_y = float(self.rect.y)
        self.speed = speed
        self.respawned_this_update = False

    def reset(self, screen_width: int = 800, difficulty: float = 1.0) -> None:
        """Disappears the star from current position and respawns it above the screen."""
        assert self.rect is not None
        rect_height = int(self.rect.height)
        self.pos_y = float(-random.randint(rect_height, rect_height + 150))
        max_x = max(10, screen_width - int(self.rect.width) - 10)
        self.rect.x = random.randint(10, max_x)
        self.rect.y = int(self.pos_y)
        self.speed = random.uniform(180.0, 260.0) * difficulty

    def update(self, screen_width: int = 800, screen_height: int = 600, dt: float = 1 / 60) -> None:
        """Moves the star downward and removes it when out of bounds."""
        assert self.rect is not None
        self.respawned_this_update = False
        self.pos_y += self.speed * dt
        self.rect.y = int(self.pos_y)

        # Wrap around / respawn if past bottom
        if self.rect.top > screen_height:
            self.respawned_this_update = True
            self.kill()
