import pygame
from src.config import PLAYER_SPEED, PLAYER_ANIMATION_DELAY, PLAYER_SIZE, PLAYER_BOTTOM_OFFSET


class Player(pygame.sprite.Sprite):
    """Player Ninja entity with animation, horizontal input controls, and bottom screen anchoring."""

    def __init__(
        self,
        frames : list[pygame.Surface],
        x : int,
        y : int = 0,
        size : tuple[int, int] = PLAYER_SIZE,
        speed : int = PLAYER_SPEED,
        bottom_offset : int = PLAYER_BOTTOM_OFFSET,
        animation_delay : int = PLAYER_ANIMATION_DELAY
    ):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.animation_delay = animation_delay
        self.last_update = pygame.time.get_ticks()

        self.speed = speed
        self.bottom_offset = bottom_offset
        self.facing_right = True

        self.image = self.frames[self.current_frame]
        self.rect = pygame.Rect(x, y, size[0], size[1])

    def handle_input(self, screen_width : int, screen_height : int):
        """Processes keyboard input for horizontal movement and locks vertical position."""
        assert self.rect is not None
        keys = pygame.key.get_pressed()

        # Horizontal movement only (Arrow keys & A/D)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True

        # Horizontal boundary constraints
        assert self.rect is not None
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

        # Fixed vertical axis (anchored 20px from bottom)
        self.rect.bottom = screen_height - self.bottom_offset

    def update(self, screen_width : int = 800, screen_height : int = 600):
        """Updates player horizontal position, animation frame, and orientation."""
        self.handle_input(screen_width, screen_height)

        # Update animation frame
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now

        current_img = self.frames[self.current_frame]
        if not self.facing_right:
            self.image = pygame.transform.flip(current_img, True, False)
        else:
            self.image = current_img

    def draw(self, surface  : pygame.Surface) -> None:
        """Draws player to the target surface."""
        assert self.rect is not None
        assert self.image is not None
        surface.blit(self.image, self.rect)

