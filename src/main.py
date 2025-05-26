import pygame
import sys
import csv

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
FPS = 60
WHITE = (255, 255, 255)
BACKGROUND = (24, 33, 51)

# Pygame Setup
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Platformer")
WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SHOWN)
clock = pygame.time.Clock()
FPS = 60

camera = pygame.Vector2(0, 0)
CAMERA_SMOOTHING = 5.0

font = pygame.font.Font("./assets/fonts/ByteBounce.ttf", 70)

def load_map(path):
    with open(path, newline='') as file:
        return [[int(tile) for tile in row] for row in csv.reader(file)]

def load_tile(path, scale=1, colorkey=None):
    image = pygame.image.load(path).convert_alpha()
    if scale != 1:
        image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
    if colorkey is not None:
        image.set_colorkey(colorkey)
    return image

class Player:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False

        self.ACCEL = 1000
        self.FRICTION = 8
        self.MAX_SPEED = 300
        self.JUMP_FORCE = -700
        self.GRAVITY = 1700

        self.jump_buffer_time = 0.15
        self.jump_buffer_timer = 0.0

        self.coyote_time = 0.1
        self.coyote_timer = 0.0

    def handle_input(self, keys, dt):
        move_dir = 0
        if keys[pygame.K_d]:
            move_dir += 1
        if keys[pygame.K_a]:
            move_dir -= 1

        self.vel.x += move_dir * self.ACCEL * dt

        if move_dir == 0:
            self.vel.x -= self.vel.x * self.FRICTION * dt

        if abs(self.vel.x) < 10:
            self.vel.x = 0
        self.vel.x = max(min(self.vel.x, self.MAX_SPEED), -self.MAX_SPEED)

        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_w]
        if jump_pressed:
            self.jump_buffer_timer = self.jump_buffer_time

    def apply_gravity(self, dt):
        self.vel.y += self.GRAVITY * dt

    def try_jump(self):
        if self.coyote_timer > 0:
            self.vel.y = self.JUMP_FORCE
            self.coyote_timer = 0
            self.jump_buffer_timer = 0
            return True
        return False

    def update(self, dt, platforms):
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= dt
        if not self.on_ground:
            self.coyote_timer -= dt
        else:
            self.coyote_timer = self.coyote_time

        self.pos.x += self.vel.x * dt
        self.rect.x = round(self.pos.x)
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel.x > 0:
                    self.rect.right = platform.left
                elif self.vel.x < 0:
                    self.rect.left = platform.right
                self.pos.x = self.rect.x
                self.vel.x = 0

        self.apply_gravity(dt)
        self.pos.y += self.vel.y * dt
        self.rect.y = round(self.pos.y)

        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel.y > 0:
                    self.rect.bottom = platform.top
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = platform.bottom
                self.pos.y = self.rect.y
                self.vel.y = 0

        if self.jump_buffer_timer > 0:
            jumped = self.try_jump()
            if jumped:
                self.jump_buffer_timer = 0

    def draw(self, surface, offset):
        surface.blit(character_img, self.pos - offset)

levels = {
    1: "level1.csv",
    2: "level2.csv"
}
current_level = 1

TILES = {
    2: load_tile("./assets/images/dirt.png", 2),
    3: load_tile("./assets/images/grass.png", 2),
    4: load_tile("./assets/images/arrow_sign.png", 2),
    5: load_tile("./assets/images/plant_small.png", 2),
    6: load_tile("./assets/images/spike.png", 2),
    7: load_tile("./assets/images/checkpoint.png", 2),
    8: load_tile("./assets/images/finish.png", 2)
}
TILE_SIZE = TILES[2].get_width()
character_img = load_tile("./assets/images/character.png", 1.5, (0, 0, 0))

def load_level(level_id):
    global tile_map, spawn, platforms, death_colliders, checkpoint_colliders, finish_colliders, player, last_checkpoint

    tile_map = load_map(levels[level_id])
    spawn = pygame.Vector2(100, 100)

    platforms = []
    death_colliders = []
    checkpoint_colliders = []
    finish_colliders = []

    for y, row in enumerate(tile_map):
        for x, tile in enumerate(row):
            world_pos = (x * TILE_SIZE, y * TILE_SIZE)
            if tile == 1:
                spawn = pygame.Vector2(*world_pos)
            elif tile in (2, 3):
                platforms.append(pygame.Rect(*world_pos, TILE_SIZE, TILE_SIZE))
            elif tile == 6:
                rect = pygame.Rect(world_pos[0], world_pos[1] + (TILE_SIZE / 3), TILE_SIZE / 1.5, TILE_SIZE / 3)
                death_colliders.append(rect)
            elif tile == 7:
                checkpoint_colliders.append(pygame.Rect(*world_pos, TILE_SIZE, TILE_SIZE))
            elif tile == 8:
                finish_colliders.append(pygame.Rect(*world_pos, TILE_SIZE, TILE_SIZE))
    player = Player(spawn.x, spawn.y, 30, 35)
    camera.x = player.pos.x + player.rect.width // 2 - SCREEN_WIDTH // 2
    camera.y = player.pos.y + player.rect.height // 2 - SCREEN_HEIGHT // 2
    last_checkpoint = pygame.Vector2(spawn.x, spawn.y)

load_level(current_level)

running = True
while running:
    dt = min(clock.tick(FPS) / 1000.0, 1 / 30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.handle_input(keys, dt)
    player.update(dt, platforms)

    death = False
    idx = player.rect.collidelist(death_colliders)
    if idx != -1:
        death = True

    if death:
        player.pos = last_checkpoint.copy()
        player.vel = pygame.Vector2(0, 0)
        camera.x = player.pos.x + player.rect.width // 2 - SCREEN_WIDTH // 2
        camera.y = player.pos.y + player.rect.height // 2 - SCREEN_HEIGHT // 2

    for collider in checkpoint_colliders[:]:
        if player.rect.colliderect(collider):
            last_checkpoint = pygame.Vector2(collider.x, collider.y)
            checkpoint_colliders.remove(collider)

    idx = player.rect.collidelist(finish_colliders)
    if idx != -1:
        if current_level + 1 in levels:
            current_level += 1
            load_level(current_level)
        else:
            running = False

    # Camera to Player
    target_x = player.pos.x + player.rect.width / 2 - SCREEN_WIDTH / 2
    target_y = player.pos.y + player.rect.height / 2 - SCREEN_HEIGHT / 2
    camera.x += (target_x - camera.x) * CAMERA_SMOOTHING * dt
    camera.y += (target_y - camera.y) * CAMERA_SMOOTHING * dt

    WINDOW.fill(BACKGROUND)

    start_x = max(0, int(camera.x) // TILE_SIZE)
    end_x = min(len(tile_map[0]), int((camera.x + SCREEN_WIDTH) // TILE_SIZE) + 1)
    start_y = max(0, int(camera.y) // TILE_SIZE)
    end_y = min(len(tile_map), int((camera.y + SCREEN_HEIGHT) // TILE_SIZE) + 1)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile = tile_map[y][x]
            if tile in TILES:
                WINDOW.blit(TILES[tile], (x * TILE_SIZE - camera.x, y * TILE_SIZE - camera.y))

    player.draw(WINDOW, camera)

    level_text = font.render(f"{current_level}", True, WHITE)
    WINDOW.blit(level_text, (SCREEN_WIDTH / 2, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
