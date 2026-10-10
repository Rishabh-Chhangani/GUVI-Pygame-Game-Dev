# Ninja Collector: Codebase Fix Plan

This document outlines the planned fixes for the architectural and logical errors in the game. For each issue, it explains what is currently wrong (or suboptimal) and how it will be implemented better.

## 1. Frame-rate Dependent Movement (Missing `dt`)
* **What is wrong:** The game caps the framerate using `clock.tick(FPS)`, but entities move by a fixed amount of pixels per frame (e.g., `speed = 6`). If the computer lags or the FPS cap changes, the game will run slower or faster.
* **The Fix:**
  1. In `Game.run()`, calculate Delta Time: `dt = self.clock.tick(config.FPS) / 1000.0` (converting milliseconds to seconds).
  2. Pass `dt` to all `update()` methods (e.g., `self.player.update(dt)`).
  3. Change the speed constants in `config.py` from pixels-per-frame to pixels-per-second (e.g., `PLAYER_SPEED = 6` becomes `360`).
  4. Multiply all movement by `dt` (e.g., `pos_y += speed * dt`).

## 2. Infinite Bomb & Star Accumulation (Memory/Logic Bug)
* **What is wrong:** Every 7 coins, a brand new Bomb is created and added to the `bombs_group`. However, when existing bombs fall off the screen, they call `reset()` and teleport back to the top. Because they never die, the number of bombs on screen grows infinitely.
* **The Fix:** 
  1. Modify `BombSprite` and `StarSprite` to call `self.kill()` when they go off the bottom of the screen instead of `self.reset()`.
  2. Modify collision logic in `Game.update()` to kill bombs/stars upon collision instead of resetting them. The spawner (`_spawn_bomb`) will handle introducing new hazards.

## 3. Sub-pixel Precision Loss in Player Movement
* **What is wrong:** `player.py` updates its position directly into `self.rect.x` (an integer). When moving using fractional speeds (which will happen when we add `dt`), the fractional part is truncated, causing jittery or snapped movement.
* **The Fix:** 
  1. Add `self.pos_x = float(x)` to the `Player` class (similar to how `CoinSprite` uses `self.pos_y`).
  2. Update `self.pos_x += speed * direction * dt`.
  3. Assign back to the rect using `self.rect.x = round(self.pos_x)`.

## 4. Animation Timing Desync During Pauses
* **What is wrong:** Animations are driven by `pygame.time.get_ticks()`. If the player pauses the game for 5 minutes, `get_ticks()` keeps counting. When unpaused, the animation logic glitches momentarily as it catches up.
* **The Fix:** 
  1. Replace `get_ticks()` in entities with an internal `self.animation_timer = 0.0`.
  2. In the `update(dt)` method, add `dt` to the timer: `self.animation_timer += dt`. 
  3. When the timer exceeds the animation delay, advance the frame and subtract the delay. This ensures animations only play when the game is actively running.

## 5. UI and Input Architecture Coupling
* **What is wrong/suboptimal:** The `Player` entity currently calls `pygame.key.get_pressed()` directly. It's generally better for the `Game` state to read inputs and pass the intent (e.g., left or right) down to the player.
* **The Fix:** 
  1. In `Game.update()`, read `keys = pygame.key.get_pressed()`.
  2. Pass `keys` to `self.player.update(keys, dt)` so the player entity strictly handles kinematics based on input state provided to it.

## 6. Hardcoded Spawning Heights
* **What is wrong/suboptimal:** `CoinSprite.reset()` and `Game._spawn_bomb()` independently hardcode values like `-random.randint(50, 400)` to figure out where to spawn.
* **The Fix:** Centralize spawning coordinates to ensure items don't overlap awkwardly and to clean up magic numbers from the codebase.
