import random

import pygame

from src import config
from src.entities.bomb import BombSprite
from src.entities.coin import CoinSprite
from src.entities.star import StarSprite


class Spawner:
    """Centralizes falling-item spawning for gameplay phase 2."""

    def __init__(
        self,
        coin_group: pygame.sprite.Group[CoinSprite],
        bomb_group: pygame.sprite.Group[BombSprite],
        star_group: pygame.sprite.Group[StarSprite],
        coin_frames: list[pygame.Surface],
        bomb_image: pygame.Surface,
        star_image: pygame.Surface,
    ):
        self.coin_group = coin_group
        self.bomb_group = bomb_group
        self.star_group = star_group
        self.coin_frames = coin_frames
        self.bomb_image = bomb_image
        self.star_image = star_image

    def spawn_coin(self, screen_width: int, screen_height: int | None = None) -> CoinSprite:
        del screen_height
        spawn_x = random.randint(30, max(30, screen_width - config.COIN_SIZE[0] - 30))
        spawn_y = -random.randint(50, 400)
        speed = random.uniform(180.0, 260.0)
        coin = CoinSprite(self.coin_frames, spawn_x, spawn_y, speed=speed)
        self.coin_group.add(coin)
        return coin

    def spawn_bomb(self, screen_width: int, screen_height: int | None = None) -> BombSprite:
        del screen_height
        spawn_x = random.randint(30, max(30, screen_width - config.BOMB_SIZE[0] - 30))
        spawn_y = -random.randint(50, 400)
        bomb = BombSprite(
            self.bomb_image,
            spawn_x,
            spawn_y,
            speed=random.uniform(180.0, 260.0),
        )
        self.bomb_group.add(bomb)
        return bomb

    def spawn_star(self, screen_width: int, screen_height: int | None = None) -> StarSprite:
        del screen_height
        spawn_x = random.randint(30, max(30, screen_width - config.STAR_SIZE[0] - 30))
        spawn_y = -random.randint(50, 400)
        star = StarSprite(
            self.star_image,
            spawn_x,
            spawn_y,
            speed=random.uniform(180.0, 260.0),
        )
        self.star_group.add(star)
        return star

    def spawn_initial_coins(self, screen_width: int) -> None:
        for _ in range(config.COIN_COUNT):
            self.spawn_coin(screen_width)
