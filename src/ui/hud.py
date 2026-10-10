import pygame
from src import config
from src.ui.juice import UIHealthBar

class HUD:
    """Render score, health, and the player status bar."""

    def __init__(self, font: pygame.font.Font | None = None):
        self.font = font if font is not None else pygame.font.Font(config.FONT_FILE, config.SCORE_FONT_SIZE)
        self.health_bar = UIHealthBar(config.PLAYER_MAX_HEALTH)

    def update(self, dt: float, current_health: int):
        self.health_bar.actual_health = current_health
        self.health_bar.update(dt)

    def draw(self, surface: pygame.Surface, score: int, health: int, max_health: int, survival_time: float) -> None:
        score_surface = self.font.render(f"Score: {score}", True, config.HUD_COLOR)
        surface.blit(score_surface, config.SCORE_POSITION)
        
        timer_surface = self.font.render(f"Time: {int(survival_time)}s", True, (255, 200, 100))
        surface.blit(timer_surface, (config.SCORE_POSITION[0] + 150, config.SCORE_POSITION[1]))

        health_surface = self.font.render(f"HP: {health}", True, config.HUD_COLOR)
        surface.blit(health_surface, config.HEALTH_POSITION)

        x, y = config.HEALTH_BAR_POSITION
        w, h = config.HEALTH_BAR_SIZE
        self.health_bar.max_health = max_health
        self.health_bar.draw(surface, x, y, w, h)
