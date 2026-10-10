# Ninja Collector 🥷🪙

[![Continuous Integration](https://github.com/Rishabh-Chhangani/GUVI-Pygame-Game-Dev/actions/workflows/ci.yml/badge.svg)](https://github.com/Rishabh-Chhangani/GUVI-Pygame-Game-Dev/actions/workflows/ci.yml)

**Ninja Collector** is an endless arcade survival and collection game built with Python and Pygame-CE. Dodge falling bombs, grab powerful magnets, collect coins to build your combo multiplier, and survive as long as you can to set the ultimate high score!

## 🎮 Play the Game
You do **not** need Python to play this game! 

1. Go to the **[Releases](../../releases/latest)** tab on this repository.
2. Download `NinjaCollector-Windows.zip`.
3. Extract the folder and double-click `NinjaCollector.exe` to play immediately on Windows.

*(A SHA256 checksum is provided with every release to verify file integrity).*

## 🌟 Gameplay Mechanics
*   **Coins:** Catch coins rapidly to build your combo multiplier and skyrocket your score.
*   **Stars:** Rare drops that award a massive flat bonus (10 points + combo multiplier).
*   **Bombs:** Avoid at all costs! Taking a hit damages your health and shakes the screen.
*   **Magnets:** Catch a magnet to temporarily pull all nearby falling coins directly toward you.
*   **Leaderboard:** Your best runs are automatically tracked and saved.

## 🛠️ DevOps & CI/CD Pipeline
This project is built using a complete, professional-grade Continuous Integration and Continuous Delivery (CI/CD) pipeline:
*   **GitHub Actions:** Automatically runs on every push and pull request.
*   **Code Quality:** Enforced via `ruff` linting.
*   **Security Scanning:** Dependencies are actively scanned for vulnerabilities using `pip-audit`.
*   **Automated Testing:** Core game logic and collision math are heavily unit-tested via `pytest` without requiring a graphical window.
*   **Automated Releases:** Pushing a `v*.*.*` tag automatically triggers a pipeline that uses `PyInstaller` to bundle the game into a standalone `.exe` and publishes it to GitHub Releases.

*Read more about our technical choices and problem-solving in the [Developer Journal](docs/DEVELOPER_JOURNAL.md). For DevOps architecture, see the [DevOps Plan](docs/Devops-Plan.md), [Pipeline Recovery Guide](docs/pipeline-recovery.md), and our [Headless Testing Strategy](docs/HEADLESS_TESTING_GUIDE.md).*

## 💻 Local Development Setup

If you want to modify the game or run the tests locally:

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rishabh-Chhangani/GUVI-Pygame-Game-Dev.git
   cd GUVI-Pygame-Game-Dev
   ```

2. **Install dependencies**
   Make sure you have Python 3.12+ installed.
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game**
   ```bash
   python main.py
   ```

4. **Run the test suite & coverage reports**
   This project includes a custom batch script that runs the tests and generates a beautifully formatted Markdown coverage report:
   ```bash
   .\run_coverage.bat
   ```
   *(Check the `reports/` folder afterward for your `coverage.md` file!)*

## 🎨 Credits
*   **Code:** Python & [Pygame Community Edition](https://pyga.me/)
*   **UI Assets:** Courtesy of [Kenney.nl](https://kenney.nl/)
*   **Audio:** Mix of custom generated assets and free-use sound effects.

---

## 🗺️ Development Roadmap & Architecture Index
This project was built following a strict 4-phase architectural plan. You can read the original design specifications for each phase below:

1. 📂 **[Phase 1: Modular Architecture](docs/phase-1-modular-architecture.md)** (Decoupling `main.py`, config, asset caching)
2. 📂 **[Phase 2: Gameplay & Collectibles](docs/phase-2-gameplay-and-collectibles.md)** (Animations, hazards, groups)
3. 📂 **[Phase 3: Performance & Audio](docs/phase-3-performance-and-audio.md)** (Delta-time `dt`, audio mixers, downscaling)
4. 📂 **[Phase 4: State Machine & Polish](docs/phase-4-state-machine-and-polish.md)** (Scenes, high scores, builds)

*(For a deep dive into the current technical architecture, check out the [Project Overview](docs/PROJECT_OVERVIEW.md)).*