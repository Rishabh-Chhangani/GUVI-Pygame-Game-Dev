import random
import pygame


class StarSprite(pygame.sprite.Sprite):
    """Falling star hazard/obstacle entity."""

    def __init__(self, image: pygame.Surface, x: int, y: int, speed: float = 2.5) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos_y = float(self.rect.y)
        self.speed = speed

    def reset(self, screen_width: int = 800) -> None:
        """Disappears the star from current position and respawns it above the screen."""
        assert self.rect is not None
        rect_height = int(self.rect.height)
        self.pos_y = float(-random.randint(rect_height, rect_height + 150))
        max_x = max(10, screen_width - int(self.rect.width) - 10)
        self.rect.x = random.randint(10, max_x)
        self.rect.y = int(self.pos_y)

    def update(self, screen_width: int = 800, screen_height: int = 600) -> None:
        """Moves the star downward and resets when out of bounds."""
        assert self.rect is not None
        self.pos_y += self.speed
        self.rect.y = int(self.pos_y)

        # Wrap around / respawn if past bottom
        if self.rect.top > screen_height:
            self.reset(screen_width)
