class SceneManager:
    def __init__(self, initial_scene):
        self.scene = initial_scene

    def switch_to(self, new_scene):
        self.scene = new_scene

    def handle_event(self, event):
        if self.scene:
            self.scene.handle_event(event)

    def update(self, dt):
        if self.scene:
            self.scene.update(dt)

    def draw(self, screen):
        if self.scene:
            self.scene.draw(screen)
