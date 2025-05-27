import pygame
import random

class Enemy:
    def __init__(self, x, y, width, height, image, speed=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image
        self.speed = speed
        self.pos = pygame.Vector2(x, y)
        self.spaw_pos = pygame.Vector2(x, y)
        self.action = 1
        self.detection_radius = 300

    def update(self, dt, player_pos):
        direction_player = player_pos - self.pos
        distance_player = direction_player.length()

        if distance_player < self.detection_radius and distance_player > 20:
            self.action = 1
        elif distance_player > 20:
            self.action = 2

        if self.action == 1:
            direction_player.normalize_ip()
            self.pos += direction_player * self.speed * dt
            self.rect.topleft = (int(self.pos.x), int(self.pos.y))

        elif self.action == 2:
            direction_spawn = self.spaw_pos - self.pos
            if direction_spawn != pygame.Vector2(0, 0):
                direction_spawn.normalize_ip()
            self.pos += direction_spawn * self.speed * dt
            self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, screen, camera_offset):
        screen.blit(self.image, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))

    def collides_with(self, target_rect):
        return self.rect.colliderect(target_rect)