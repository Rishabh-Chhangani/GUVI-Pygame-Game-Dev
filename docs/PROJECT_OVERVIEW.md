
# Ninja Collector

## 1. Project Overview

Ninja Collector is a small single-window pygame project in which the player moves horizontally at the bottom of the screen, collects falling coins and rare stars, and avoids falling bombs. The active runtime is driven by a central `Game` controller that owns the game loop, state transitions, rendering, and entity lifecycle.

The current gameplay loop is structured as: input/events -> update -> render -> repeat. The program starts in the main menu, transitions into gameplay when PLAY is selected, pauses using a pause menu, and enters `GAME_OVER` when the player's health reaches zero after bomb impacts.

## 2. Technology Stack

- Python: no explicit Python version is pinned in project configuration; the project runs with the active local Python environment that executes the game.
- pygame-ce: the project imports `pygame` and the active project setup is aligned with pygame-ce. `requirements.txt` declares `pygame-ce>=2.5.0` and the current development environment is using pygame-ce behavior consistent with 2.5.8.
- Git / GitHub: the repository includes Git metadata and is hosted as a GitHub project repository.
- VS Code: the project is developed in the editor environment used for the session, with GitHub Copilot assisting in iteration and validation.
- jurigged: included in `requirements.txt` and used by `main.py` when the `--live` / `-l` option is passed for live file watching.

## 3. Project Structure

```text
Ninja Collector/
├── assets/
│   ├── Catch/
│   ├── Runing/
│   ├── idle_anim/
│   ├── bg1.png
│   ├── coin1.png ... coin7.png
│   └── other project art assets
├── docs/
│   └── PROJECT_OVERVIEW.md
├── src/
│   ├── asset_manager.py
│   ├── config.py
│   ├── entities/
│   │   ├── coin.py
│   │   ├── bomb.py
│   │   ├── player.py
│   │   └── star.py
│   └── game.py
├── .gitignore
├── README.md
├── dev.py
├── main.py
├── requirements.txt
├── issues.txt
├── skills-lock.json
├── GUVI-Pygame-Game-Dev.zip
└── .github/
```

Important modules:

- `main.py`: application entry point; creates `Game` and starts the loop.
- `dev.py`: development helper that watches project files and restarts the app when files change; includes a lightweight live-reload workflow.
- `src/game.py`: central controller for game state, event handling, entity creation, game updates, rendering, lifecycle, and UI state transitions.
- `src/config.py`: shared configuration for window size, asset paths, animation frame names, game constants, and UI settings.
- `src/asset_manager.py`: loads images and animation sequences, caches resources, and supports proportional scaling for collectibles.
- `src/entities/player.py`: player sprite with movement, animation state selection, and bottom anchoring.
- `src/entities/coin.py`: collectible sprite with falling movement, frame animation, and respawn behavior.
- `src/entities/bomb.py`: falling bomb hazard sprite; Game handles its collision damage.
- `src/entities/star.py`: falling rare collectible sprite; Game handles its score value.
- `assets/`: image resources used for the background, player animations, coins, bomb, and star.

## 4. Architecture

The current implementation is a single-controller Pygame game with explicit state transitions.

```text
Game
├── Game State (MENU / PLAYING / PAUSED / OPTIONS / GAME_OVER)
├── Player
├── Collectibles (CoinSprite, StarSprite)
├── Hazard (BombSprite)
├── Asset Manager
├── HUD / Menu UI
├── Configuration
└── Event Loop
```

### Main game lifecycle
- `main.py` creates a `Game` instance and calls `run()`.
- `Game.run()` owns the main loop and repeatedly calls `handle_events()`, `update()`, and `draw()`.

### Game loop
- `pygame.time.Clock` controls tick rate via `config.FPS`.
- Each frame drains `pygame.event.get()` and updates the current state.

### Event handling
- `Game.handle_events()` handles active window resize, quit, keyboard actions, and menu/button interaction.
- Keyboard actions include toggling resizable mode, hot reload via `F5`, and ESC-based pause behavior.
- Mouse click handling is used for main menu, pause menu, options, and game-over actions.

### Update phase
- The update loop only processes gameplay when the state is `PLAYING`.
- Coins, bombs, and stars are moved; coin respawns are counted for hazard drop scheduling.
- The player position is updated and animated.
- Collision detection is performed with `pygame.sprite.spritecollide()`.
- Score changes and catch animation start when a coin is collected.
- Bomb collisions reduce player health; zero health transitions into `GAME_OVER`.

