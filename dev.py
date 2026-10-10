"""
Ninja Collector - Development Auto-Reloader
Watches project files and automatically restarts the game on save.
"""
import subprocess
import sys
import time
from pathlib import Path

# File extensions to watch for modifications
WATCH_EXTENSIONS = {".py", ".png", ".jpg", ".jpeg", ".json", ".wav", ".mp3", ".ogg"}
PROJECT_ROOT = Path(__file__).resolve().parent


def get_latest_mtime() -> float:
    """Returns the most recent modification time across all watched project files."""
    mtimes: list[float] = []
    for path in PROJECT_ROOT.rglob("*"):
        # Ignore git, cache, and editor folders
        if any(part.startswith((".", "__pycache__", "build", "dist")) for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in WATCH_EXTENSIONS:
            try:
                mtimes.append(path.stat().st_mtime)
            except OSError:
                pass
    return max(mtimes) if mtimes else 0.0


def run_dev_server():
    print("=" * 60)
    print(" [~] Ninja Collector Auto-Reloader active!")
    print(" [SAVE] Save any Python or asset file (Ctrl+S) to auto-reload.")
    print(" [STOP] Press Ctrl+C in this terminal to stop.")
    print("=" * 60)

    last_mtime = get_latest_mtime()
    current_process = subprocess.Popen([sys.executable, "main.py"], cwd=str(PROJECT_ROOT))

    try:
        while True:
            time.sleep(0.4)
            current_mtime = get_latest_mtime()

            # Check if files changed
            if current_mtime > last_mtime:
                print("\n[⚡ DEV] Changes detected! Reloading game window...")
                last_mtime = current_mtime
                if current_process.poll() is None:
                    current_process.terminate()
                    try:
                        current_process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        current_process.kill()
                current_process = subprocess.Popen([sys.executable, "main.py"], cwd=str(PROJECT_ROOT))

            # If user manually closed the game window and no files changed, exit or keep waiting
            if current_process.poll() is not None:
                # Wait for next save to re-open or let user know
                pass

    except KeyboardInterrupt:
        print("\n[DEV] Stopping auto-reloader...")
        if current_process.poll() is None:
            current_process.terminate()
            try:
                current_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                current_process.kill()
        print("[DEV] Cleanly exited.")


if __name__ == "__main__":
    run_dev_server()
