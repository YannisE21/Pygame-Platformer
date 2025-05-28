import pygame
import random

class Enemy:
    def __init__(self, x, y, width, height, image, speed=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image
        self.speed = speed
        self.pos = pygame.Vector2(x, y)
        self.spaw_pos = pygame.Vector2(x, y)
        self.detection_radius = 300
        self.action = 0

    def update(self, dt, player_pos):
        direction_to_player = player_pos - self.pos
        distance_to_player = direction_to_player.length()

        if distance_to_player < self.detection_radius and distance_to_player > 20:
            self.action = 1
        elif distance_to_player > 20:
            self.action = 2
        else:
            self.action = 0

        if self.action == 1:
            move_dir = direction_to_player
            if move_dir.length_squared() > 0:
                move_dir.normalize_ip()

            self.pos += move_dir * self.speed * dt + pygame.Vector2(0, -1)
            self.rect.topleft = (int(self.pos.x), int(self.pos.y))

        elif self.action == 2:
            direction_to_spawn = self.spaw_pos - self.pos
            if direction_to_spawn.length_squared() > 0:
                direction_to_spawn.normalize_ip()
            self.pos += direction_to_spawn * self.speed * dt
            self.rect.topleft = (int(self.pos.x), int(self.pos.y))


    def draw(self, screen, camera_offset):
        screen.blit(self.image, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))

    def collides_with(self, target_rect):
        return self.rect.colliderect(target_rect)