### Rendering phase
- Background is drawn first, then world sprites, then player.
- HUD text is rendered with `pygame.font.Font`.
- Menu and pause-state overlays are rendered as simple custom UI surfaces and button rectangles.

### Entity responsibilities
- `Player` handles player movement, horizontal boundaries, current direction, and animation state transitions.
- `CoinSprite` handles coin falling, animation, and respawn.
- `BombSprite` handles bomb falling and off-screen respawn; `Game` handles collision damage.
- `StarSprite` handles star falling and off-screen respawn; `Game` handles collection scoring.

### Asset loading
- `AssetManager` loads `Surface` data from the `assets/` directory and caches them by file name and size.
- `get_animation()` builds a list of frames for sprite sequences.
- `get_proportional_animation()` scales frames proportionally into a centered transparent canvas, used for coin animation stability.

### Configuration management
- `src/config.py` holds project constants for window size, player movement, animation timing, asset names, coin settings, and UI styling.

### Game state management
- `Game.state` is used as the central state switch for menu, gameplay, pause, options, and game-over flow.
- State transitions are handled in `Game.handle_events()`, `Game.update()`, and `Game.draw()`.

### UI responsibilities
- UI state is rendered in the same `Game` controller rather than a separate game loop or toolchain.
- Buttons are rectangular `pygame.Rect` objects with hover highlighting and click detection.

## 5. Game States

The project currently implements the following states:

- `MENU`
  - Represents the initial title screen with PLAY and QUIT buttons.
  - Entered on startup.
  - Exits when PLAY is selected or when QUIT is chosen.

- `PLAYING`
  - Represents active coin collection gameplay.
  - Entered from `MENU` after PLAY or from `PAUSED` after RESUME.
  - Leaves when ESC pauses the game, when player health reaches zero, or when the game is restarted.

- `PAUSED`
  - Freezes the gameplay update loop while keeping the current session state intact.
  - Entered when `ESC` is pressed during `PLAYING`.
  - Leaves via RESUME or RESTART, or by going into the OPTIONS screen.

- `OPTIONS`
  - Placeholder options screen with a BACK button.
  - Entered from `PAUSED` via the OPTIONS action.
  - Leaves by returning to `PAUSED` through BACK.

- `GAME_OVER`
  - Displays the game-over screen and prevents gameplay updates.
  - Entered when player health reaches zero after bomb collisions.
  - Leaves through RESTART or RETURN TO MAIN MENU.

### State transition diagram

```text
MENU
  ├── PLAY ──> PLAYING
  └── QUIT ──> exit

PLAYING
  ├── ESC ──> PAUSED
  └── health reaches 0 from bomb hits ──> GAME_OVER

PAUSED
  ├── RESUME ──> PLAYING
  ├── RESTART ──> PLAYING (fresh session)
  └── OPTIONS ──> OPTIONS

OPTIONS
  └── BACK ──> PAUSED

GAME_OVER
  ├── RESTART ──> PLAYING (fresh session)
  └── RETURN TO MAIN MENU ──> MENU
```

## 6. Gameplay Systems

### Player
- Movement is horizontal-only and constrained to the screen width.
- The player is anchored near the bottom of the screen using `PLAYER_BOTTOM_OFFSET`.
- The player keeps a facing direction (`facing_right`) and toggles animation accordingly.
- Idle animation frames are loaded from `assets/idle_anim/`.
- Running animation frames are loaded from `assets/Runing/` and used when the player is moving.
- Catch animation frames are loaded from `assets/Catch/` and temporarily override normal animation when a coin is collected.

### Collectibles
- Coin entities are created in `Game._init_entities()` using `AssetManager.get_proportional_animation()`.
- Two coins are active concurrently. Each coin has a downward speed and is respawned at a randomized position above the screen when it passes the bottom or is collected.
- `Game` counts initial coin spawns and respawns. Every 7th coin drop spawns one bomb; every 10th spawns one rare star.
- Coin collision is handled via `pygame.sprite.spritecollide(self.player, self.coins_group, False)`.
- Collection increases score and triggers the catch animation.
- Passing the bottom only respawns the coin and advances the drop counter; it does not reduce health or trigger Game Over.
- Bombs fall from randomized positions above the play area. A bomb collision deals 25 damage and respawns that bomb.
- Stars fall from randomized positions above the play area. Collecting a star adds 10 points and respawns it.

