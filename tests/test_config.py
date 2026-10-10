from src import config


def test_critical_game_configuration_has_expected_types_and_values() -> None:
    assert isinstance(config.FPS, int) and config.FPS > 0
    assert isinstance(config.DEFAULT_WIDTH, int) and config.DEFAULT_WIDTH > 0
    assert isinstance(config.DEFAULT_HEIGHT, int) and config.DEFAULT_HEIGHT > 0
    assert isinstance(config.PLAYER_SPEED, int) and config.PLAYER_SPEED > 0
