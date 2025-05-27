import pygame
import sys
import constants
from player import Player
from camera import Camera
import level
import tile_data
from enemy import Enemy

# Pygame Setup
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Platformer")
WINDOW = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.SHOWN)
clock = pygame.time.Clock()
FPS = 60

camera = Camera(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
CAMERA_SMOOTHING = 30.0

font = pygame.font.Font("./assets/fonts/ByteBounce.ttf", 70)

levels = level.levels
current_level = 1

tile_data.TILES, tile_data.TILE_SIZE = tile_data.load_tiles()
TILES = tile_data.TILES
TILE_SIZE = tile_data.TILE_SIZE
character_img = tile_data.load("./assets/images/character.png", 1.5, (0, 0, 0))
enemy_img = tile_data.load("./assets/images/enemy.png", 1.5, (0, 0, 0))

def fade(screen, clock, speed=5, fade_in=False):
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill((0, 0, 0))

    if fade_in:
        alpha_values = range(255, -1, -speed)
    else:
        alpha_values = range(0, 256, speed)

    for alpha in alpha_values:
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        clock.tick(60)

def draw_tiles():
    start_x = max(0, int(camera.offset.x) // TILE_SIZE)
    end_x = min(len(tile_map[0]), int((camera.offset.x + constants.SCREEN_WIDTH) // TILE_SIZE) + 1)
    start_y = max(0, int(camera.offset.y) // TILE_SIZE)
    end_y = min(len(tile_map), int((camera.offset.y + constants.SCREEN_HEIGHT) // TILE_SIZE) + 1)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile = tile_map[y][x]
            if tile in TILES:
                WINDOW.blit(TILES[tile], (x * TILE_SIZE - camera.offset.x, y * TILE_SIZE - camera.offset.y))

def load_level(level_id):
    global tile_map, spawn, platforms, death_colliders, checkpoint_colliders, finish_colliders, player, last_checkpoint, enemies

    tile_map = level.load_map(levels[level_id])
    spawn = pygame.Vector2(100, 100)

    platforms = []
    death_colliders = []
    checkpoint_colliders = []
    finish_colliders = []
    enemies = []

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
            elif tile == 10:
                enemies.append(Enemy(world_pos[0], world_pos[1], 30, 35, enemy_img))

    player = Player(spawn.x, spawn.y, 30, 35, character_img)
    camera.update(player.pos, (player.rect.width, player.rect.height), 1)
    last_checkpoint = pygame.Vector2(spawn.x, spawn.y)

load_level(current_level)

def handle_player_death():
    player.pos = last_checkpoint.copy()
    player.vel = pygame.Vector2(0, 0)
    camera.update(player.pos, (player.rect.width, player.rect.height), 1)

running = True
while running:
    dt = min(clock.tick(FPS) / 1000.0, 1 / 30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.handle_input(keys, dt)
    player.update(dt, platforms)

    for enemy in enemies:
        enemy.update(dt, player.pos)
        if enemy.collides_with(player.rect):
            handle_player_death()

    death = False
    idx = player.rect.collidelist(death_colliders)
    if idx != -1:
        death = True

    if death:
        handle_player_death()

    for collider in checkpoint_colliders[:]:
        if player.rect.colliderect(collider):
            last_checkpoint = pygame.Vector2(collider.x, collider.y)
            checkpoint_colliders.remove(collider)
            tile_x = collider.x // TILE_SIZE
            tile_y = collider.y // TILE_SIZE
            tile_map[tile_y][tile_x] = 9

    idx = player.rect.collidelist(finish_colliders)
    if idx != -1:
        if current_level + 1 in levels:
            current_level += 1
            fade(WINDOW, clock, 5, False)
            load_level(current_level)
            transition_text = font.render(f"Level {current_level}", True, constants.WHITE)
            WINDOW.blit(transition_text, (constants.SCREEN_WIDTH / 2 - (transition_text.get_width() / 2), constants.SCREEN_HEIGHT / 2 - (transition_text.get_height() / 2)))
            pygame.display.update()
            pygame.time.delay(4000)
        else:
            running = False
            fade(WINDOW, clock, 5, False)
            transition_text = font.render(f"The End", True, constants.WHITE)
            WINDOW.blit(transition_text, (constants.SCREEN_WIDTH / 2 - (transition_text.get_width() / 2), constants.SCREEN_HEIGHT / 2 - (transition_text.get_height() / 2)))
            pygame.display.update()
            pygame.time.delay(8000)

    camera.update(player.pos, (player.rect.width, player.rect.height), CAMERA_SMOOTHING)

    WINDOW.fill(constants.BACKGROUND)

    draw_tiles()
    player.draw(WINDOW, camera.offset)
    for enemy in enemies:
        enemy.draw(WINDOW, camera.offset)

    level_text = font.render(f"{current_level}", True, constants.WHITE)
    WINDOW.blit(level_text, (constants.SCREEN_WIDTH / 2, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
