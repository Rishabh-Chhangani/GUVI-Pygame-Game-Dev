import importlib
import random
import pygame
import src.config as config
from src.asset_manager import AssetManager
import src.entities.player as player_module
import src.entities.coin as coin_module


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
        self.score = 0
        self.missed_coins = 0
        self.game_over = False
        self.score_font = pygame.font.Font(None, config.SCORE_FONT_SIZE)
        self.game_over_font = pygame.font.Font(None, config.GAME_OVER_FONT_SIZE)

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

        # Animated Coins with smooth proportional scaling
        coin_frames = self.assets.get_proportional_animation(config.COIN_FRAME_NAMES, target_box=config.COIN_SIZE)
        self.coins_group: pygame.sprite.Group[coin_module.CoinSprite] = pygame.sprite.Group()
        self.all_sprites: pygame.sprite.Group[coin_module.CoinSprite] = pygame.sprite.Group()

        # Spawn initial coins staggered across screen
        for _ in range(config.COIN_COUNT):
            spawn_x = random.randint(30, max(30, self.width - config.COIN_SIZE[0] - 30))
            spawn_y = -random.randint(50, 400)
            coin = coin_module.CoinSprite(coin_frames, spawn_x, spawn_y, speed=random.uniform(2.5, 4.0))
            self.coins_group.add(coin)
            self.all_sprites.add(coin)

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

    def handle_events(self):
        """Processes OS and user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                if self.is_resizable:
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self._sync_drawable_size()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.is_resizable = not self.is_resizable
                    mode_flag = pygame.RESIZABLE if self.is_resizable else 0
                    self.window = pygame.display.set_mode((self.width, self.height), mode_flag)
                    self._sync_drawable_size()
                elif event.key == pygame.K_F5:
                    self.reload_game_state()

    def _sync_drawable_size(self) -> None:
        """Keeps game dimensions aligned with the active display surface."""
        drawable_size: tuple[int, int] = self.window.get_size()
        if drawable_size != (self.width, self.height):
            self.width, self.height = drawable_size
            self.bg_image = pygame.transform.scale(self.bg_raw, drawable_size)

    def update(self):
        """Updates game state, kinematics, and collisions."""
        self._sync_drawable_size()
        if self.game_over:
            return

        # Update coins and count those that pass the bottom of the screen.
        for coin in self.coins_group:
            coin.update(self.width, self.height)
            if coin.missed_this_update:
                self.missed_coins += 1
                if self.missed_coins >= config.MAX_MISSED_COINS:
                    self.game_over = True
                    break

        if self.game_over:
            return

        # Update player position and animation
        self.player.update(self.width, self.height)

        # Collision detection: When player collects a coin, coin disappears and respawns from top
        collected_coins = pygame.sprite.spritecollide(self.player, self.coins_group, False)
        if collected_coins:
            self.score += len(collected_coins)
            self.player.start_catch()
            for coin in collected_coins:
                coin.reset(self.width)

    def draw(self):
        """Renders all game layers to the active window."""
        self.window.blit(self.bg_image, (0, 0))
        self.all_sprites.draw(self.window)
        self.player.draw(self.window)

        score_surface = self.score_font.render(f"Score: {self.score}", True, config.HUD_COLOR)
        self.window.blit(score_surface, config.SCORE_POSITION)
        if self.game_over:
            game_over_surface = self.game_over_font.render("GAME OVER", True, config.GAME_OVER_COLOR)
            game_over_rect = game_over_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.window.blit(game_over_surface, game_over_rect)

        pygame.display.update()

    def run(self):
        """Main game loop."""
        while self.running:
            self.clock.tick(config.FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
