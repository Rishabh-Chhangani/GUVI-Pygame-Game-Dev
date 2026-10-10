from typing import Any

import pygame
import pytest

from src import config
from src.game import Game
from src.scenes.base import BaseScene
from src.scenes.manager import SceneManager
from src.scenes.menu import MenuScene
from src.scenes.pause import PauseScene
from src.scenes.play import PlayScene


class RecordingSpawner:
    def __init__(self) -> None:
        self.bombs_spawned = 0
        self.stars_spawned = 0
        self.magnets_spawned = 0

    def spawn_bomb(self, _width: int, difficulty: float) -> None:
        del _width, difficulty
        self.bombs_spawned += 1

    def spawn_star(self, _width: int, difficulty: float) -> None:
        del _width, difficulty
        self.stars_spawned += 1

    def spawn_magnet(self, _width: int, difficulty: float) -> None:
        del _width, difficulty
        self.magnets_spawned += 1


class DummyWindow:
    def get_size(self) -> tuple[int, int]:
        return (800, 600)


class DummyPlayer(pygame.sprite.Sprite):
    def __init__(self, health: int = 100) -> None:
        super().__init__()
        self.rect = pygame.Rect(10, 10, 20, 20)
        self.health = health
        self.magnet_timer = 0.0
        self.combo = 1
        self.invulnerability_timer = 0.0
        self.recorded_pickups = 0
        self.catch_started = False

    def update(
        self,
        _screen_width: int,
        _screen_height: int,
        _dt: float,
        _difficulty: float,
    ) -> None:
        del _screen_width, _screen_height, _dt, _difficulty

    def record_coin_pickup(self, _dt: float) -> None:
        del _dt
        self.recorded_pickups += 1
        self.combo += 1

    def get_combo_multiplier(self) -> int:
        return self.combo

    def start_catch(self) -> None:
        self.catch_started = True

    def take_damage(self, amount: int) -> bool:
        if self.invulnerability_timer > 0:
            return False
        self.health = max(0, self.health - amount)
        self.invulnerability_timer = 1.0
        return True

    def activate_magnet(self, duration: float) -> None:
        self.magnet_timer = duration


class DummyItem(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.Rect | None = None, value: int = 1) -> None:
        super().__init__()
        self.rect = rect or pygame.Rect(10, 10, 10, 10)
        self.value = value
        self.reset_count = 0
        self.respawned_this_update = False

    def update(self, *_args: object) -> None:
        del _args
        self.respawned_this_update = False

    def reset(self, *_args: object) -> None:
        del _args
        self.reset_count += 1
        assert self.rect is not None
        self.rect.left = 500


class DummyHud:
    def update(self, _dt: float, _health: int) -> None:
        del _dt, _health


class DummyPopup:
    def __init__(self, *_args: object) -> None:
        del _args
        self.timer = 1.0

    def update(self, dt: float) -> None:
        self.timer -= dt


class DummyParticles:
    def update(self, _dt: float) -> None:
        del _dt

    def emit_coin_sparkles(self, *_args: object, **_kwargs: object) -> None:
        del _args, _kwargs

    def emit_bomb_shrapnel(self, *_args: object, **_kwargs: object) -> None:
        del _args, _kwargs


class DummyAudio:
    def __init__(self) -> None:
        self.played: list[str] = []

    def play_sfx(self, name: str) -> None:
        self.played.append(name)

    def pause_bgm(self) -> None:
        pass

    def unpause_bgm(self) -> None:
        pass


class DummyDataManager:
    def __init__(self) -> None:
        self.saved_runs: list[tuple[int, float]] = []

    def save_run(self, score: int, survival_time: float) -> bool:
        self.saved_runs.append((score, survival_time))
        return True


class DummySceneManager:
    def __init__(self) -> None:
        self.scene: object | None = None

    def switch_to(self, scene: object) -> None:
        self.scene = scene


