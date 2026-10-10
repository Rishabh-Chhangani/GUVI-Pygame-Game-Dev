from pathlib import Path
from typing import cast

import pygame

from src.config import ASSETS_DIR


class AssetManager:
    """Manages loading and caching of game assets (surfaces, animations, sounds)."""

    def __init__(self, base_dir : Path | str = ASSETS_DIR):
        self.base_dir = Path(base_dir)
        self._image_cache: dict[tuple[object, ...], pygame.Surface | list[pygame.Surface]] = {}
        self._sound_cache: dict[str, pygame.mixer.Sound] = {}

    def get_image(self, filename : str, size:tuple[int,int] |None, smooth :bool =False) -> pygame.Surface:
        """Loads and caches an image, optionally scaled to `size` (width, height)."""
        key = (str(filename), size, smooth)
        if key in self._image_cache:
            return cast(pygame.Surface, self._image_cache[key])

        filepath = self.base_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Asset not found: {filepath}")

        # Load with alpha channel support
        surface = pygame.image.load(str(filepath)).convert_alpha()
        if size is not None:
            if smooth:
                surface = pygame.transform.smoothscale(surface, size)
            else:
                surface = pygame.transform.scale(surface, size)

        self._image_cache[key] = surface
        return surface

    def get_animation(self, filenames: list[str], size: tuple[int, int] | None = None, smooth: bool = False) -> list[pygame.Surface]:
        """Loads a sequence of image surfaces for animations."""
        return [self.get_image(name, size, smooth=smooth) for name in filenames]

    def get_proportional_animation(self, filenames: list[str], target_box: tuple[int, int] = (50, 50)) -> list[pygame.Surface]:
        """
        Loads animation frames scaled proportionally and centered on a uniform transparent canvas.
        Maintains correct 3D aspect ratio during rotations (e.g. coin turning edge-on).
        """
        key = ("prop_anim", tuple(filenames), target_box)
        if key in self._image_cache:
            return cast(list[pygame.Surface], self._image_cache[key])

        box_w, box_h = target_box
        surfaces: list[pygame.Surface] = []

        for name in filenames:
            filepath = self.base_dir / name
            if not filepath.exists():
                raise FileNotFoundError(f"Asset not found: {filepath}")

            raw = pygame.image.load(str(filepath)).convert_alpha()
            orig_w, orig_h = raw.get_size()

            # Maintain natural aspect ratio based on box height
            scale_ratio = box_h / float(orig_h)
            new_w = max(1, int(orig_w * scale_ratio))
            new_h = box_h

            scaled_frame = pygame.transform.smoothscale(raw, (new_w, new_h))

            # Center onto a fixed transparent surface of size (box_w, box_h)
            canvas = pygame.Surface(target_box, pygame.SRCALPHA)
            x_offset = (box_w - new_w) // 2
            y_offset = (box_h - new_h) // 2
            canvas.blit(scaled_frame, (x_offset, y_offset))

            surfaces.append(canvas)

        self._image_cache[key] = surfaces
        return surfaces

    def get_sound(self, filename: str) -> pygame.mixer.Sound:
        """Loads and caches a sound effect from the asset directory."""
        if filename not in self._sound_cache:
            filepath = self.base_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"Asset not found: {filepath}")

            self._sound_cache[filename] = pygame.mixer.Sound(str(filepath))

        return self._sound_cache[filename]

    def clear_cache(self):
        """Clears cached assets."""
        self._image_cache.clear()
        self._sound_cache.clear()
