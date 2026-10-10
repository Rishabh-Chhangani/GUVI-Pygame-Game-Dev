import json
from pathlib import Path

class DataManager:
    """Handles persistence of high scores and other game data."""
    def __init__(self, data_dir: str | Path = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.highscore_file = self.data_dir / "highscores.json"
        
        # Load or initialize high score
        self.high_score = self.load_high_score()
        
    def load_high_score(self) -> int:
        if self.highscore_file.exists():
            try:
                with open(self.highscore_file, 'r') as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
            except (json.JSONDecodeError, IOError):
                return 0
        return 0
        
    def save_high_score(self, score: int) -> bool:
        """Saves high score if it's a new record. Returns True if record was broken."""
        if score > self.high_score:
            self.high_score = score
            try:
                with open(self.highscore_file, 'w') as f:
                    json.dump({"high_score": self.high_score}, f)
                return True
            except IOError:
                pass
        return False
