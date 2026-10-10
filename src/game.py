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
        self._state = "MENU"
        self.score = 0
        self.coin_drop_count = 0
        self.bomb_drop_count = 0
        self.star_drop_count = 0
        self.coins_since_bomb = 0
        self.coins_since_star = 0
        self.coins_since_magnet = 0
        self.difficulty_multiplier = 1.0
        self.survival_time = 0.0
        self.score_font = pygame.font.Font(config.FONT_FILE, config.SCORE_FONT_SIZE)
        self.game_over_font = pygame.font.Font(config.FONT_FILE, config.GAME_OVER_FONT_SIZE)
        self.menu_title_font = pygame.font.Font(config.FONT_FILE, config.MENU_TITLE_FONT_SIZE)
        self.menu_button_font = pygame.font.Font(config.FONT_FILE, config.MENU_BUTTON_FONT_SIZE)
        self.hud = HUD(self.score_font)
        self.data_manager = DataManager(config.USER_DATA_DIR)
        self.audio_manager = AudioManager(config.ASSETS_DIR)
        self.audio_manager.play_bgm()
        self.popups: list[DamagePopup] = []
        self.particle_system = ParticleSystem()
        self.camera_shake = 0.0
        self.high_score = self.data_manager.high_score

        from src.scenes.manager import SceneManager
        from src.scenes.menu import MenuScene
        from src.scenes.play import PlayScene
        from src.scenes.pause import PauseScene
        from src.scenes.game_over import GameOverScene
        from src.scenes.options import OptionsScene
        from src.scenes.leaderboard import LeaderboardScene

        self.scenes = {
            "MENU": MenuScene(self),
            "PLAYING": PlayScene(self),
            "PAUSED": PauseScene(self),
            "GAME_OVER": GameOverScene(self),
            "OPTIONS": OptionsScene(self),
            "LEADERBOARD": LeaderboardScene(self)
        }
        self.scene_manager = SceneManager(self.scenes["MENU"])

        # Load UI Button Images
        self.btn_normal_img = pygame.image.load(config.ASSETS_DIR / "UI" / "Button" / "Blue Button" / "blue_button00.png").convert_alpha()
        self.btn_normal_img = pygame.transform.scale(self.btn_normal_img, (config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT))
        self.btn_hover_img = pygame.image.load(config.ASSETS_DIR / "UI" / "Button" / "Blue Button" / "blue_button04.png").convert_alpha()
        self.btn_hover_img = pygame.transform.scale(self.btn_hover_img, (config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT))

        # Menu UI
        self.play_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.leaderboard_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.quit_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.resume_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.restart_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.options_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.back_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.option_bgm_button_rect = pygame.Rect(0, 0, 260, config.MENU_BUTTON_HEIGHT)
        self.option_sfx_button_rect = pygame.Rect(0, 0, 260, config.MENU_BUTTON_HEIGHT)
        self.option_reset_button_rect = pygame.Rect(0, 0, 260, config.MENU_BUTTON_HEIGHT)
        self.leaderboard_back_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.leaderboard_reset_button_rect = pygame.Rect(0, 0, 260, config.MENU_BUTTON_HEIGHT)
        self.game_over_restart_button_rect = pygame.Rect(0, 0, config.MENU_BUTTON_WIDTH, config.MENU_BUTTON_HEIGHT)
        self.game_over_menu_button_rect = pygame.Rect(0, 0, 220, config.MENU_BUTTON_HEIGHT)

        self.btn_menu_normal_img = pygame.transform.scale(self.btn_normal_img, (220, config.MENU_BUTTON_HEIGHT))
        self.btn_menu_hover_img = pygame.transform.scale(self.btn_hover_img, (220, config.MENU_BUTTON_HEIGHT))
        self.btn_wide_normal_img = pygame.transform.scale(self.btn_normal_img, (260, config.MENU_BUTTON_HEIGHT))
        self.btn_wide_hover_img = pygame.transform.scale(self.btn_hover_img, (260, config.MENU_BUTTON_HEIGHT))

        # Sliders
        from src.ui.slider import Slider
        track_img = self.assets.get_image("UI/Controls/Indicators/grey_sliderHorizontal.png", size=None)
        thumb_img = self.assets.get_image("UI/Controls/Sliders/blue_sliderDown.png", size=None)
        self.bgm_slider = Slider(0, 0, 180, track_img, thumb_img, initial_value=self.audio_manager.bgm_volume)
        self.sfx_slider = Slider(0, 0, 180, track_img, thumb_img, initial_value=self.audio_manager.sfx_volume)

        self._layout_menu_buttons()
        self._layout_pause_buttons()
        self._layout_options_buttons()
        self._layout_game_over_buttons()
        self._layout_leaderboard_buttons()

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
        self.magnet_image = self.assets.get_image(
            config.MAGNET_IMAGE_FILE,
            size=config.MAGNET_SIZE,
            smooth=True,
        )

        self.coins_group: pygame.sprite.Group[coin_module.CoinSprite] = pygame.sprite.Group()
        self.all_sprites: pygame.sprite.Group[coin_module.CoinSprite] = self.coins_group
        self.bombs_group: pygame.sprite.Group[bomb_module.BombSprite] = pygame.sprite.Group()
        self.stars_group: pygame.sprite.Group[star_module.StarSprite] = pygame.sprite.Group()
        from src.entities.magnet import MagnetSprite
        self.magnets_group: pygame.sprite.Group[MagnetSprite] = pygame.sprite.Group()
        
        self.spawner = Spawner(
            coin_group=self.coins_group,
            bomb_group=self.bombs_group,
            star_group=self.stars_group,
            coin_frames=self.coin_frames,
            bomb_image=self.bomb_image,
            star_image=self.star_image,
            magnet_group=self.magnets_group,
            magnet_image=self.magnet_image,
        )

        # Spawn initial coins staggered across screen
        self.spawner.spawn_initial_coins(self.width)
        self.particle_system.particles.clear()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        if hasattr(self, 'scene_manager') and new_state in self.scenes:
            self.scene_manager.switch_to(self.scenes[new_state])

    def get_difficulty(self) -> float:
        """Returns the current difficulty multiplier based on survival without bomb hits."""
        return self.difficulty_multiplier

    def _spawn_coin(self, x: int, y: int, speed: float) -> None:
        """Creates a coin and triggers rare drops at configured coin milestones."""
        coin = coin_module.CoinSprite(self.coin_frames, x, y, speed=speed * self.get_difficulty())
        self.coins_group.add(coin)
        self._register_coin_drop()

    def _spawn_game_coin(self) -> None:
        """Uses the spawner to generate a coin from the top of the play area."""
        self.spawner.spawn_coin(self.width, difficulty=self.get_difficulty())
        self._register_coin_drop()

    def _register_coin_drop(self) -> None:
        """Tracks coin drops and triggers hazards at repeating coin intervals."""
        self.coin_drop_count += 1
        self.coins_since_bomb += 1
        self.coins_since_star += 1
        self.coins_since_magnet += 1

        if self.coins_since_bomb >= config.COINS_PER_BOMB:
            self.coins_since_bomb = 0
            self._spawn_bomb()
        if self.coins_since_star >= config.COINS_PER_STAR:
            self.coins_since_star = 0
            self._spawn_star()
        if self.coins_since_magnet >= config.COINS_PER_MAGNET:
            self.coins_since_magnet = 0
            self._spawn_magnet()

    def _spawn_bomb(self) -> None:
        """Drops a bomb from a randomized position above the play area."""
        self.spawner.spawn_bomb(self.width, difficulty=self.get_difficulty())
        self.bomb_drop_count += 1

    def _spawn_star(self) -> None:
        """Drops a rare, ten-point star from above the play area."""
        self.spawner.spawn_star(self.width, difficulty=self.get_difficulty())
        self.star_drop_count += 1

    def _spawn_magnet(self) -> None:
        """Drops a magnet power-up from above the play area."""
        self.spawner.spawn_magnet(self.width, difficulty=self.get_difficulty())

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
        self.play_button_rect.center = (self.width // 2, self.height // 2 - 10)
        self.leaderboard_button_rect.center = (self.width // 2, self.height // 2 - 10 + config.MENU_BUTTON_HEIGHT + config.MENU_BUTTON_SPACING)
        self.quit_button_rect.center = (self.width // 2, self.height // 2 - 10 + (config.MENU_BUTTON_HEIGHT + config.MENU_BUTTON_SPACING) * 2)

    def _layout_pause_buttons(self):
        """Positions pause menu buttons."""
        self.resume_button_rect.center = (self.width // 2, self.height // 2 - 40)
        self.restart_button_rect.center = (self.width // 2, self.height // 2 + 40)
        self.options_button_rect.center = (self.width // 2, self.height // 2 + 120)

    def _layout_options_buttons(self):
        """Positions options screen buttons and sliders."""
        bgm_label = self.menu_button_font.render("BGM: 100%", True, config.MENU_BUTTON_TEXT_COLOR)
        sfx_label = self.menu_button_font.render("SFX: 100%", True, config.MENU_BUTTON_TEXT_COLOR)
        
        spacing = 20
        total_bgm_w = bgm_label.get_width() + spacing + self.bgm_slider.rect.width
        total_sfx_w = sfx_label.get_width() + spacing + self.sfx_slider.rect.width
        
        bgm_start_x = (self.width - total_bgm_w) // 2
        sfx_start_x = (self.width - total_sfx_w) // 2
        
        self.bgm_slider.rect.left = bgm_start_x + bgm_label.get_width() + spacing
        self.bgm_slider.rect.top = self.height // 2 - 20
        self.bgm_slider.update_thumb_pos()

        self.sfx_slider.rect.left = sfx_start_x + sfx_label.get_width() + spacing
        self.sfx_slider.rect.top = self.height // 2 + 50
        self.sfx_slider.update_thumb_pos()

        self.option_reset_button_rect.center = (self.width // 2, self.height // 2 + 130)
        self.back_button_rect.center = (self.width // 2, self.height // 2 + 200)

    def _layout_leaderboard_buttons(self):
        """Positions leaderboard screen buttons."""
        self.leaderboard_reset_button_rect.center = (self.width // 2 - 140, self.height - 80)
        self.leaderboard_back_button_rect.center = (self.width // 2 + 140, self.height - 80)

    def _layout_game_over_buttons(self):
        """Positions the buttons displayed under the game over text."""
        self.game_over_restart_button_rect.center = (self.width // 2, self.height // 2 + 100)
        self.game_over_menu_button_rect.center = (self.width // 2, self.height // 2 + 100 + config.MENU_BUTTON_HEIGHT + config.MENU_BUTTON_SPACING)

    def _handle_menu_click(self, mouse_pos: tuple[int, int]) -> None:
        """Handles main menu button interactions."""
        if self.play_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self._start_game_play()
        elif self.leaderboard_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self.state = "LEADERBOARD"
        elif self.quit_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self.running = False

    def _handle_pause_click(self, mouse_pos: tuple[int, int]) -> None:
        """Handles pause menu button interactions."""
        if self.resume_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self.state = "PLAYING"
        elif self.restart_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self._restart_playing_session()
        elif self.options_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self.state = "OPTIONS"

    def _handle_options_click(self, mouse_pos: tuple[int, int]) -> None:
        """Handles options screen button interactions."""
        if self.back_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self.state = "PAUSED"
        elif self.option_reset_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self.data_manager.reset_data()
            self.high_score = 0

    def _handle_leaderboard_click(self, mouse_pos: tuple[int, int]) -> None:
        """Handles leaderboard screen button interactions."""
        if self.leaderboard_back_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self.state = "MENU"
        elif self.leaderboard_reset_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self.data_manager.reset_data()
            self.high_score = 0

    def _handle_game_over_click(self, mouse_pos: tuple[int, int]) -> None:
        """Handles game-over screen button interactions."""
        if self.game_over_restart_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self._restart_playing_session()
        elif self.game_over_menu_button_rect.collidepoint(mouse_pos):
            self.audio_manager.play_sfx("click")
            self._return_to_menu()

    def _start_game_play(self):
        """Resets gameplay and enters the PLAYING state."""
        self.score = 0
        self.coin_drop_count = 0
        self.bomb_drop_count = 0
        self.star_drop_count = 0
        self.coins_since_bomb = 0
        self.coins_since_star = 0
        self.coins_since_magnet = 0
        self.difficulty_multiplier = 1.0
        self.survival_time = 0.0
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
        self.coins_since_magnet = 0
        self.difficulty_multiplier = 1.0
        self.survival_time = 0.0
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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.is_resizable = not self.is_resizable
                mode_flag = pygame.RESIZABLE if self.is_resizable else 0
                self.window = pygame.display.set_mode((self.width, self.height), mode_flag)
                self._sync_drawable_size()
                self._layout_menu_buttons()
                self._layout_pause_buttons()
                self._layout_options_buttons()
                self._layout_game_over_buttons()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
                self.reload_game_state()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.audio_manager.toggle_mute()
            else:
                self.scene_manager.handle_event(event)

    def _sync_drawable_size(self) -> None:
        """Keeps game dimensions aligned with the active display surface."""
        drawable_size: tuple[int, int] = self.window.get_size()
        if drawable_size != (self.width, self.height):
            self.width, self.height = drawable_size
            self.bg_image = pygame.transform.scale(self.bg_raw, drawable_size)

    def update(self, dt: float = 1 / 60):
        """Updates game state, kinematics, and collisions."""
        self._sync_drawable_size()
        if hasattr(self, 'scene_manager'):
            self.scene_manager.update(dt)

    def _update_playing(self, dt: float):

        if self.player.health <= 0:
            self.state = "GAME_OVER"
            self.audio_manager.play_sfx("game_over")
            if self.data_manager.save_run(self.score, self.survival_time):
                self.high_score = self.score
            return

        self.survival_time += dt
        self.hud.update(dt, self.player.health)
        if self.camera_shake > 0:
            self.camera_shake = max(0.0, self.camera_shake - 60.0 * dt)
        for popup in self.popups:
            popup.update(dt)
        self.popups = [p for p in self.popups if p.timer > 0]

        self.particle_system.update(dt)

        magnet_target = None
        if self.player.magnet_timer > 0:
            assert self.player.rect is not None
            magnet_target = (float(self.player.rect.centerx), float(self.player.rect.centery))

        # Keep coin spawns and milestone drops coordinated in the Game layer.
        for coin in list(self.coins_group):
            coin.update(self.width, self.height, dt, self.get_difficulty(), magnet_target)
            if coin.respawned_this_update:
                self._register_coin_drop()

        for bomb in list(self.bombs_group):
            bomb.update(self.width, self.height, dt)
        for star in list(self.stars_group):
            star.update(self.width, self.height, dt)
        for magnet in list(self.magnets_group):
            magnet.update(self.width, self.height, dt, self.get_difficulty())

        # Update player position and animation
        self.player.update(self.width, self.height, dt, self.get_difficulty())

        # Collision detection: When player collects a coin, coin disappears and respawns from top
        collected_coins = pygame.sprite.spritecollide(self.player, self.coins_group, False)
        if collected_coins:
            self.difficulty_multiplier += len(collected_coins) * 0.005 # +0.5% speed per coin
            self.player.record_coin_pickup(dt)
            self.score += sum(coin.value for coin in collected_coins) * self.player.get_combo_multiplier()
            self.player.start_catch()
            for coin in collected_coins:
                assert coin.rect is not None
                self.particle_system.emit_coin_sparkles(coin.rect.centerx, coin.rect.centery)
                coin.reset(self.width, self.get_difficulty())
                self.popups.append(DamagePopup(coin.rect.centerx, coin.rect.top, "+1", (255, 215, 0)))
                self.audio_manager.play_sfx("coin")
                self._register_coin_drop()

        collected_stars = pygame.sprite.spritecollide(self.player, self.stars_group, False)
        for star in collected_stars:
            assert star.rect is not None
            self.difficulty_multiplier += 0.02 # +2% speed per star
            self.score += config.STAR_VALUE
            self.particle_system.emit_coin_sparkles(star.rect.centerx, star.rect.centery, count=20)
            star.kill()
            self.popups.append(DamagePopup(star.rect.centerx, star.rect.top, f"+{config.STAR_VALUE}", (0, 255, 255)))
            self.audio_manager.play_sfx("coin")

        collected_magnets = pygame.sprite.spritecollide(self.player, self.magnets_group, False)
        for magnet in collected_magnets:
            assert magnet.rect is not None
            self.player.activate_magnet(config.MAGNET_DURATION)
            magnet.kill()
            self.popups.append(DamagePopup(magnet.rect.centerx, magnet.rect.top, "MAGNET!", (0, 100, 255)))
            self.audio_manager.play_sfx("coin")

        hit_bombs = pygame.sprite.spritecollide(self.player, self.bombs_group, False)
        for bomb in hit_bombs:
            assert bomb.rect is not None
            if self.player.take_damage(config.BOMB_DAMAGE):
                self.difficulty_multiplier = 1.0 # Reset speed on bomb hit
                self.particle_system.emit_bomb_shrapnel(bomb.rect.centerx, bomb.rect.centery)
                bomb.kill()
                self.camera_shake = 15.0
                self.popups.append(DamagePopup(bomb.rect.centerx, bomb.rect.top, f"-{config.BOMB_DAMAGE}", (255, 50, 50)))
                self.audio_manager.play_sfx("hit")
            if self.player.health <= 0:
                self.state = "GAME_OVER"
                self.audio_manager.play_sfx("game_over")
                if self.data_manager.save_run(self.score, self.survival_time):
                    self.high_score = self.score
                break

    def _draw_main_menu(self):
        """Draws the main menu screen."""
        self.window.fill(config.MENU_BACKGROUND_COLOR)

        title_surface = self.menu_title_font.render("Ninja Collector", True, config.MENU_TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 2 - 120))
        self.window.blit(title_surface, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        play_img = self.btn_hover_img if self.play_button_rect.collidepoint(mouse_pos) else self.btn_normal_img
        leaderboard_img = self.btn_hover_img if self.leaderboard_button_rect.collidepoint(mouse_pos) else self.btn_normal_img
        quit_img = self.btn_hover_img if self.quit_button_rect.collidepoint(mouse_pos) else self.btn_normal_img

        self.window.blit(play_img, self.play_button_rect.topleft)
        self.window.blit(leaderboard_img, self.leaderboard_button_rect.topleft)
        self.window.blit(quit_img, self.quit_button_rect.topleft)

        play_label = self.menu_button_font.render("PLAY", True, config.MENU_BUTTON_TEXT_COLOR)
        leaderboard_label = self.menu_button_font.render("SCORES", True, config.MENU_BUTTON_TEXT_COLOR)
        quit_label = self.menu_button_font.render("QUIT", True, config.MENU_BUTTON_TEXT_COLOR)

        self.window.blit(play_label, play_label.get_rect(center=self.play_button_rect.center))
        self.window.blit(leaderboard_label, leaderboard_label.get_rect(center=self.leaderboard_button_rect.center))
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
        resume_img = self.btn_hover_img if self.resume_button_rect.collidepoint(mouse_pos) else self.btn_normal_img
        restart_img = self.btn_hover_img if self.restart_button_rect.collidepoint(mouse_pos) else self.btn_normal_img
        options_img = self.btn_hover_img if self.options_button_rect.collidepoint(mouse_pos) else self.btn_normal_img

        self.window.blit(resume_img, self.resume_button_rect.topleft)
        self.window.blit(restart_img, self.restart_button_rect.topleft)
        self.window.blit(options_img, self.options_button_rect.topleft)

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
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 2 - 140))
        self.window.blit(title_surface, title_rect)

        highscore_surface = self.score_font.render(f"HIGH SCORE: {self.high_score}", True, config.HUD_COLOR)
        highscore_rect = highscore_surface.get_rect(center=(self.width // 2, self.height // 2 - 80))
        self.window.blit(highscore_surface, highscore_rect)

        mouse_pos = pygame.mouse.get_pos()
        reset_img = self.btn_wide_hover_img if self.option_reset_button_rect.collidepoint(mouse_pos) else self.btn_wide_normal_img
        back_img = self.btn_hover_img if self.back_button_rect.collidepoint(mouse_pos) else self.btn_normal_img

        self.window.blit(reset_img, self.option_reset_button_rect.topleft)
        self.window.blit(back_img, self.back_button_rect.topleft)

        self.bgm_slider.draw(self.window)
        self.sfx_slider.draw(self.window)

        bgm_label = self.menu_button_font.render(f"BGM: {int(self.audio_manager.bgm_volume * 100)}%", True, config.MENU_BUTTON_TEXT_COLOR)
        sfx_label = self.menu_button_font.render(f"SFX: {int(self.audio_manager.sfx_volume * 100)}%", True, config.MENU_BUTTON_TEXT_COLOR)
        reset_label = self.menu_button_font.render("RESET DATA", True, config.MENU_BUTTON_TEXT_COLOR)
        back_label = self.menu_button_font.render("RETURN", True, config.MENU_BUTTON_TEXT_COLOR)

        self.window.blit(bgm_label, bgm_label.get_rect(midright=(self.bgm_slider.rect.left - 20, self.bgm_slider.rect.centery)))
        self.window.blit(sfx_label, sfx_label.get_rect(midright=(self.sfx_slider.rect.left - 20, self.sfx_slider.rect.centery)))
        self.window.blit(reset_label, reset_label.get_rect(center=self.option_reset_button_rect.center))
        self.window.blit(back_label, back_label.get_rect(center=self.back_button_rect.center))

    def _draw_leaderboard_menu(self):
        """Draws the leaderboard screen with run history."""
        self.window.fill(config.MENU_BACKGROUND_COLOR)
        
        title_surface = self.menu_title_font.render("LEADERBOARD", True, config.MENU_TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(self.width // 2, 60))
        self.window.blit(title_surface, title_rect)

        highscore_surface = self.score_font.render(f"ALL-TIME HIGH SCORE: {self.high_score}", True, (255, 215, 0))
        highscore_rect = highscore_surface.get_rect(center=(self.width // 2, 120))
        self.window.blit(highscore_surface, highscore_rect)

        # Draw up to 5 recent runs
        recent_runs = self.data_manager.run_history[-5:]
        recent_runs.reverse()
        
        start_y = 180
        for i, run in enumerate(recent_runs):
            run_text = f"Run {len(self.data_manager.run_history) - i}: Score {run['score']} (Survived {int(run['time'])}s)"
            run_surface = self.score_font.render(run_text, True, config.HUD_COLOR)
            run_rect = run_surface.get_rect(center=(self.width // 2, start_y + (i * 40)))
            self.window.blit(run_surface, run_rect)

        mouse_pos = pygame.mouse.get_pos()
        reset_img = self.btn_wide_hover_img if self.leaderboard_reset_button_rect.collidepoint(mouse_pos) else self.btn_wide_normal_img
        back_img = self.btn_hover_img if self.leaderboard_back_button_rect.collidepoint(mouse_pos) else self.btn_normal_img
        
        self.window.blit(reset_img, self.leaderboard_reset_button_rect.topleft)
        self.window.blit(back_img, self.leaderboard_back_button_rect.topleft)

        reset_label = self.menu_button_font.render("RESET DATA", True, config.MENU_BUTTON_TEXT_COLOR)
        back_label = self.menu_button_font.render("RETURN", True, config.MENU_BUTTON_TEXT_COLOR)
        
        self.window.blit(reset_label, reset_label.get_rect(center=self.leaderboard_reset_button_rect.center))
        self.window.blit(back_label, back_label.get_rect(center=self.leaderboard_back_button_rect.center))

    def draw(self):
        """Renders all game layers to the active window."""
        if hasattr(self, 'scene_manager'):
            self.scene_manager.draw(self.window)
        pygame.display.update()

    def _draw_playing(self):
        offset_x, offset_y = 0, 0
        if self.camera_shake > 0:
            offset_x = random.uniform(-self.camera_shake, self.camera_shake)
            offset_y = random.uniform(-self.camera_shake, self.camera_shake)

        self.window.blit(self.bg_image, (int(offset_x), int(offset_y)))
        self.particle_system.draw(self.window)
        self.all_sprites.draw(self.window)
        self.bombs_group.draw(self.window)
        self.stars_group.draw(self.window)
        self.magnets_group.draw(self.window)
        self.player.draw(self.window)

        self.hud.draw(self.window, self.score, self.player.health, self.player.max_health, self.survival_time)
        for popup in self.popups:
            popup.draw(self.window)

    def _draw_game_over(self):
        self._draw_playing()
        game_over_surface = self.game_over_font.render("GAME OVER", True, config.GAME_OVER_COLOR)
        game_over_rect = game_over_surface.get_rect(center=(self.width // 2, self.height // 2 - 60))
        self.window.blit(game_over_surface, game_over_rect)

        mouse_pos = pygame.mouse.get_pos()
        restart_img = self.btn_hover_img if self.game_over_restart_button_rect.collidepoint(mouse_pos) else self.btn_normal_img
        menu_img = self.btn_menu_hover_img if self.game_over_menu_button_rect.collidepoint(mouse_pos) else self.btn_menu_normal_img

        self.window.blit(restart_img, self.game_over_restart_button_rect.topleft)
        self.window.blit(menu_img, self.game_over_menu_button_rect.topleft)

        restart_label = self.menu_button_font.render("RESTART", True, config.MENU_BUTTON_TEXT_COLOR)
        menu_label = self.menu_button_font.render("MAIN MENU", True, config.MENU_BUTTON_TEXT_COLOR)

        self.window.blit(restart_label, restart_label.get_rect(center=self.game_over_restart_button_rect.center))
        self.window.blit(menu_label, menu_label.get_rect(center=self.game_over_menu_button_rect.center))

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
