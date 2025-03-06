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
        self.group_list = parameters['group_list']
        self.textures = parameters['textures']
        self.block_group = self.group_list['block_group']
        self.inventory = parameters['inventory']

        # Wartości fizyczne
        self.velocity = pygame.math.Vector2()
        self.speed = 150
        self.is_grounded = False
        self.jump_cooldown = 0
        self.jump_force = -450
        self.DT = get_DT(self.clock)

    def update_animation(self):
        self.image = pygame.transform.flip(self.animation_list[self.action][self.frame_index], self.flip, False)
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
                self.is_grounded = True
            else:
                self.is_grounded = False

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

    def input(self, keys):
        if not self.is_grounded:
            self.update_action(2)  # Animacja skoku
        elif keys[pygame.K_a] or keys[pygame.K_d]:
            self.update_action(1)  # Animacja biegania
        else:
            self.update_action(0)  # Animacja stania

        if keys[pygame.K_a]:
            self.velocity.x -= self.speed * self.DT
            self.flip = True
        if keys[pygame.K_d]:
            self.velocity.x += self.speed * self.DT
            self.flip = False
        if not keys[pygame.K_a] and not keys[pygame.K_d]:
            self.velocity.x = 0

        if keys[pygame.K_SPACE] and self.is_grounded and self.jump_cooldown == 0:
            self.velocity.y = self.jump_force
            self.jump_cooldown = 0.2 * self.DT  # Ustawienie opóźnienia skoku

    # Funkcja zwracająca pozycję myszki z uwzględnieniem przesunięcia kamery
    def get_adjusted_mouse_pos(self) -> tuple:
        mouse_pos = pygame.mouse.get_pos()
        player_offset = pygame.math.Vector2()
        player_offset.x = SCREEN_WIDTH / 2 - self.rect.centerx
        player_offset.y = SCREEN_HEIGHT / 2 - self.rect.centery

        return (mouse_pos[0] - player_offset.x, mouse_pos[1] - player_offset.y)

    # Funkcja pomagająca ustawić blok w siatce (gridzie)
    def get_block_pos(self, mouse_pos: tuple):
        return (int ((mouse_pos[0]//TILE_SIZE)*TILE_SIZE), int ((mouse_pos[1]//TILE_SIZE)*TILE_SIZE))

    def block_handling(self, keys):
        state = pygame.mouse.get_pressed()
        mouse_pos = self.get_adjusted_mouse_pos()
        placed = False
        collision = False

        if any(state): # pygame.mouse.get_pressed() zwraca listę w której LMB ma indeks 0 i RMB 2
            for block in self.block_group:
                if block.rect.collidepoint(mouse_pos):
                    collision = True
                    if state[0]: # Niszczenie bloku
                        self.inventory.add_item(block)
                        block.kill()
            if state[2] and not collision: # Stawianie bloku
                placed = True
        if placed:
            self.inventory.use(self, self.get_block_pos(mouse_pos))

    def update(self):
        keys = pygame.key.get_pressed()

        if self.alive:
            self.input(keys)
            self.move()
            self.block_handling(keys)

        # Resetowanie gry jeśli gracz spadnie poza ekran
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.topleft = (100, SCREEN_HEIGHT - 100)
            self.velocity_y = 0

        # Zmniejszanie opóźnienia skoku
        if self.jump_cooldown > 0:
            self.jump_cooldown -= self.DT
            if self.jump_cooldown < 0:
                self.jump_cooldown = 0