@pytest.fixture
def game(monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.setattr("src.game.DamagePopup", DummyPopup)
    instance: Any = Game.__new__(Game)
    instance._state = "PLAYING"
    instance.scenes = {
        "GAME_OVER": BaseScene(instance),
        "PAUSED": BaseScene(instance),
        "PLAYING": BaseScene(instance),
    }
    instance.scene_manager = DummySceneManager()
    instance.width = 800
    instance.height = 600
    instance.player = DummyPlayer()
    instance.coins_group = pygame.sprite.Group()
    instance.bombs_group = pygame.sprite.Group()
    instance.stars_group = pygame.sprite.Group()
    instance.magnets_group = pygame.sprite.Group()
    instance.score = 0
    instance.high_score = 0
    instance.survival_time = 5.0
    instance.camera_shake = 0.0
    instance.difficulty_multiplier = 1.0
    instance.coins_since_bomb = 0
    instance.coins_since_star = 0
    instance.coins_since_magnet = 0
    instance.coin_drop_count = 0
    instance.bomb_drop_count = 0
    instance.star_drop_count = 0
    instance.popups = []
    instance.hud = DummyHud()
    instance.particle_system = DummyParticles()
    instance.audio_manager = DummyAudio()
    instance.data_manager = DummyDataManager()
    return instance


def update_playing(game: Any, dt: float = 0.1) -> None:
    Game.update_playing(game, dt)


def test_coin_collision_scores_with_combo_and_respawns(game: Any) -> None:
    coin = DummyItem(value=5)
    game.coins_group.add(coin)

    update_playing(game)

    assert game.score == 10
    assert game.player.recorded_pickups == 1
    assert game.player.catch_started
    assert coin.reset_count == 1
    assert game.coin_drop_count == 1


def test_star_collision_scores_and_removes_star(game: Any) -> None:
    star = DummyItem()
    game.stars_group.add(star)

    update_playing(game)

    assert game.score == config.STAR_VALUE
    assert star not in game.stars_group


def test_bomb_collision_damages_player_and_respects_invulnerability(game: Any) -> None:
    bomb = DummyItem()
    game.bombs_group.add(bomb)

    update_playing(game)

    assert game.player.health == 100 - config.BOMB_DAMAGE
    assert bomb not in game.bombs_group
    assert game.camera_shake == 15.0
    assert "hit" in game.audio_manager.played

    protected_bomb = DummyItem()
    game.bombs_group.add(protected_bomb)
    update_playing(game)

    assert game.player.health == 100 - config.BOMB_DAMAGE
    assert protected_bomb in game.bombs_group


def test_zero_health_transitions_to_game_over_and_saves_run(game: Any) -> None:
    game.player.health = 0
    game.score = 42

    update_playing(game)

    assert game.state == "GAME_OVER"
    assert game.scene_manager.scene is game.scenes["GAME_OVER"]
    assert game.data_manager.saved_runs == [(42, 5.0)]
    assert game.high_score == 42
    assert "game_over" in game.audio_manager.played


def test_state_transition_selects_matching_scene(game: Any) -> None:
    game.state = "PAUSED"

    assert game.state == "PAUSED"
    assert game.scene_manager.scene is game.scenes["PAUSED"]


def test_menu_play_and_pause_scene_events_switch_states(
    game: Game,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    game.scenes["MENU"] = BaseScene(game)
    game.state = "MENU"
    monkeypatch.setattr(
        game,
        "start_game_play",
        lambda: setattr(game, "state", "PLAYING"),
    )

    MenuScene(game).handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    )
    assert game.state == "PLAYING"

    PlayScene(game).handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    )
    assert game.state == "PAUSED"

    PauseScene(game).handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    )
    assert game.state == "PLAYING"


def test_bomb_spawns_exactly_at_configured_coin_threshold(game: Any) -> None:
    game.spawner = RecordingSpawner()

    for _ in range(config.COINS_PER_BOMB - 1):
        game._register_coin_drop()
    assert game.spawner.bombs_spawned == 0

    game._register_coin_drop()

    assert game.spawner.bombs_spawned == 1
    assert game.coins_since_bomb == 0


def test_star_spawns_at_configured_coin_threshold(game: Any) -> None:
    game.spawner = RecordingSpawner()

    for _ in range(config.COINS_PER_STAR - 1):
        game._register_coin_drop()
    assert game.spawner.stars_spawned == 0

    game._register_coin_drop()

    assert game.spawner.stars_spawned == 1
    assert game.coins_since_star == 0


def test_pause_scene_does_not_update_gameplay(game: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    game.window = DummyWindow()
    pause_scene = PauseScene(game)
    game.scene_manager = SceneManager(pause_scene)

    player_update_calls: list[tuple[int, int, float, float]] = []

    def record_player_update(
        screen_width: int,
        screen_height: int,
        dt: float,
        difficulty: float,
    ) -> None:
        player_update_calls.append((screen_width, screen_height, dt, difficulty))

    monkeypatch.setattr(game.player, "update", record_player_update)
    bomb = DummyItem()
    game.bombs_group.add(bomb)
    bomb_update_calls: list[tuple[int, int, float]] = []

    def record_bomb_update(
        screen_width: int,
        screen_height: int,
        dt: float,
    ) -> None:
        bomb_update_calls.append((screen_width, screen_height, dt))

    monkeypatch.setattr(bomb, "update", record_bomb_update)

    game.update(dt=0.5)

    assert player_update_calls == []
    assert bomb_update_calls == []


def test_clicking_start_button_calls_game_start(game: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    game.play_button_rect = pygame.Rect(100, 100, 80, 40)
    game.state = "MENU"
    monkeypatch.setattr(
        game,
        "start_game_play",
        lambda: setattr(game, "state", "PLAYING"),
    )

    game.handle_menu_click(game.play_button_rect.center)

    assert game.state == "PLAYING"


def test_clicking_options_button_opens_options_state(game: Any) -> None:
    game.resume_button_rect = pygame.Rect(0, 0, 10, 10)
    game.restart_button_rect = pygame.Rect(20, 0, 10, 10)
    game.options_button_rect = pygame.Rect(100, 100, 80, 40)
    game.state = "PAUSED"

    game.handle_pause_click(game.options_button_rect.center)

    assert game.state == "OPTIONS"
    assert "click" in game.audio_manager.played
