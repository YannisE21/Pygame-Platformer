import pygame
import csv
import os

pygame.init()

# Settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
TILE_SIZE = 40
MAP_WIDTH, MAP_HEIGHT = 100, 20
SPAWN_TILE = 1  # Changed to integer

WHITE = (255, 255, 255)
GRID_COLOR = (60, 60, 60)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tilemap Editor")
clock = pygame.time.Clock()

# Load tile images
def load_tile(path):
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (TILE_SIZE, TILE_SIZE))

tiles = {
    0: pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA),  # empty tile = transparent
    SPAWN_TILE: pygame.Surface((TILE_SIZE, TILE_SIZE)),
    2: load_tile("./assets/images/dirt.png"),
    3: load_tile("./assets/images/grass.png"),
    4: load_tile("./assets/images/arrow_sign.png"),
    5: load_tile("./assets/images/plant_small.png"),
    6: load_tile("./assets/images/spike.png")
}
tiles[SPAWN_TILE].fill((255, 0, 255))  # magenta for spawn

max_tile_id = max(k for k in tiles.keys() if isinstance(k, int))  # max int tile id

# Load or create map
def load_map(path):
    if os.path.exists(path):
        with open(path, newline='') as file:
            data = []
            for row in csv.reader(file):
                new_row = []
                for cell in row:
                    try:
                        new_row.append(int(cell))
                    except ValueError:
                        new_row.append(0)  # fallback empty if invalid
                data.append(new_row)
            return data
    return [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

def save_map(map_data, path):
    with open(path, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(map_data)

tilemap = load_map("level.csv")

# Camera
camera_x = 0
camera_y = 0
CAMERA_SPEED = 400

# Main loop
running = True
while running:
    dt = clock.tick(60) / 1000.0
    screen.fill(WHITE)

    # Input handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        camera_x -= CAMERA_SPEED * dt
    if keys[pygame.K_RIGHT]:
        camera_x += CAMERA_SPEED * dt
    if keys[pygame.K_UP]:
        camera_y -= CAMERA_SPEED * dt
    if keys[pygame.K_DOWN]:
        camera_y += CAMERA_SPEED * dt

    # Clamp camera
    camera_x = max(0, min(camera_x, MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT))

    # Draw tiles
    start_x = int(camera_x // TILE_SIZE)
    start_y = int(camera_y // TILE_SIZE)
    end_x = int((camera_x + SCREEN_WIDTH) // TILE_SIZE) + 1
    end_y = int((camera_y + SCREEN_HEIGHT) // TILE_SIZE) + 1

    for y in range(start_y, min(end_y, MAP_HEIGHT)):
        for x in range(start_x, min(end_x, MAP_WIDTH)):
            tile = tilemap[y][x]
            if tile in tiles:
                draw_x = x * TILE_SIZE - camera_x
                draw_y = y * TILE_SIZE - camera_y
                screen.blit(tiles[tile], (draw_x, draw_y))

    # Draw grid
    for x in range(start_x * TILE_SIZE, end_x * TILE_SIZE, TILE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x - camera_x, 0), (x - camera_x, SCREEN_HEIGHT))
    for y in range(start_y * TILE_SIZE, end_y * TILE_SIZE, TILE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y - camera_y), (SCREEN_WIDTH, y - camera_y))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            tile_x = int((mx + camera_x) // TILE_SIZE)
            tile_y = int((my + camera_y) // TILE_SIZE)
            if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
                if event.button == 1:  # Left click: cycle tiles including spawn
                    current = tilemap[tile_y][tile_x]
                    next_tile = (current + 1) % (max_tile_id + 1)
                    # Prevent spawn cycling here or allow it - your choice
                    tilemap[tile_y][tile_x] = next_tile
                elif event.button == 3:  # Right click = erase
                    tilemap[tile_y][tile_x] = 0

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save_map(tilemap, "level.csv")
                print("Map saved.")
            elif event.key == pygame.K_l:
                tilemap = load_map("level.csv")
                print("Map loaded.")
            elif event.key == pygame.K_p:
                # Place spawn at mouse position
                mx, my = pygame.mouse.get_pos()
                tile_x = int((mx + camera_x) // TILE_SIZE)
                tile_y = int((my + camera_y) // TILE_SIZE)
                if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
                    # Remove existing spawn
                    for y in range(MAP_HEIGHT):
                        for x in range(MAP_WIDTH):
                            if tilemap[y][x] == SPAWN_TILE:
                                tilemap[y][x] = 0
                    tilemap[tile_y][tile_x] = SPAWN_TILE
                    print(f"Spawn point set at ({tile_x}, {tile_y})")

    pygame.display.flip()

pygame.quit()
