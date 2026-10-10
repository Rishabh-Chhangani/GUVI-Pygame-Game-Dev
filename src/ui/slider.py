import pygame

class Slider:
    def __init__(self, x: int, y: int, width: int, track_img: pygame.Surface, thumb_img: pygame.Surface, initial_value: float = 1.0):
        self.rect = pygame.Rect(x, y, width, track_img.get_height())
        self.track_img = pygame.transform.scale(track_img, (width, track_img.get_height()))
        self.thumb_img = thumb_img
        
        self.min_val = 0.0
        self.max_val = 1.0
        self.value = initial_value
        
        # Center thumb vertically
        self.thumb_rect = self.thumb_img.get_rect()
        self.thumb_rect.centery = self.rect.centery
        self.is_dragging = False
        self.update_thumb_pos()
        
    def update_thumb_pos(self):
        """Update thumb pixel position based on value."""
        percent = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.thumb_rect.centerx = int(self.rect.left + percent * self.rect.width)
        self.thumb_rect.centery = self.rect.centery
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Returns True if value changed."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.thumb_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.is_dragging = True
                self._update_value_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self._update_value_from_mouse(event.pos[0])
                return True
        return False
        
    def _update_value_from_mouse(self, mouse_x: int):
        rel_x = mouse_x - self.rect.left
        percent = rel_x / self.rect.width
        percent = max(0.0, min(1.0, percent))
        self.value = self.min_val + percent * (self.max_val - self.min_val)
        self.update_thumb_pos()
        
    def draw(self, surface: pygame.Surface):
        # Draw track
        surface.blit(self.track_img, self.rect.topleft)
        # Draw thumb
        surface.blit(self.thumb_img, self.thumb_rect.topleft)
