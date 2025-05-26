import pygame

class Camera:
    def __init__(self, width, height):
        self.offset = pygame.Vector2(0, 0)
        self.width = width
        self.height = height

    def update(self, target_pos, target_size, smoothing=5.0):
        target_center = pygame.Vector2(target_pos.x + target_size[0] / 2,
                                       target_pos.y + target_size[1] / 2)

        screen_center = pygame.Vector2(self.width / 2, self.height / 2)
        desired_offset = target_center - screen_center

        self.offset += (desired_offset - self.offset) / smoothing
