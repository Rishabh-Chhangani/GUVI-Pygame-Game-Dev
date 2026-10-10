from pathlib import Path
from typing import Self

import pygame
import pytest

from src.asset_manager import AssetManager


class LoadedImage:
    def convert_alpha(self) -> Self:
        return self


def test_get_image_caches_loaded_surface(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image_path = tmp_path / "sprite.png"
    image_path.touch()
    loaded_image = LoadedImage()
    load_calls: list[str] = []

    def load_image(path: str) -> LoadedImage:
        load_calls.append(path)
        return loaded_image

    monkeypatch.setattr(pygame.image, "load", load_image)
    manager = AssetManager(tmp_path)

    first = manager.get_image("sprite.png", size=None)
    second = manager.get_image("sprite.png", size=None)

    assert first is loaded_image
    assert second is first
    assert load_calls == [str(image_path)]
