import chunk

import pygame
from opensimplex import OpenSimplex

from inventory.inventory import Inventory
from settings import *
from sprite import Entity, Mob
from player import Player
from texture_data import atlas_texture_data, solo_texture_data
from camera import Camera
from items import *


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
        self.inventory = Inventory(self.app, self.atlas_textures)

        # Stworzenie gracza
        self.player = Player([self.sprites], 0, 0, parameters={
                            'textures':self.atlas_textures, 'group_list': self.group_list, 'inventory':self.inventory})


        # Stworzenie moba
        Mob([self.sprites], pygame.transform.scale(pygame.image.load('Assets/mobs/zombie.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            (200, 400), parameters={'block_group':self.blocks, 'player':self.player, 'speed':70})

        # Generacja świata
        self.chunks: dict[tuple[int,int], Chunk] = {}
        self.active_chunks: dict[tuple[int,int], Chunk] = {}

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
        pass

    def update(self):
        self.sprites.update()
        self.player.update_animation()
        self.inventory.update()

        player_chunk_pos = Chunk.get_chunk_pos(self.player.rect.center)
        positions = [
            (player_chunk_pos[0], player_chunk_pos[1] - 1),
            (player_chunk_pos[0] - 1, player_chunk_pos[1] - 1),
            (player_chunk_pos[0] + 1, player_chunk_pos[1] - 1),

            player_chunk_pos,
            (player_chunk_pos[0] - 1, player_chunk_pos[1]),
            (player_chunk_pos[0] + 1, player_chunk_pos[1]),

            (player_chunk_pos[0], player_chunk_pos[1] + 1),
            (player_chunk_pos[0] - 1, player_chunk_pos[1] + 1),
            (player_chunk_pos[0] + 1, player_chunk_pos[1] + 1),
        ]

        for position in positions:
            if position not in self.active_chunks:
                if position in self.chunks:
                    self.chunks[position].load_chunk()
                    self.active_chunks[position] = self.chunks[position]
                else:
                    self.chunks[position] = Chunk(position, self.group_list, self.atlas_textures)
                    self.active_chunks[position] = self.chunks[position]

        target = None
        for pos, chunk in self.active_chunks.items():
            if pos not in positions:
                target = pos
        if target:
            self.active_chunks[target].unload_chunk()
            self.active_chunks.pop(target)


    def draw(self):
        self.app.screen.fill('lightblue')
        self.sprites.draw(self.player, self.app.screen)
        self.inventory.draw()


class Chunk:
    CHUNK_SIZE = 30
    CHUNK_PIXEL_SIZE = CHUNK_SIZE * TILE_SIZE

    def __init__(self, position: tuple[int, int], group_list: dict[str, pygame.sprite.Group], textures: dict[str, pygame.Surface]):
        self.position = position
        self.group_list = group_list
        self.textures = textures

        self.blocks: list[Entity] = []

        self.gen_chunk()

    def gen_chunk(self):
        noise_generator = OpenSimplex(seed=121343)
        heightmap = []

        for y in range(Chunk.CHUNK_SIZE * self.position[0], Chunk.CHUNK_SIZE * self.position[0] + Chunk.CHUNK_SIZE):
            noise_value = noise_generator.noise2(y * 0.05, 0)
            height = int((noise_value + 1) * 4 + 5)
            heightmap.append(height)

        for x in range(len(heightmap)):
            if self.position[1] > 0:
                height_val = Chunk.CHUNK_SIZE
            elif self.position[1] < 0:
                height_val = 0
            else:
                height_val = heightmap[x]

            for y in range(height_val):

                # Wybór tekstury
                block_type = 'dirt'
                if y == heightmap[x] - 1:
                    block_type = 'grass'
                if y < heightmap[x] - 5:
                    block_type = 'stone'

                if self.position[1] > 0: # Tymczasowe rozwiązanie na kamień pod ziemią
                    block_type = 'stone'

                use_type = items[block_type].use_type
                groups = [self.group_list[group] for group in items[block_type].groups]
                self.blocks.append(use_type(groups,
                                    self.textures[block_type],
                                    (x * TILE_SIZE + Chunk.CHUNK_PIXEL_SIZE * self.position[0],
                                     (Chunk.CHUNK_SIZE - y) * TILE_SIZE + Chunk.CHUNK_PIXEL_SIZE * self.position[1]), block_type))

    def load_chunk(self):
        for block in self.blocks:
            groups = [self.group_list[group] for group in items[block.name].groups]
            for group in groups:
                group.add(block)

    def unload_chunk(self):
        for block in self.blocks:
            block.kill()

    def get_chunk_pos(position: tuple[int, int]):
        return (position[0] // Chunk.CHUNK_PIXEL_SIZE, position[1] // Chunk.CHUNK_PIXEL_SIZE)