import importlib
import random

import pygame

import src.config as config
from src.asset_manager import AssetManager
from src.entities.spawner import Spawner
from src.ui.hud import HUD
from src.ui.juice import DamagePopup
from src.data_manager import DataManager
from src.audio_manager import AudioManager
from src.entities.particles import ParticleSystem
import src.entities.player as player_module
import src.entities.coin as coin_module
import src.entities.bomb as bomb_module
import src.entities.star as star_module


class Game:

    """Main Game Engine managing lifecycle, systems, events, and rendering."""

    def __init__(self):
        pygame.init()

        # Display Setup
        self.width: int = config.DEFAULT_WIDTH
        self.height: int = config.DEFAULT_HEIGHT
        self.is_resizable = True
        self.window : pygame.Surface = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.width, self.height = self.window.get_size()
        pygame.display.set_caption(config.CAPTION)

        # Asset Manager
        self.assets = AssetManager()

        # Set Window Icon
        icon_surface = self.assets.get_image(config.ICON_FILE, size=None)
        pygame.display.set_icon(icon_surface)

        # Load and scale background
        self.bg_raw: pygame.Surface = self.assets.get_image(config.BG_IMAGE_FILE, size=None)
        self.bg_image: pygame.Surface = pygame.transform.scale(self.bg_raw, (self.width, self.height))

        # Timing
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"
        self.score = 0
        self.coin_drop_count = 0
        self.bomb_drop_count = 0
        self.star_drop_count = 0
        self.coins_since_bomb = 0
        self.coins_since_star = 0
        self.score_font = pygame.font.Font(config.FONT_FILE, config.SCORE_FONT_SIZE)
        self.game_over_font = pygame.font.Font(config.FONT_FILE, config.GAME_OVER_FONT_SIZE)
        self.menu_title_font = pygame.font.Font(config.FONT_FILE, config.MENU_TITLE_FONT_SIZE)
        self.menu_button_font = pygame.font.Font(config.FONT_FILE, config.MENU_BUTTON_FONT_SIZE)
        self.hud = HUD(self.score_font)
        self.data_manager = DataManager(config.ROOT_DIR / "data")
        self.audio_manager = AudioManager(config.ASSETS_DIR)
        self.audio_manager.play_bgm()
        self.popups: list[DamagePopup] = []
        self.particle_system = ParticleSystem()
        self.camera_shake = 0.0
        self.high_score = self.data_manager.high_score

        # Menu UI
        self.play_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.quit_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.resume_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.restart_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.options_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.back_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.game_over_restart_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.game_over_menu_button_rect = pygame.Rect(0, 0, 260, config.MENU_BUTTON_HEIGHT)
        self._layout_menu_buttons()
        self._layout_pause_buttons()
        self._layout_options_buttons()
        self._layout_game_over_buttons()

        # Initialize Entities
        self._init_entities()

    def _init_entities(self):
        """Instantiates all player and world sprite entities."""
        # Player
        player_frames = self.assets.get_animation(config.PLAYER_FRAME_NAMES, size=config.PLAYER_SIZE)
        player_running_frames = self.assets.get_animation(
            config.PLAYER_RUN_FRAME_NAMES,
            size=config.PLAYER_SIZE,
        )
        player_catch_frames = self.assets.get_animation(
            config.PLAYER_CATCH_FRAME_NAMES,
            size=config.PLAYER_SIZE,
        )
        self.player: player_module.Player = player_module.Player(
            frames=player_frames,
            running_frames=player_running_frames,
            catch_frames=player_catch_frames,
            x=self.width // 2 - config.PLAYER_SIZE[0] // 2,
            y=self.height - config.PLAYER_SIZE[1] - config.PLAYER_BOTTOM_OFFSET,
            size=config.PLAYER_SIZE,
            speed=config.PLAYER_SPEED,
            bottom_offset=config.PLAYER_BOTTOM_OFFSET
        )

        # Load collectible and hazard assets through AssetManager.
        self.coin_frames = self.assets.get_proportional_animation(
            config.COIN_FRAME_NAMES,
            target_box=config.COIN_SIZE,
        )
        self.bomb_image = self.assets.get_image(
            config.BOMB_IMAGE_FILE,
            size=config.BOMB_SIZE,
            smooth=True,
        )
        self.star_image = self.assets.get_image(
            config.STAR_IMAGE_FILE,
            size=config.STAR_SIZE,
            smooth=True,
        )

        self.coins_group: pygame.sprite.Group[coin_module.CoinSprite] = pygame.sprite.Group()
        self.all_sprites: pygame.sprite.Group[coin_module.CoinSprite] = self.coins_group
        self.bombs_group: pygame.sprite.Group[bomb_module.BombSprite] = pygame.sprite.Group()
        self.stars_group: pygame.sprite.Group[star_module.StarSprite] = pygame.sprite.Group()
        self.spawner = Spawner(
            coin_group=self.coins_group,
            bomb_group=self.bombs_group,
            star_group=self.stars_group,
            coin_frames=self.coin_frames,
            bomb_image=self.bomb_image,
            star_image=self.star_image,
        )

        # Spawn initial coins staggered across screen
        self.spawner.spawn_initial_coins(self.width)
        self.particle_system.particles.clear()

    def _spawn_coin(self, x: int, y: int, speed: float) -> None:
        """Creates a coin and triggers rare drops at configured coin milestones."""
        coin = coin_module.CoinSprite(self.coin_frames, x, y, speed=speed)
        self.coins_group.add(coin)
        self._register_coin_drop()

    def _spawn_game_coin(self) -> None:
        """Uses the spawner to generate a coin from the top of the play area."""
        self.spawner.spawn_coin(self.width)
        self._register_coin_drop()

    def _register_coin_drop(self) -> None:
        """Tracks coin drops and triggers hazards at repeating coin intervals."""
        self.coin_drop_count += 1
        self.coins_since_bomb += 1
        self.coins_since_star += 1

        if self.coins_since_bomb >= config.COINS_PER_BOMB:
            self.coins_since_bomb = 0
            self._spawn_bomb()
        if self.coins_since_star >= config.COINS_PER_STAR:
            self.coins_since_star = 0
            self._spawn_star()

    def _spawn_bomb(self) -> None:
        """Drops a bomb from a randomized position above the play area."""
        self.spawner.spawn_bomb(self.width)
        self.bomb_drop_count += 1

    def _spawn_star(self) -> None:
        """Drops a rare, ten-point star from above the play area."""
        self.spawner.spawn_star(self.width)
        self.star_drop_count += 1

    def reload_game_state(self):
        """Hot-reloads configuration, assets, and entities live without restarting."""
        try:
            importlib.reload(config)
            importlib.reload(player_module)
            importlib.reload(coin_module)
            self.assets.clear_cache()

            # Refresh background
            self.bg_raw = self.assets.get_image(config.BG_IMAGE_FILE, size=None)
            self.bg_image = pygame.transform.scale(self.bg_raw, (self.width, self.height))

            # Re-initialize entities with fresh values
            self._init_entities()
            print("[⚡ HOT-RELOAD] Config, assets, and entities reloaded successfully!")
        except Exception as e:
            print(f"[HOT-RELOAD ERROR] Could not reload game state: {e}")

    def _layout_menu_buttons(self):
        """Positions the main menu buttons based on the current window size."""
        self.play_button_rect.center = (self.width // 2, self.height // 2 + 30)
        self.quit_button_rect.center = (self.width // 2, self.height // 2 + 30 + config.MENU_BUTTON_HEIGHT + config.MENU_BUTTON_SPACING)

    def _layout_pause_buttons(self):
        """Positions pause menu buttons."""
        self.resume_button_rect.center = (self.width // 2, self.height // 2 - 40)
        self.restart_button_rect.center = (self.width // 2, self.height // 2 + 40)
        self.options_button_rect.center = (self.width // 2, self.height // 2 + 120)

    def _layout_options_buttons(self):
        """Positions options screen buttons."""
        self.back_button_rect.center = (self.width // 2, self.height // 2 + 80)

    def _layout_game_over_buttons(self):
        """Positions the buttons displayed under the game over text."""
        self.game_over_restart_button_rect.center = (self.width // 2, self.height // 2 + 100)
        self.game_over_menu_button_rect.center = (self.width // 2, self.height // 2 + 100 + config.MENU_BUTTON_HEIGHT + config.MENU_BUTTON_SPACING)

    def _handle_menu_click(self, mouse_pos: tuple[int, int]) -> None:
        """Handles main menu button interactions."""
        if self.play_button_rect.collidepoint(mouse_pos):
            self._start_game_play()
        elif self.quit_button_rect.collidepoint(mouse_pos):
            self.running = False

    def _handle_pause_click(self, mouse_pos: tuple[int, int]) -> None:
        """Handles pause menu button interactions."""
        if self.resume_button_rect.collidepoint(mouse_pos):
            self.state = "PLAYING"
        elif self.restart_button_rect.collidepoint(mouse_pos):
            self._restart_playing_session()
        elif self.options_button_rect.collidepoint(mouse_pos):
            self.state = "OPTIONS"

    def _handle_options_click(self, mouse_pos: tuple[int, int]) -> None:
        """Handles options screen button interactions."""
        if self.back_button_rect.collidepoint(mouse_pos):
            self.state = "PAUSED"

    def _handle_game_over_click(self, mouse_pos: tuple[int, int]) -> None:
        """Handles game-over screen button interactions."""
        if self.game_over_restart_button_rect.collidepoint(mouse_pos):
            self._restart_playing_session()
        elif self.game_over_menu_button_rect.collidepoint(mouse_pos):
            self._return_to_menu()

    def _start_game_play(self):
        """Resets gameplay and enters the PLAYING state."""
        self.score = 0
        self.coin_drop_count = 0
        self.bomb_drop_count = 0
        self.star_drop_count = 0
        self.coins_since_bomb = 0
        self.coins_since_star = 0
        self.state = "PLAYING"
        self._init_entities()

    def _restart_playing_session(self):
        """Reinitializes the current session and starts playing immediately."""
        self.score = 0
        self.coin_drop_count = 0
        self.bomb_drop_count = 0
        self.star_drop_count = 0
        self.coins_since_bomb = 0
        self.coins_since_star = 0
        self.state = "PLAYING"
        self._init_entities()

    def _return_to_menu(self):
        """Resets the current gameplay session and returns to the menu."""
        self.score = 0
        self.coin_drop_count = 0
        self.bomb_drop_count = 0
        self.star_drop_count = 0
        self.coins_since_bomb = 0
        self.coins_since_star = 0
        self.state = "MENU"
        self._init_entities()

    def handle_events(self):
        """Processes OS and user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                if self.is_resizable:
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self._sync_drawable_size()
                    self._layout_menu_buttons()
                    self._layout_pause_buttons()
                    self._layout_options_buttons()
                    self._layout_game_over_buttons()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "PLAYING":
                        self.state = "PAUSED"
                    elif self.state == "PAUSED":
                        self.state = "PLAYING"
                    elif self.state == "OPTIONS":
                        self.state = "PAUSED"
                elif event.key == pygame.K_r:
                    self.is_resizable = not self.is_resizable
                    mode_flag = pygame.RESIZABLE if self.is_resizable else 0
                    self.window = pygame.display.set_mode((self.width, self.height), mode_flag)
                    self._sync_drawable_size()
                    self._layout_menu_buttons()
                    self._layout_pause_buttons()
                    self._layout_options_buttons()
                    self._layout_game_over_buttons()
                elif event.key == pygame.K_F5:
                    self.reload_game_state()
                elif event.key == pygame.K_m:
                    self.audio_manager.toggle_mute()
                elif self.state == "MENU" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._start_game_play()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "MENU":
                    self._handle_menu_click(event.pos)
                elif self.state == "PAUSED":
                    self._handle_pause_click(event.pos)
                elif self.state == "OPTIONS":
                    self._handle_options_click(event.pos)
                elif self.state == "GAME_OVER":
                    self._handle_game_over_click(event.pos)

    def _sync_drawable_size(self) -> None:
        """Keeps game dimensions aligned with the active display surface."""
        drawable_size: tuple[int, int] = self.window.get_size()
        if drawable_size != (self.width, self.height):
            self.width, self.height = drawable_size
            self.bg_image = pygame.transform.scale(self.bg_raw, drawable_size)

    def update(self, dt: float = 1 / 60):
        """Updates game state, kinematics, and collisions."""
        self._sync_drawable_size()

        if self.state != "PLAYING":
            return

        if self.player.health <= 0:
            self.state = "GAME_OVER"
            self.audio_manager.play_sfx("game_over")
            if self.data_manager.save_high_score(self.score):
                self.high_score = self.score
            return

        self.hud.update(dt, self.player.health)
        if self.camera_shake > 0:
            self.camera_shake = max(0.0, self.camera_shake - 60.0 * dt)
        for popup in self.popups:
            popup.update(dt)
        self.popups = [p for p in self.popups if p.timer > 0]

        self.particle_system.update(dt)

        # Keep coin spawns and milestone drops coordinated in the Game layer.
        for coin in list(self.coins_group):
            coin.update(self.width, self.height, dt)
            if coin.respawned_this_update:
                self._register_coin_drop()

        for bomb in list(self.bombs_group):
            bomb.update(self.width, self.height, dt)
        for star in list(self.stars_group):
            star.update(self.width, self.height, dt)

        # Update player position and animation
        self.player.update(self.width, self.height, dt)

        # Collision detection: When player collects a coin, coin disappears and respawns from top
        collected_coins = pygame.sprite.spritecollide(self.player, self.coins_group, False)
        if collected_coins:
            self.player.record_coin_pickup(dt)
            self.score += sum(coin.value for coin in collected_coins) * self.player.get_combo_multiplier()
            self.player.start_catch()
            for coin in collected_coins:
                assert coin.rect is not None
                self.particle_system.emit_coin_sparkles(coin.rect.centerx, coin.rect.centery)
                coin.reset(self.width)
                self.popups.append(DamagePopup(coin.rect.centerx, coin.rect.top, "+1", (255, 215, 0)))
                self.audio_manager.play_sfx("coin")
                self._register_coin_drop()

        collected_stars = pygame.sprite.spritecollide(self.player, self.stars_group, False)
        for star in collected_stars:
            assert star.rect is not None
            self.score += config.STAR_VALUE
            self.particle_system.emit_coin_sparkles(star.rect.centerx, star.rect.centery, count=20)
            star.kill()
            self.popups.append(DamagePopup(star.rect.centerx, star.rect.top, f"+{config.STAR_VALUE}", (0, 255, 255)))
            self.audio_manager.play_sfx("coin")

        hit_bombs = pygame.sprite.spritecollide(self.player, self.bombs_group, False)
        for bomb in hit_bombs:
            assert bomb.rect is not None
            if self.player.take_damage(config.BOMB_DAMAGE):
                self.particle_system.emit_bomb_shrapnel(bomb.rect.centerx, bomb.rect.centery)
                bomb.kill()
                self.camera_shake = 15.0
                self.popups.append(DamagePopup(bomb.rect.centerx, bomb.rect.top, f"-{config.BOMB_DAMAGE}", (255, 50, 50)))
                self.audio_manager.play_sfx("hit")
            if self.player.health <= 0:
                self.state = "GAME_OVER"
                self.audio_manager.play_sfx("game_over")
                if self.data_manager.save_high_score(self.score):
                    self.high_score = self.score
                break

    def _draw_main_menu(self):
        """Draws the main menu screen."""
        self.window.fill(config.MENU_BACKGROUND_COLOR)

        title_surface = self.menu_title_font.render("Ninja Collector", True, config.MENU_TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 2 - 120))
        self.window.blit(title_surface, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        play_button_color = config.MENU_BUTTON_HOVER_COLOR if self.play_button_rect.collidepoint(mouse_pos) else config.MENU_BUTTON_COLOR
        quit_button_color = config.MENU_BUTTON_HOVER_COLOR if self.quit_button_rect.collidepoint(mouse_pos) else config.MENU_BUTTON_COLOR

        pygame.draw.rect(self.window, play_button_color, self.play_button_rect, border_radius=10)
        pygame.draw.rect(self.window, quit_button_color, self.quit_button_rect, border_radius=10)

        play_label = self.menu_button_font.render("PLAY", True, config.MENU_BUTTON_TEXT_COLOR)
        quit_label = self.menu_button_font.render("QUIT", True, config.MENU_BUTTON_TEXT_COLOR)

        self.window.blit(play_label, play_label.get_rect(center=self.play_button_rect.center))
        self.window.blit(quit_label, quit_label.get_rect(center=self.quit_button_rect.center))

    def _draw_pause_menu(self):
        """Draws the pause overlay and available actions."""
        offset_x, offset_y = 0, 0
        if self.camera_shake > 0:
            offset_x = random.uniform(-self.camera_shake, self.camera_shake)
            offset_y = random.uniform(-self.camera_shake, self.camera_shake)

        self.window.blit(self.bg_image, (int(offset_x), int(offset_y)))
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.window.blit(overlay, (0, 0))

        title_surface = self.menu_title_font.render("PAUSED", True, config.MENU_TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 2 - 120))
        self.window.blit(title_surface, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        resume_color = config.MENU_BUTTON_HOVER_COLOR if self.resume_button_rect.collidepoint(mouse_pos) else config.MENU_BUTTON_COLOR
        restart_color = config.MENU_BUTTON_HOVER_COLOR if self.restart_button_rect.collidepoint(mouse_pos) else config.MENU_BUTTON_COLOR
        options_color = config.MENU_BUTTON_HOVER_COLOR if self.options_button_rect.collidepoint(mouse_pos) else config.MENU_BUTTON_COLOR

        pygame.draw.rect(self.window, resume_color, self.resume_button_rect, border_radius=10)
        pygame.draw.rect(self.window, restart_color, self.restart_button_rect, border_radius=10)
        pygame.draw.rect(self.window, options_color, self.options_button_rect, border_radius=10)

        resume_label = self.menu_button_font.render("RESUME", True, config.MENU_BUTTON_TEXT_COLOR)
        restart_label = self.menu_button_font.render("RESTART", True, config.MENU_BUTTON_TEXT_COLOR)
        options_label = self.menu_button_font.render("OPTIONS", True, config.MENU_BUTTON_TEXT_COLOR)

        self.window.blit(resume_label, resume_label.get_rect(center=self.resume_button_rect.center))
        self.window.blit(restart_label, restart_label.get_rect(center=self.restart_button_rect.center))
        self.window.blit(options_label, options_label.get_rect(center=self.options_button_rect.center))

    def _draw_options_menu(self):
        """Draws the options screen."""
        offset_x, offset_y = 0, 0
        if self.camera_shake > 0:
            offset_x = random.uniform(-self.camera_shake, self.camera_shake)
            offset_y = random.uniform(-self.camera_shake, self.camera_shake)

        self.window.blit(self.bg_image, (int(offset_x), int(offset_y)))
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.window.blit(overlay, (0, 0))

        title_surface = self.menu_title_font.render("OPTIONS", True, config.MENU_TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 2 - 80))
        self.window.blit(title_surface, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        back_color = config.MENU_BUTTON_HOVER_COLOR if self.back_button_rect.collidepoint(mouse_pos) else config.MENU_BUTTON_COLOR
        pygame.draw.rect(self.window, back_color, self.back_button_rect, border_radius=10)

        back_label = self.menu_button_font.render("BACK", True, config.MENU_BUTTON_TEXT_COLOR)
        self.window.blit(back_label, back_label.get_rect(center=self.back_button_rect.center))

    def draw(self):
        """Renders all game layers to the active window."""
        if self.state == "MENU":
            self._draw_main_menu()
            pygame.display.update()
            return

        if self.state == "PAUSED":
            self._draw_pause_menu()
            pygame.display.update()
            return

        if self.state == "OPTIONS":
            self._draw_options_menu()
            pygame.display.update()
            return

        offset_x, offset_y = 0, 0
        if self.camera_shake > 0:
            offset_x = random.uniform(-self.camera_shake, self.camera_shake)
            offset_y = random.uniform(-self.camera_shake, self.camera_shake)

        self.window.blit(self.bg_image, (int(offset_x), int(offset_y)))
        self.particle_system.draw(self.window)
        self.all_sprites.draw(self.window)
        self.bombs_group.draw(self.window)
        self.stars_group.draw(self.window)
        self.player.draw(self.window)

        self.hud.draw(self.window, self.score, self.player.health, self.player.max_health)
        for popup in self.popups:
            popup.draw(self.window)

        if self.state == "GAME_OVER":
            game_over_surface = self.game_over_font.render("GAME OVER", True, config.GAME_OVER_COLOR)
            game_over_rect = game_over_surface.get_rect(center=(self.width // 2, self.height // 2 - 60))
            self.window.blit(game_over_surface, game_over_rect)

            mouse_pos = pygame.mouse.get_pos()
            restart_color = config.MENU_BUTTON_HOVER_COLOR if self.game_over_restart_button_rect.collidepoint(mouse_pos) else config.MENU_BUTTON_COLOR
            menu_color = config.MENU_BUTTON_HOVER_COLOR if self.game_over_menu_button_rect.collidepoint(mouse_pos) else config.MENU_BUTTON_COLOR

            pygame.draw.rect(self.window, restart_color, self.game_over_restart_button_rect, border_radius=10)
            pygame.draw.rect(self.window, menu_color, self.game_over_menu_button_rect, border_radius=10)

            restart_label = self.menu_button_font.render("RESTART", True, config.MENU_BUTTON_TEXT_COLOR)
            menu_label = self.menu_button_font.render("RETURN TO MAIN MENU", True, config.MENU_BUTTON_TEXT_COLOR)

            self.window.blit(restart_label, restart_label.get_rect(center=self.game_over_restart_button_rect.center))
            self.window.blit(menu_label, menu_label.get_rect(center=self.game_over_menu_button_rect.center))

        pygame.display.update()

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
