import pygame
import pytest

from src.entities.coin import CoinSprite


def make_coin() -> CoinSprite:
    frames = [pygame.Surface((10, 10), pygame.SRCALPHA) for _ in range(2)]
    return CoinSprite(frames, x=30, y=30, speed=100, animation_delay=0.1)


def test_coin_fall_and_animation_scale_with_delta_time() -> None:
    coin = make_coin()
    assert coin.rect is not None
    initial_y = coin.rect.y
    initial_frame = coin.current_frame

    coin.update(screen_width=100, screen_height=200, dt=0.1)

    assert coin.rect.y == initial_y + 10
    assert coin.current_frame == (initial_frame + 1) % len(coin.frames)
    assert not coin.respawned_this_update


def test_coin_respawns_after_leaving_screen(monkeypatch: pytest.MonkeyPatch) -> None:
    coin = make_coin()
    assert coin.rect is not None
    coin.rect.top = 201
    coin.pos_y = float(coin.rect.y)
    def minimum_int(low: int, _high: int) -> int:
        del _high
        return low

    def minimum_float(low: float, _high: float) -> float:
        del _high
        return low

    monkeypatch.setattr("src.entities.coin.random.randint", minimum_int)
    monkeypatch.setattr("src.entities.coin.random.uniform", minimum_float)

    coin.update(screen_width=100, screen_height=200, dt=0)

    assert coin.respawned_this_update
    assert coin.rect.top < 0
    assert coin.speed == 180
