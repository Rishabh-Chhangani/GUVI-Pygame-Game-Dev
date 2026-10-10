import pygame
import pytest

from src.entities.player import Player


class PressedKeys:
    def __init__(self, *keys: int) -> None:
        self.keys = set(keys)

    def __getitem__(self, key: int) -> bool:
        return key in self.keys


@pytest.fixture
def player() -> Player:
    frame = pygame.Surface((20, 20), pygame.SRCALPHA)
    return Player(
        frames=[frame],
        x=10,
        y=10,
        size=(20, 20),
        speed=100,
        bottom_offset=20,
        max_health=100,
    )


def test_movement_scales_with_delta_time_and_anchors_to_bottom(
    player: Player,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: PressedKeys(pygame.K_RIGHT))

    player.handle_input(screen_width=200, screen_height=200, dt=0.5)

    assert player.rect is not None
    assert player.rect.x == 60
    assert player.rect.bottom == 180
    assert player.is_moving


@pytest.mark.parametrize(
    ("start_x", "pressed_key", "expected_x"),
    [
        (0, pygame.K_LEFT, 0),
        (80, pygame.K_RIGHT, 80),
    ],
)
def test_movement_is_clamped_to_screen_edges(
    player: Player,
    monkeypatch: pytest.MonkeyPatch,
    start_x: int,
    pressed_key: int,
    expected_x: int,
) -> None:
    assert player.rect is not None
    player.rect.x = start_x
    player.pos_x = float(start_x)
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: PressedKeys(pressed_key))

    player.handle_input(screen_width=100, screen_height=200, dt=1.0)

    assert player.rect.x == expected_x


def test_damage_respects_invulnerability_and_health_floor(player: Player) -> None:
    assert player.take_damage(30)
    assert player.health == 70
    assert player.combo == 0

    assert not player.take_damage(30)
    assert player.health == 70

    player.invulnerability_timer = 0
    assert player.take_damage(1000)
    assert player.health == 0


def test_combo_multiplier_increases_and_expires(player: Player) -> None:
    player.record_coin_pickup(0)
    assert player.get_combo_multiplier() == 1

    player.record_coin_pickup(0)
    assert player.get_combo_multiplier() == 2

    player.update_combo(player.combo_window)

    assert player.combo == 0
    assert player.get_combo_multiplier() == 1
