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
        self.width = config.DEFAULT_WIDTH
        self.height = config.DEFAULT_HEIGHT
        self.is_resizable = True
        self.window : pygame.Surface = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
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

        # Initialize Entities
        self._init_entities()

    def _init_entities(self):
        """Instantiates all player and world sprite entities."""
        # Player
        player_frames = self.assets.get_animation(config.PLAYER_FRAME_NAMES, size=config.PLAYER_SIZE)
        self.player: player_module.Player = player_module.Player(
            frames=player_frames,
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
                    self.width, self.height = event.w, event.h
                    self.window = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    self.bg_image = pygame.transform.scale(self.bg_raw, (self.width, self.height))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.is_resizable = not self.is_resizable
                    mode_flag = pygame.RESIZABLE if self.is_resizable else 0
                    self.window = pygame.display.set_mode((self.width, self.height), mode_flag)
                    self.bg_image = pygame.transform.scale(self.bg_raw, (self.width, self.height))
                elif event.key == pygame.K_F5:
                    self.reload_game_state()

    def update(self):
        """Updates game state, kinematics, and collisions."""
        # Update animated falling coins
        for coin in self.coins_group:
            coin.update(self.width, self.height)

        # Update player position and animation
        self.player.update(self.width, self.height)

        # Collision detection: When player collects a coin, coin disappears and respawns from top
        collected_coins = pygame.sprite.spritecollide(self.player, self.coins_group, False)
        for coin in collected_coins:
            coin.reset(self.width)

    def draw(self):
        """Renders all game layers to the active window."""
        self.window.blit(self.bg_image, (0, 0))
        self.all_sprites.draw(self.window)
        self.player.draw(self.window)
        pygame.display.update()

    def run(self):
        """Main game loop."""
        while self.running:
            self.clock.tick(config.FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()

