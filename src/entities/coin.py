import random
import pygame
from src.config import COIN_ANIMATION_DELAY


class CoinSprite(pygame.sprite.Sprite):
    """Animated collectible coin that falls from top of screen."""

    def __init__(
        self,
        frames: list[pygame.Surface],
        x: int,
        y: int,
        speed: float = 3.0,
        animation_delay: int = COIN_ANIMATION_DELAY,
    ) -> None:
        super().__init__()
        self.frames = frames
        self.current_frame = random.randint(0, len(frames) - 1)
        self.animation_delay = animation_delay
        self.last_update = pygame.time.get_ticks()

        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos_y = float(self.rect.y)
        self.speed = speed
        self.missed_this_update = False

    def reset(self, screen_width: int = 800) -> None:
        """Resets the coin above the screen at a randomized horizontal position and speed."""
        assert self.rect is not None
        rect_height = int(self.rect.height)
        self.pos_y = float(-random.randint(rect_height, rect_height + 250))
        max_x = max(10, screen_width - int(self.rect.width) - 10)
        self.rect.x = random.randint(10, max_x)
        self.rect.y = int(self.pos_y)
        self.speed = random.uniform(2.5, 4.5)

    def update(self, screen_width: int = 800, screen_height: int = 600) -> None:
        """Updates downward falling kinematics and frame animation."""
        assert self.rect is not None
        self.missed_this_update = False
        # Kinematics
        self.pos_y += self.speed
        self.rect.y = int(self.pos_y)

        # Animation
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.last_update = now

        # Screen loop
        if self.rect.top > screen_height:
            self.reset(screen_width)
            self.missed_this_update = True
