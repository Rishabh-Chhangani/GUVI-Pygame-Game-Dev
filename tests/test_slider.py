import pygame

from src.ui.slider import Slider


def test_clicking_slider_middle_sets_value_to_half() -> None:
    track = pygame.Surface((100, 10), pygame.SRCALPHA)
    thumb = pygame.Surface((10, 20), pygame.SRCALPHA)
    slider = Slider(20, 30, 100, track, thumb, initial_value=0.0)
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        button=1,
        pos=(70, 35),
    )

    assert slider.handle_event(event)
    assert slider.value == 0.5
    assert slider.is_dragging
