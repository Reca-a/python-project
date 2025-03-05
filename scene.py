import pygame
from opensimplex import OpenSimplex
from settings import *
from sprite import Entity
from player import Player
from texture_data import atlas_texture_data
from camera import Camera


class Scene:
    def __init__(self, app) -> None:
        self.app = app
        self.sprites = Camera()
        self.blocks = pygame.sprite.Group()

        # Wczytanie tekstur
        self.atlas_textures = self.gen_altas_textures('Assets/blocks/atlas.png')

        # Stworzenie gracza
        self.player = Player([self.sprites], 150, SCREEN_HEIGHT - 200, parameters={'block_group': self.blocks})

        # Generacja świata
        self.gen_world()

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

        for y in range(20):
            noise_value = noise_generator.noise2(y * 4, 0)
            height = int((noise_value + 1) * 4 + 5)
            heightmap.append(height)

        for x in range(len(heightmap)):
            for y in range(heightmap[x]):
                y_offset = 5 - y + 34

                # Wybór tekstury
                texture = self.atlas_textures['dirt']
                if y == heightmap[x] - 1:
                    texture = self.atlas_textures['grass']
                if y < heightmap[x] - 5:
                    texture = self.atlas_textures['stone']

                Entity([self.sprites, self.blocks], texture, (x * TILE_SIZE, y_offset * TILE_SIZE))

    def update(self):
        self.sprites.update()
        self.player.update_animation()

    def draw(self):
        self.app.screen.fill('lightblue')
        self.sprites.draw(self.player, self.app.screen)
