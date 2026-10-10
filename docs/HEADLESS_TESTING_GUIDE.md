# Headless Testing Guide: Ninja Collector

This document outlines the scope of **Headless Testing** (testing the game programmatically without opening a graphical window or requiring a video driver). It breaks down exactly what components of the game can be reliably automated and verified in a CI/CD pipeline (like GitHub Actions), organized by our development phases.

---

## 🏗️ Phase 1: Modular Architecture & Data
*These components form the foundation of the game and deal primarily with data and configuration.*

*   **Configuration Integrity (`src/config.py`):**
    *   Verify that critical constants (e.g., `FPS`, `PLAYER_SPEED`, window dimensions) exist and are of the correct data type.
*   **Data Persistence (`src/data_manager.py`):**
    *   Test that saving a new high score successfully writes to the local JSON file.
    *   Test that saving a lower score does *not* overwrite an existing high score.
    *   Verify that corrupted JSON files are handled gracefully without crashing the game.
    *   Verify the factory reset function completely wipes historical data.
*   **Asset Manager Logic (`src/asset_manager.py`):**
    *   *(Requires Pygame mock)* Verify the caching dictionary correctly registers paths so files aren't loaded from the hard drive twice.

## 🎮 Phase 2: Gameplay & Collectibles
*This phase covers the core rules, math, and physics of the game. Because Pygame uses invisible `Rect` objects for hitboxes, all of this can be tested in memory.*

*   **Collision Detection (Hitboxes):**
    *   Force a `Coin` hitbox and `Player` hitbox to overlap and assert that the score increases.
    *   Force a `Bomb` hitbox and `Player` hitbox to overlap and assert that the player's health decreases.
*   **Combo System Math:**
    *   Test that collecting 3 coins within the time limit correctly applies a `3x` multiplier.
    *   Fast-forward the simulation (`dt = 5.0`) and verify the combo multiplier resets to `1x` when the timer expires.
*   **Spawner Logic (`src/entities/spawner.py`):**
    *   Verify that exactly 1 bomb spawns after a certain threshold of coins are dropped.
    *   Verify that stars only spawn based on the configured rare probability.
*   **Boundary Clamping:**
    *   Set the player's X coordinate to `-100` (off-screen left), run the update loop, and assert the position is clamped back to `0`.

## 🚀 Phase 3: Performance & Audio
*Testing timing, speed, and state triggers without actually rendering frames or playing audio.*

*   **Delta-Time (`dt`) Movement:**
    *   Test that feeding `dt = 1.0` (1 second) moves the player exactly `config.PLAYER_SPEED` pixels.
    *   Test that feeding `dt = 0.5` (half a second) moves the player exactly half that distance.
*   **Animation State Machine:**
    *   Verify that a player holding the left/right key switches from the `IDLE` animation state to the `RUNNING` state.
    *   Simulate a coin collection and verify the `CATCH` animation state is triggered and overrides the idle state temporarily.
*   **Audio State Triggers (`src/audio_manager.py`):**
    *   While we cannot test if sound comes out of the speakers, we *can* verify that `play_sfx("hit")` is correctly called internally when the player collides with a bomb.

## 🕹️ Phase 4: State Machine & UI Polish
*Testing the overarching flow of the application and menu logic.*

*   **Scene Transitions (`src/game.py` / Scenes):**
    *   Simulate pressing the "Start" button and verify the internal state changes from `MENU` to `PLAYING`.
    *   Simulate the player's health reaching `0` and verify the state immediately transitions to `GAME_OVER`.
*   **Pause Logic:**
    *   Simulate an `ESC` key press while `PLAYING` and verify the `update()` loop for enemies and the player stops executing.
*   **UI Click Boundaries (`src/ui/slider.py` etc.):**
    *   Feed fake mouse X/Y coordinates into the UI manager and verify that clicking within a button's `Rect` triggers the correct callback function (like opening the Options menu).
    *   Test the math of the volume slider (e.g., clicking the exact middle of the slider track translates to exactly `0.5` or `50%` volume in the logic).

---

### ❌ Out of Scope for Headless Testing
*(These must be tested manually by a human playing the game)*
1.  **Rendering Bugs:** If an image is drawn upside down or a font is missing a character (e.g., the "BACH" / "BACK" font issue).
2.  **Audio Output:** Verifying the volume levels and ensuring the OS audio driver plays the sounds correctly.
3.  **Game "Feel":** Balancing the difficulty, the feel of the controls, and ensuring the screen-shake effect looks good to the human eye.
