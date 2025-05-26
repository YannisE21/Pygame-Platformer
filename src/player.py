import pygame

class Player:
    def __init__(self, x, y, width, height, character_img):
        self.rect = pygame.Rect(x, y, width, height)
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False

        self.character_img = character_img

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
        surface.blit(self.character_img, self.pos - offset)