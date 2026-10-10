"""
Ninja Collector - Main Entry Point
"""
import sys
from importlib import import_module
from pathlib import Path
from typing import Protocol, cast


class _JuriggedModule(Protocol):
    def watch(self, pattern: str) -> object: ...

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Live code watching support
if "--live" in sys.argv or "-l" in sys.argv:
    try:
        jurigged = cast(_JuriggedModule, import_module("jurigged"))
        jurigged.watch(str(ROOT_DIR / "src"))
        print("[⚡ JURIGGED] Live code reloading active! Changes in src/ update instantly on save.")
    except ImportError:
        print("[WARNING] jurigged not installed. Run 'pip install jurigged'")

from src.game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