### Score
- `Game.score` starts at `0`.
- Each collected coin increments score by 1.
- The score is rendered in the HUD with `pygame.font.Font` in `Game.draw()`.

### Health
- `Player.health` starts at `PLAYER_MAX_HEALTH = 100`.
- Each bomb impact removes `BOMB_DAMAGE = 25` health; health is clamped at zero.
- Game Over is triggered when health reaches zero. Missed coins do not affect health or game state.
- Health data is implemented on the Player. The HUD displays `HP: X` and a bar filled proportionally to current health.

### Game Over
- The current game-over condition is: `self.player.health <= 0` after bomb damage.
- When triggered, the game stops gameplay updates and renders the `GAME OVER` text plus action buttons.
- Current actions are:
  - RESTART: fresh session, direct return to `PLAYING`
  - RETURN TO MAIN MENU: switch to `MENU`

## 7. UI System

The UI exists inside the same `Game` class and does not use a separate application or second event loop.

- Main Menu: title + PLAY + QUIT; hover highlighting is supported via `pygame.Rect` collisions.
- HUD: score and current HP text render in the gameplay view alongside a health bar that drains in proportion to damage.
- Pause Menu: RESUME, RESTART, and OPTIONS actions; drawn as overlayed menu buttons.
- Options screen: placeholder `OPTIONS` title and a BACK button.
- Game Over screen: `GAME OVER` text plus RESTART and RETURN TO MAIN MENU buttons.
- Restart behavior is implemented in Game reset helpers, not in the entity classes.
- Return-to-menu behavior resets the current gameplay state and returns to `MENU`.

## 8. Animation System

The project uses a state-driven animation system in `Player` rather than a separate animation manager.

- Idle: `PLAYER_FRAME_NAMES` loaded from `assets/idle_anim/`
- Running: `PLAYER_RUN_FRAME_NAMES` loaded from `assets/Runing/`
- Catch: `PLAYER_CATCH_FRAME_NAMES` loaded from `assets/Catch/`
- Animation timing is controlled by `PLAYER_ANIMATION_DELAY` in `src/config.py`.
- `Player.update()` chooses between idle, running, and catch frames based on movement and catch state.
- The catch animation temporarily overrides the normal idle/running animation and resets back to the current normal state when complete.

## 9. Asset Management

`AssetManager` is the asset access layer for the project.

Responsibilities:
- `get_image()` loads a single surface and caches it by filename and size
- `get_animation()` loads a list of frames from a set of filenames
- `get_proportional_animation()` loads images scaled proportionally into a common transparent canvas to preserve collectibles’ visual proportions
- `clear_cache()` clears cached resources when a reload occurs

The cache is stored in `self._image_cache` and is keyed using filename and scaling parameters.

## 10. Configuration

`src/config.py` centralizes all shared settings used by the game and UI.

Important values currently present:

- Window: `DEFAULT_WIDTH`, `DEFAULT_HEIGHT`
- Timing: `FPS`, `PLAYER_ANIMATION_DELAY`, `COIN_ANIMATION_DELAY`
- Player: `PLAYER_SIZE`, `PLAYER_SPEED`, `PLAYER_BOTTOM_OFFSET`
- Coin: `COIN_SIZE`, `COIN_COUNT`, `COINS_PER_BOMB`, `COINS_PER_STAR`
- Player health and hazard values: `PLAYER_MAX_HEALTH`, `BOMB_DAMAGE`, `STAR_VALUE`
- Assets: `ASSETS_DIR`, `ICON_FILE`, `BG_IMAGE_FILE`, player/coin frames, `BOMB_IMAGE_FILE`, `STAR_IMAGE_FILE`
- HUD/UI: `SCORE_FONT_SIZE`, `GAME_OVER_FONT_SIZE`, `HUD_COLOR`, `GAME_OVER_COLOR`, menu button colors and sizes

## 11. Design Patterns / Design Principles

### State-driven controller
- Used in `Game.state` and the state-specific flow inside `Game.handle_events()`, `Game.update()`, and `Game.draw()`.
- Classes involved: `Game`.
- Why it fits: the game is built as a single controller with explicit screen and gameplay states rather than independent sub-apps.

