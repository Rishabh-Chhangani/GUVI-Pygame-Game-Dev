import random
import math
import pygame

class Particle:
    """A single particle for visual effects."""
    def __init__(self, x: float, y: float, color: tuple[int, int, int], is_shrapnel: bool = False):
        self.x = x
        self.y = y
        self.color = color
        self.is_shrapnel = is_shrapnel
        
        # Random velocity
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(50, 200) if not is_shrapnel else random.uniform(100, 350)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.lifetime = random.uniform(0.3, 0.7) if not is_shrapnel else random.uniform(0.5, 1.2)
        self.max_lifetime = self.lifetime
        self.size = random.uniform(3, 6) if not is_shrapnel else random.uniform(4, 9)
        
    def update(self, dt: float) -> bool:
        """Update particle physics. Returns True if alive, False if dead."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Add some gravity
        self.vy += 400 * dt
        
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface):
        """Draw the particle."""
        if self.lifetime <= 0:
            return
            
        ratio = self.lifetime / self.max_lifetime
        current_size = max(1.0, self.size * ratio)
        
        alpha = int(255 * ratio)
        if alpha > 0:
            surf = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (int(current_size), int(current_size)), int(current_size))
            surface.blit(surf, (int(self.x - current_size), int(self.y - current_size)))

class ParticleSystem:
    """Manages all active particles in the game."""
    def __init__(self):
        self.particles: list[Particle] = []
        
    def emit_coin_sparkles(self, x: float, y: float, count: int = 10):
        """Emits gold sparkles for coin collection."""
        for _ in range(count):
            self.particles.append(Particle(x, y, (255, 215, 0))) # Gold
            
    def emit_bomb_shrapnel(self, x: float, y: float, count: int = 15):
        """Emits grey/orange shrapnel for bomb explosion."""
        colors = [(100, 100, 100), (150, 150, 150), (255, 100, 50), (200, 50, 20)]
        for _ in range(count):
            self.particles.append(Particle(x, y, random.choice(colors), is_shrapnel=True))
            
    def update(self, dt: float):
        """Updates all particles and removes dead ones."""
        self.particles = [p for p in self.particles if p.update(dt)]
        
    def draw(self, surface: pygame.Surface):
        """Draws all active particles."""
        for p in self.particles:
            p.draw(surface)
