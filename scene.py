import pygame
from opensimplex import OpenSimplex

from inventory.inventory import Inventory
from settings import *
from sprite import Entity, Mob
from player import Player
from texture_data import atlas_texture_data, solo_texture_data
from camera import Camera


class Scene:
    def __init__(self, app) -> None:
        self.app = app
        self.sprites = Camera()
        self.blocks = pygame.sprite.Group()
        self.group_list: dict[str, pygame.sprite.Group] = {
            'sprites': self.sprites,
            'block_group': self.blocks
        }

        # Wczytanie tekstur
        self.atlas_textures = self.gen_altas_textures('Assets/blocks/atlas.png')
        self.solo_textures = self.gen_solo_textures('Assets/mobs/zombie.png')

        # Ekwipunek
        self.inventory = Inventory(self.app)

        # Stworzenie gracza
        self.player = Player([self.sprites], 150, SCREEN_HEIGHT - 200, parameters={
                            'textures':self.atlas_textures, 'group_list': self.group_list, 'inventory':self.inventory})


        # Stworzenie moba
        Mob([self.sprites], pygame.transform.scale(pygame.image.load('Assets/mobs/zombie.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            (200, 400), parameters={'block_group':self.blocks, 'player':self.player, 'speed':70})

        # Generacja świata
        self.gen_world()

    def gen_solo_textures(self, file_path):
        textures = {}
        for name, data in solo_texture_data.items():
            textures[name] = pygame.transform.scale(pygame.image.load(data['file_path']).convert_alpha(), data['size'])
        return textures

    def gen_altas_textures(self, file_path):
        textures = {}
        atlas_img = pygame.transform.scale(pygame.image.load(file_path).convert_alpha(), (TILE_SIZE * 16, TILE_SIZE * 16))

        for name, data in atlas_texture_data.items():
            textures[name] = pygame.Surface.subsurface(atlas_img, pygame.Rect(data['position'][0] * TILE_SIZE,
                                                                              data['position'][1] * TILE_SIZE,
                                                                              data['size'][0],
                                                                              data['size'][1]))
        return textures

    # Generowanie świata
    def gen_world(self):
        noise_generator = OpenSimplex(seed=92413458)
        heightmap = []

        for y in range(60):
            noise_value = noise_generator.noise2(y * 4, 0)
            height = int((noise_value + 1) * 4 + 5)
            heightmap.append(height)

        for x in range(len(heightmap)):
            for y in range(heightmap[x]):
                y_offset = 5 - y + 34

                # Wybór tekstury
                block_type = 'dirt'
                if y == heightmap[x] - 1:
                    block_type = 'grass'
                if y < heightmap[x] - 5:
                    block_type = 'stone'

                Entity([self.sprites, self.blocks], self.atlas_textures[block_type], (x * TILE_SIZE, y_offset * TILE_SIZE), name=block_type)

    def update(self):
        self.sprites.update()
        self.player.update_animation()
        self.inventory.update()

    def draw(self):
        self.app.screen.fill('lightblue')
        self.sprites.draw(self.player, self.app.screen)
        self.inventory.draw()
