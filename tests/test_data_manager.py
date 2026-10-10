from pathlib import Path

from src.data_manager import DataManager


def test_save_run_persists_history_and_new_high_score(tmp_path: Path) -> None:
    manager = DataManager(tmp_path / "data")

    assert manager.save_run(score=25, time_survived=12.5)
    assert manager.high_score == 25

    reloaded = DataManager(tmp_path / "data")
    assert reloaded.high_score == 25
    assert reloaded.run_history == [{"score": 25, "time": 12.5}]


def test_lower_score_does_not_replace_high_score(tmp_path: Path) -> None:
    manager = DataManager(tmp_path / "data")
    manager.save_run(score=25, time_survived=12)

    assert not manager.save_run(score=10, time_survived=8)
    assert manager.high_score == 25
    assert len(manager.run_history) == 2


def test_reset_clears_persisted_scores_and_history(tmp_path: Path) -> None:
    manager = DataManager(tmp_path / "data")
    manager.save_run(score=25, time_survived=12)

    manager.reset_data()

    assert manager.high_score == 0
    assert manager.run_history == []
    assert not manager.highscore_file.exists()
