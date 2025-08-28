import pygame
class Player(pygame.sprite.Sprite):
    @classmethod
    def load_images(cls):
        cls.idle_images = [
            pygame.image.load("Ninja1.jpg").convert_alpha(),
            pygame.image.load("Ninja2.jpg").convert_alpha(),
            pygame.image.load("Ninja3.jpg").convert_alpha(),
            pygame.image.load("Ninja4.jpg").convert_alpha(),
            pygame.image.load("Ninja5.jpg").convert_alpha()
        ]

    def __init__(self,x,y,w,h):
        pygame.sprite.Sprite.__init__(self)
        self.current_frame=0
        self.animation_delay=100
        self.last_update=pygame.time.get_ticks()
        self.image =self.idle_images[self.current_frame]
        self.rect = pygame.Rect(x,y,w,h)
        self.x = x
        self.y =y

    def draw(self,window):
        window.blit(self.image,self.rect)

    def update(self):
        if pygame.time.get_ticks() - self.last_update>self.animation_delay:
            self.current_frame += 1
            self.current_frame %= len(self.idle_images)
            self.image = self.idle_images[self.current_frame]
            self.last_update=pygame.time.get_ticks()

# Static Sprite
class StarSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed_):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed_

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > height:
            self.rect.y = -self.rect.height


pygame.init()


width = 800
height = 600
window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
is_resizable = True

bg_image_path = 'bg1.png'
bg_image = pygame.image.load(bg_image_path)
bg_image = pygame.transform.scale(bg_image, (width, height))

# bg_color = (255,255,255)

caption = "Ninja Collector"
pygame.display.set_caption(caption)
icon = "star.png"
icon_image = pygame.image.load(icon)
pygame.display.set_icon(icon_image)

sprite_path = "star.png"
sprite_image = pygame.image.load(sprite_path)
sprite_image = pygame.transform.scale(sprite_image, (100, 100))
star_sprite = StarSprite(sprite_image, width // 2, height // 2, 1)


sprite1_path = "star1.png"
sprite1_image = pygame.image.load(sprite1_path)
star1_sprite = StarSprite(sprite1_image, 200, 200, 0.9)

all_sprite = pygame.sprite.Group()
all_sprite.add(star_sprite)
all_sprite.add(star1_sprite)

Player.load_images()
player = Player(370, height-150,64,64)


running = True
while running:
    # screen.blit(bg_image, (0, 0))
    # screen.blit(coin_sprite.image,coin_sprite.rect)
    # screen.fill(bg_color)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            if is_resizable:
                width = event.w
                height = event.h
                window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                bg_image = pygame.transform.scale(bg_image, (width, height))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                is_resizable = not is_resizable
                if is_resizable:
                    window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                    bg_image = pygame.transform.scale(bg_image, (width, height))
                else:
                    screen = pygame.display.set_mode((width, height))
                    bg_image = pygame.transform.scale(bg_image, (width, height))
    if star_sprite.rect.colliderect(player.rect):
        print("Collision has Occurred")

    window.blit(bg_image, (0, 0))
    # coin_sprite.update()
    # window.blit(coin_sprite.image, coin_sprite.rect)
    all_sprite.update()
    all_sprite.draw(window)
    player.update()
    player.draw(window)

    pygame.display.update()
pygame.quit()
