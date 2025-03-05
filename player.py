import pygame
from os import listdir
from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, groups, x, y, parameters: dict):
        super().__init__(groups)
        self.clock = pygame.time.Clock()
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0

        # Ładowanie animacji
        animation_types = ['idle', 'run', 'jump']
        for animation in animation_types:
            temp_list = []
            # Sprawdzenie ilości animacji w folderze
            num_of_frames = listdir(f'Assets/player/{animation}')
            for i in range(len(num_of_frames)):
                img = pygame.image.load(f'Assets/player/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * SCALE), (int(img.get_height() * SCALE))))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.update_time = pygame.time.get_ticks()
        self.direction = 1
        self.flip = False

        # Parametry
        self.block_group = parameters['block_group']

        # Wartości fizyczne
        self.velocity = pygame.math.Vector2()
        self.speed = 150
        self.on_ground = False
        self.jump_cooldown = 0
        self.jump_force = -450
        self.DT = get_DT(self.clock)

    def update_animation(self):
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_collisions(self, direction):
        if direction == "horizontal":
            for block in self.block_group:
                if block.rect.colliderect(self.rect):
                    if self.velocity.x > 0: # Poruszanie w prawo
                        self.rect.right =block.rect.left
                    if self.velocity.x < 0: # Poruszanie w prawo
                        self.rect.left =block.rect.right
        elif direction == "vertical":
            collisions = 0
            for block in self.block_group:
                if block.rect.colliderect(self.rect):
                    if self.velocity.y > 0: # Poruszanie w dół
                        self.rect.bottom =block.rect.top
                        collisions += 1
                    if self.velocity.y < 0: # Poruszanie w górę
                        self.rect.top =block.rect.bottom
            if collisions > 0:
                self.on_ground = True
            else:
                self.on_ground = False

    def move(self):
        self.velocity.y += GRAVITY * self.DT

        self.rect.y += self.velocity.y * self.DT
        self.check_collisions('vertical')

        self.rect.x += self.velocity.x
        self.check_collisions('horizontal')

        if self.velocity.y > MAX_Y_VELOCITY:
            self.velocity.y = MAX_Y_VELOCITY

        if self.velocity.x > MAX_X_VELOCITY:
            self.velocity.x = MAX_X_VELOCITY
        elif self.velocity.x < -MAX_X_VELOCITY:
            self.velocity.x = -MAX_X_VELOCITY

    def update(self):
        keys = pygame.key.get_pressed()

        if self.alive:
            if not self.on_ground:
                self.update_action(2) # Animacja skoku
            elif keys[pygame.K_a] or keys[pygame.K_d]:
                self.update_action(1) # Animacja biegania
            else:
                self.update_action(0) # Animacja stania

            if keys[pygame.K_a]:
                self.velocity.x -= self.speed * self.DT
            if keys[pygame.K_d]:
                self.velocity.x += self.speed * self.DT
            if not keys[pygame.K_a] and not keys[pygame.K_d]:
                self.velocity.x = 0

            if keys[pygame.K_SPACE] and self.on_ground and self.jump_cooldown == 0:
                self.velocity.y = self.jump_force
                self.jump_cooldown = 0.2 * self.DT  # Ustawienie opóźnienia skoku

            self.move()

        # Resetowanie gry jeśli gracz spadnie poza ekran
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.topleft = (100, SCREEN_HEIGHT - 100)
            self.velocity_y = 0

        # Zmniejszanie opóźnienia skoku
        if self.jump_cooldown > 0:
            self.jump_cooldown -= self.DT
            if self.jump_cooldown < 0:
                self.jump_cooldown = 0