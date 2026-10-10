import pygame
from src.config import (
    PLAYER_SPEED,
    PLAYER_ANIMATION_DELAY,
    PLAYER_SIZE,
    PLAYER_BOTTOM_OFFSET,
    PLAYER_MAX_HEALTH,
    PLAYER_INVULNERABILITY_DURATION,
    PLAYER_COMBO_WINDOW,
)


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
        animation_delay : float = PLAYER_ANIMATION_DELAY,
        running_frames: list[pygame.Surface] | None = None,
        catch_frames: list[pygame.Surface] | None = None,
        max_health: int = PLAYER_MAX_HEALTH,
    ):
        super().__init__()
        self.frames = frames
        self.running_frames = running_frames if running_frames is not None else frames
        self.catch_frames = catch_frames if catch_frames is not None else []
        self.current_animation = self.frames
        self.current_frame = 0
        self.animation_delay = animation_delay
        self.animation_timer = 0.0

        self.speed = speed
        self.bottom_offset = bottom_offset
        self.facing_right = True
        self.is_moving = False
        self.is_catching = False
        self.max_health = max_health
        self.health = max_health
        self.invulnerability_timer = 0.0
        self.invulnerability_duration = PLAYER_INVULNERABILITY_DURATION
        self.combo = 0
        self.combo_timer = 0.0
        self.combo_window = PLAYER_COMBO_WINDOW

        self.image = self.frames[self.current_frame]
        self.rect = pygame.Rect(x, y, size[0], size[1])
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

    def update_combo(self, dt: float) -> None:
        """Counts and expires coin-chain multipliers for polished gameplay."""
        if self.combo > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0
                self.combo_timer = 0.0

    def get_combo_multiplier(self) -> int:
        """Returns the current score multiplier, starting at 1x."""
        return max(1, self.combo)

    def record_coin_pickup(self, dt: float) -> None:
        """Increase combo chain after collecting a coin and reset the timer."""
        self.combo += 1
        self.combo_timer = self.combo_window
        self.update_combo(dt)

    def take_damage(self, amount: int) -> bool:
        """Reduces health without allowing it to fall below zero. Returns True if damage was applied."""
        if self.invulnerability_timer > 0:
            return False

        self.health = max(0, self.health - amount)
        self.invulnerability_timer = self.invulnerability_duration
        self.combo = 0
        self.combo_timer = 0.0
        return True

    def start_catch(self) -> None:
        """Starts the one-shot catch animation when frames are available."""
        if not self.catch_frames:
            return

        self.is_catching = True
        self.current_frame = 0
        self.animation_timer = 0.0
        current_img = self.catch_frames[self.current_frame]
        self.image = pygame.transform.flip(current_img, True, False) if not self.facing_right else current_img.copy()

    def handle_input(self, screen_width : int, screen_height : int, dt: float = 1 / 60):
        """Processes keyboard input for horizontal movement and locks vertical position."""
        assert self.rect is not None
        start_x = self.rect.x
        keys = pygame.key.get_pressed()

        move_direction = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_direction -= 1.0
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_direction += 1.0
            self.facing_right = True

        if move_direction != 0.0:
            self.pos_x += self.speed * move_direction * dt
            self.pos_x = max(0.0, min(self.pos_x, float(screen_width - self.rect.width)))

        self.rect.x = int(round(self.pos_x))

        if self.rect.left < 0:
            self.rect.left = 0
            self.pos_x = float(self.rect.x)
        if self.rect.right > screen_width:
            self.rect.right = screen_width
            self.pos_x = float(self.rect.x)

        self.is_moving = self.rect.x != start_x

        # Fixed vertical axis (anchored 20px from bottom)
        self.rect.bottom = screen_height - self.bottom_offset

    def update(self, screen_width : int = 800, screen_height : int = 600, dt: float = 1 / 60):
        """Updates player horizontal position, animation frame, and orientation."""
        self.handle_input(screen_width, screen_height, dt)
        self.update_combo(dt)

        if self.invulnerability_timer > 0:
            self.invulnerability_timer = max(0.0, self.invulnerability_timer - dt)

        self.animation_timer += dt
        catch_delay = self.animation_delay
        if self.is_catching:
            if self.animation_timer >= catch_delay:
                self.current_frame += 1
                self.animation_timer = 0.0
                if self.current_frame >= len(self.catch_frames):
                    self.is_catching = False
                    self.current_frame = 0

            if self.is_catching:
                current_img = self.catch_frames[self.current_frame]
                if not self.facing_right:
                    self.image = pygame.transform.flip(current_img, True, False)
                else:
                    self.image = current_img.copy()
                if self.invulnerability_timer > 0:
                    self.image.set_alpha(120)
                else:
                    self.image.set_alpha(255)
                return

        animation = self.running_frames if self.is_moving else self.frames
        if animation is not self.current_animation:
            self.current_animation = animation
            self.current_frame = 0
            self.animation_timer = 0.0

        if self.animation_timer >= catch_delay:
            self.current_frame = (self.current_frame + 1) % len(self.current_animation)
            self.animation_timer = 0.0

        current_img = self.current_animation[self.current_frame]
        if not self.facing_right:
            self.image = pygame.transform.flip(current_img, True, False)
        else:
            self.image = current_img.copy()

        if self.invulnerability_timer > 0:
            self.image.set_alpha(120 if int(self.invulnerability_timer * 12) % 2 else 200)
        else:
            self.image.set_alpha(255)

    def draw(self, surface  : pygame.Surface) -> None:
        """Draws player to the target surface."""
        assert self.rect is not None
        assert self.image is not None
        surface.blit(self.image, self.rect)
