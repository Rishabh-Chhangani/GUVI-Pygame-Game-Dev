# Developer Journal: Ninja Collector

This document serves as a post-mortem and developer journal for the Ninja Collector project. It outlines the technical decisions made, the tools utilized, the challenges encountered during development, and the solutions implemented.

## 🛠️ Tools & Technologies Used

### Core Technologies
*   **Python 3.12:** The core language used for its readability and massive ecosystem.
*   **Pygame-CE (Community Edition):** Chosen over standard Pygame because it is actively maintained, has better performance, and includes modern features like improved delta-time support.

### DevOps & CI/CD
*   **GitHub Actions:** Selected for Continuous Integration (CI) and Continuous Delivery (CD) because it integrates natively with GitHub and removes the need to host a separate Jenkins/Travis server.
*   **PyInstaller:** Used to package the Python scripts and assets into a standalone Windows `.exe`. This was critical to ensure non-developers could play the game without installing Python.
*   **Pytest & Pytest-Cov:** Chosen for the automated testing framework. Pytest is the industry standard for Python, and pytest-cov allowed us to generate exact coverage percentages and missing-line reports.
*   **Ruff & Pip-Audit:** Used in the CI pipeline to enforce strict code formatting and scan dependencies for known security vulnerabilities.

---

## 🧗‍♂️ Challenges Faced & Solutions

### 1. The Kenney UI Font Quirk
**The Problem:** We used the beautiful Kenney UI future font (`kenvector_future.ttf`), but we quickly noticed that its capital "K" looked almost identical to an "H". This caused our "BACK" buttons to read as "BACH".
**The Solution:** Rather than digging for a new font and ruining the cohesive aesthetic, we solved this at the UX level by permanently changing the button labels from "BACK" to "RETURN". 

### 2. Audio State Desync on Pause/Resume
**The Problem:** When the user paused the game via the `ESC` key, the `PauseScene` correctly paused the background music. However, if the user clicked the mouse on the "RESUME" or "RESTART" UI buttons to unpause, the game state returned to `PLAYING` but the music stayed permanently paused.
**The Solution:** We tracked down the mouse click event handlers in `game.py` (`handle_pause_click`) and explicitly injected `self.audio_manager.unpause_bgm()` into the UI button flows, ensuring the audio state stayed perfectly synced with the game state regardless of whether the user used the keyboard or the mouse.

### 3. Draggable UI Slider Math & Layout Alignment
**The Problem:** Implementing a custom draggable volume slider from scratch required mapping a mouse X-coordinate to a 0.0-1.0 percentage while keeping the slider thumb constrained to the track. Furthermore, as the percentage text changed width (e.g., from `100%` to `0%`), the entire row became off-center on the Options screen.
**The Solution:** We separated the logic. The `Slider` component handles its own clamp math (`max(0, min(1, relative_x / track_width))`). For the layout, we calculated the total width of the text + slider together, centered that bounding box on the screen, and anchored the text to the `midright` coordinate of the slider track so it expands outward without shifting the slider itself.

### 4. Continuous Integration Testing for a Graphical Game
**The Problem:** GitHub Actions runs on headless Ubuntu servers without a display. Attempting to run Pygame would crash the pipeline because there is no video driver to open a window.
**The Solution:** We decoupled the core game logic (math, collision, scores, entity state) from the rendering loop. We wrote `pytest` functions that manually feed `dt` (delta-time) into `update()` functions and assert the mathematical results without ever calling `pygame.display.set_mode()`.

---

## 🔮 Future Improvements

*(Write about what you would like to add next: e.g., difficulty scaling, new enemies, power-ups, web deployment via Pygbag, etc.)*
