import pygame

TILES = {}
TILE_SIZE= 18

def load(path, scale=1, colorkey=None):
    image = pygame.image.load(path).convert_alpha()
    if scale != 1:
        image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
    if colorkey is not None:
        image.set_colorkey(colorkey)
    return image

def load_tiles():
    tiles = {
        2: load("./assets/images/dirt.png", 2),
        3: load("./assets/images/grass.png", 2),
        4: load("./assets/images/arrow_sign.png", 2),
        5: load("./assets/images/plant_small.png", 2),
        6: load("./assets/images/spike.png", 2),
        7: load("./assets/images/checkpoint.png", 2),
        8: load("./assets/images/finish.png", 2)
    }
    tile_size = tiles[2].get_width()
    return tiles, tile_size