### Sprite-based entity architecture
- Used in `pygame.sprite.Sprite` and `pygame.sprite.Group` for the player and collectibles.
- Classes involved: `Player`, `CoinSprite`, `BombSprite`, `StarSprite`, and their Game-owned sprite groups.
- Why it fits: entity behavior is localized to sprite objects while the game controller manages world state.

### Manager pattern
- Used in `AssetManager` for image and animation loading.
- Classes involved: `AssetManager`.
- Why it fits: asset loading and caching are encapsulated away from gameplay code.

### Separation of concerns
- `Game` manages game-wide state; entity classes keep local behavior; config centralizes constants.
- Why it fits: the code keeps entity logic and game rules separate while preserving a compact project structure.

## 12. APIs and Framework Features Used

Important pygame APIs actually used in the project:

- `pygame.init()`
- `pygame.display.set_mode()` and `pygame.display.set_caption()`
- `pygame.display.update()`
- `pygame.event.get()`
- `pygame.time.Clock`
- `pygame.Surface`
- `pygame.Rect`
- `pygame.sprite.Sprite`
- `pygame.sprite.Group`
- `pygame.sprite.spritecollide()`
- `pygame.transform.scale()` / `pygame.transform.smoothscale()`
- `pygame.font.Font()`

Included Python standard-library modules:

- `pathlib` for asset and project path resolution
- `random` for coin spawn and movement randomness
- `importlib` in `Game.reload_game_state()`
- `subprocess` in `dev.py` for the live-reload launcher
- `time` in `dev.py` for polling and reload timing

## 13. Development Tools

- VS Code: editor environment used for the project and its session work.
- Git: repository versioning and change tracking.
- GitHub: repository hosting and remote workflow.
- GitHub Copilot: used as an AI-assisted development assistant during architecture review, validation, and iterative implementation.
- `jurigged`: optional live-reload tool enabled through `main.py` when the `--live` flag is used.

## 14. Debugging / Development Practices

- Configuration separation: project values are centralized in `src/config.py`.
- Type annotations: present in multiple areas, notably `Player`, `AssetManager`, and `Game` methods.
- Pylance/static analysis: used during code review and issue resolution in the project workflow.
- Hot reload helper: `Game.reload_game_state()` reloads config and assets in-place without restarting the whole app.
- Manual gameplay validation: gameplay behavior is evaluated through the live game loop and visual checks rather than a formal automated test suite.
- Incremental feature development: the project was expanded in stages across menu, pause, catch animation, score, miss tracking, and game-over flow.

## 15. Current Feature Status

- [x] Player movement
- [x] Idle animation
- [x] Running animation
- [x] Coin animation
- [x] Coin collection
- [x] Catch animation
- [x] Score
- [x] Coin spawn tracking
- [x] Bomb drops and damage
- [x] Rare star drops and +10 score
- [x] Player health model
- [x] Game Over
- [x] Main Menu
- [x] Pause Menu
- [x] Options screen
- [x] Restart
- [x] Return to Main Menu
- [x] Persistent High Scores (data/highscores.json)
- [x] Audio Manager (SFX and BGM)
- [x] Godot-style UI Juice (Animated health bars, floating damage numbers, screen shake)
- [x] Delta-Time (dt) based movement and animations
- [x] Combo multiplier system

## 16. Known Limitations / Not Yet Implemented

- [x] Persistent high-score storage (DataManager)
- [x] Audio and music system (AudioManager)
- No difficulty progression or level scaling
- [x] Invulnerability flashing, screen shake, and damage popups (UI Juice)
- No power-ups or additional collectible types beyond coins and the rare star
- No advanced menu art or background image support in the menu system yet
- No real settings implementation beyond a placeholder options screen
- No formal automated test suite currently present in the repository

## 17. Architecture Summary

The project is a compact single-window Pygame application in which `Game` acts as the central controller for state, input, entity updates, and rendering. Player and coin logic are kept in their respective entity classes, while shared values live in `src/config.py` and assets are loaded through `AssetManager`. The current architecture is intentionally lightweight: a small state machine, sprite-based entities, simple HUD/menu rendering, and a direct event-driven game loop without a broader engine abstraction.
