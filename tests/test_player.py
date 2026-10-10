import pygame
import pytest

from src import config
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


@pytest.mark.parametrize(("dt", "expected_x"), [(1.0, 360), (0.5, 180)])
def test_movement_matches_speed_over_delta_time(
    monkeypatch: pytest.MonkeyPatch,
    dt: float,
    expected_x: int,
) -> None:
    frame = pygame.Surface((20, 20), pygame.SRCALPHA)
    player = Player(
        frames=[frame],
        x=10,
        size=(20, 20),
        speed=config.PLAYER_SPEED,
    )
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: PressedKeys(pygame.K_RIGHT))

    player.handle_input(screen_width=1000, screen_height=200, dt=dt)

    assert player.rect is not None
    assert player.rect.x == 10 + expected_x


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


def test_three_pickups_within_combo_window_give_three_x(player: Player) -> None:
    for _ in range(3):
        player.record_coin_pickup(0.1)

    assert player.get_combo_multiplier() == 3


def test_combo_expires_after_long_delta(player: Player) -> None:
    player.record_coin_pickup(0)

    player.update_combo(dt=5.0)

    assert player.get_combo_multiplier() == 1
    assert player.combo_timer == 0.0


def test_player_clamps_out_of_bounds_x_position(
    player: Player,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert player.rect is not None
    player.rect.x = -100
    player.pos_x = -100.0
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: PressedKeys())

    player.handle_input(screen_width=200, screen_height=200, dt=0)

    assert player.rect.x == 0


def test_player_update_switches_idle_running_and_catch_animations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    idle_frame = pygame.Surface((20, 20), pygame.SRCALPHA)
    running_frame = pygame.Surface((20, 20), pygame.SRCALPHA)
    catch_frames = [
        pygame.Surface((20, 20), pygame.SRCALPHA) for _ in range(2)
    ]
    running_frame.fill((0, 255, 0, 255))
    catch_frames[0].fill((255, 0, 0, 255))
    player = Player(
        frames=[idle_frame],
        running_frames=[running_frame],
        catch_frames=catch_frames,
        x=10,
        size=(20, 20),
        speed=100,
        animation_delay=0.1,
    )
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: PressedKeys())

    player.update(screen_width=200, screen_height=200, dt=0)
    assert player.current_animation is player.frames

    monkeypatch.setattr(
        pygame.key,
        "get_pressed",
        lambda: PressedKeys(pygame.K_RIGHT),
    )
    player.update(screen_width=200, screen_height=200, dt=0.1)
    assert player.current_animation is player.running_frames

    player.start_catch()
    player.update(screen_width=200, screen_height=200, dt=0)
    assert player.is_catching
    assert player.current_frame == 0
    assert player.image is not None
    assert player.image.get_at((0, 0)) == (255, 0, 0, 255)
