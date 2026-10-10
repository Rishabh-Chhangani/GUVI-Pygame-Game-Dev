import json
from pathlib import Path


class DataManager:
    """Handles persistence of high scores and other game data."""
    def __init__(self, data_dir: str | Path = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.highscore_file = self.data_dir / "highscores.json"
        
        # Load or initialize data
        self.run_history: list[dict[str, int | float]] = []
        self.high_score = 0
        self.load_data()
        
    def load_data(self) -> None:
        if self.highscore_file.exists():
            try:
                with open(self.highscore_file, 'r') as f:
                    data = json.load(f)
                    self.high_score = data.get("high_score", 0)
                    self.run_history = data.get("run_history", [])
            except (json.JSONDecodeError, OSError):
                pass
        
    def save_run(self, score: int, time_survived: float) -> bool:
        """Saves a run to history. Updates and returns True if it's a new high score."""
        self.run_history.append({"score": score, "time": time_survived})
        
        is_new_high_score = False
        if score > self.high_score:
            self.high_score = score
            is_new_high_score = True
            
        try:
            with open(self.highscore_file, 'w') as f:
                json.dump({
                    "high_score": self.high_score,
                    "run_history": self.run_history
                }, f)
        except OSError:
            pass
            
        return is_new_high_score

    def reset_data(self) -> None:
        """Resets all high scores and run history."""
        self.high_score = 0
        self.run_history = []
        if self.highscore_file.exists():
            try:
                self.highscore_file.unlink()
            except OSError:
                pass
