import pygame
import math

from settings import *


class Entity(pygame.sprite.Sprite):
    def __init__(self, groups, image = pygame.Surface((TILE_SIZE, TILE_SIZE)), position = (0,0), name: str = "default"):
        super().__init__(groups)
        self.name = name
        self.active_groups = groups
        self.image = image
        self.rect = self.image.get_rect(topleft = position)
        self.clock = pygame.time.Clock()

    def update(self):
        pass

class Mob(Entity):
    def __init__(self, groups, image = pygame.Surface((TILE_SIZE, TILE_SIZE)), position = (0,0), parameters = {}):
        super().__init__(groups, image, position)
        self.DT = get_DT(pygame.time.Clock())

        if parameters:
            self.block_group = parameters['block_group']
            self.speed = parameters['speed']
            self.player = parameters['player']

        self.velocity = pygame.math.Vector2()

        # Stany
        self.attacking = True
        self.is_grounded = False

    def check_collisions(self, direction):
        if direction == "horizontal":
            for block in self.block_group:
                if block.rect.colliderect(self.rect):
                    if self.velocity.x > 0: # Poruszanie w prawo
                        self.rect.right = block.rect.left
                    if self.velocity.x < 0: # Poruszanie w prawo
                        self.rect.left = block.rect.right
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
                self.is_grounded = True
            else:
                self.is_grounded = False

    def move(self):
        self.velocity.y += GRAVITY * self.DT

        if self.velocity.y > MAX_Y_VELOCITY:
            self.velocity.y = MAX_Y_VELOCITY

        if self.velocity.x > MAX_X_VELOCITY:
            self.velocity.x = MAX_X_VELOCITY
        elif self.velocity.x < -MAX_X_VELOCITY:
            self.velocity.x = -MAX_X_VELOCITY

        # Sprawdzenie odległości do gracza
        if abs(math.sqrt((self.rect.x - self.player.rect.x)**2 + (self.rect.y - self.player.rect.y)**2)) < TILE_SIZE * 10:
            if self.rect.x > self.player.rect.x:
                self.velocity.x -= self.speed * self.DT
            elif self.rect.x < self.player.rect.x:
                self.velocity.x += self.speed * self.DT
            self.attacking = True
        else:
            self.attacking = False
            self.velocity.x = 0

        if self.is_grounded and self.attacking and abs(self.velocity.x) < 1:
            self.velocity.y = - 300

        self.rect.y += self.velocity.y * self.DT
        self.check_collisions('vertical')

        self.rect.x += self.velocity.x
        self.check_collisions('horizontal')

    def update(self):
        self.move()