import pygame
import random

class UIHealthBar:
    def __init__(self, max_health: int):
        self.max_health = max_health
        self.actual_health = max_health
        self.animated_health = float(max_health)
        
    def take_damage(self, amount: int):
        self.actual_health = max(0, self.actual_health - amount)
        
    def update(self, dt: float):
        # Smoothly interpolate the animated health towards the actual health
        # Higher multiplier = faster catch-up
        self.animated_health += (self.actual_health - self.animated_health) * 10.0 * dt
        
    def draw(self, surface: pygame.Surface, x: int, y: int, width: int, height: int):
        # Background (empty bar)
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (75, 35, 35), bg_rect)
        
        # Damage flash (red bar based on animated health)
        anim_ratio = max(0, min(1, self.animated_health / self.max_health))
        anim_width = int(width * anim_ratio)
        if anim_width > 0:
            anim_rect = pygame.Rect(x, y, anim_width, height)
            pygame.draw.rect(surface, (255, 50, 50), anim_rect)
            
        # Actual health (green foreground)
        real_ratio = max(0, min(1, self.actual_health / self.max_health))
        real_width = int(width * real_ratio)
        if real_width > 0:
            real_rect = pygame.Rect(x, y, real_width, height)
            pygame.draw.rect(surface, (70, 190, 95), real_rect)

class DamagePopup:
    def __init__(
        self,
        x: float,
        y: float,
        text: str,
        color: tuple[int, int, int] = (255, 50, 50),
        font_size: int = 36,
    ):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.timer = 1.0  # Popup lives for 1 second
        self.font = pygame.font.Font(None, font_size)
        
        # Slight random horizontal drift
        self.dx = random.uniform(-20, 20)
        self.dy = -80.0  # Float upwards
        
    def update(self, dt: float):
        self.timer -= dt
        self.x += self.dx * dt
        self.y += self.dy * dt
        
    def draw(self, surface: pygame.Surface):
        if self.timer > 0:
            # Render text
            text_surface = self.font.render(self.text, True, self.color)
            
            # Fade out alpha calculation
            alpha = int(255 * min(1.0, self.timer * 2)) # Fade quickly at the end
            text_surface.set_alpha(alpha)
            
            # Draw Outline for visibility
            outline = self.font.render(self.text, True, (0, 0, 0))
            outline.set_alpha(alpha)
            
            # Blit outline offset by 2 pixels in each direction
            for ox, oy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
                surface.blit(outline, (int(self.x) + ox, int(self.y) + oy))
                
            surface.blit(text_surface, (int(self.x), int(self.y)))
