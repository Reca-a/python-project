import random

import numpy as np
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
        self.atlas_textures = self.gen_atlas_textures('Assets/blocks/atlas.png')
        self.solo_textures = self.gen_solo_textures('Assets/mobs/zombie.png')

        # Ekwipunek
        self.inventory = Inventory(self.app, self.atlas_textures)

        # Stworzenie gracza
        self.player = Player([self.sprites], 0, 0, parameters={
                            'textures':self.atlas_textures, 'group_list': self.group_list, 'inventory':self.inventory})


        # Stworzenie moba
        Mob([self.sprites], pygame.transform.scale(pygame.image.load('Assets/mobs/zombie.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            (200, 400), parameters={'block_group':self.blocks, 'player':self.player, 'speed':5})

        # Generacja świata
        self.chunks: dict[tuple[int,int], Chunk] = {}
        self.active_chunks: dict[tuple[int,int], Chunk] = {}

        self.gen_world()

    def gen_solo_textures(self, file_path):
        textures = {}
        for name, data in solo_texture_data.items():
            textures[name] = pygame.transform.scale(pygame.image.load(data['file_path']).convert_alpha(), data['size'])
        return textures

    def gen_atlas_textures(self, file_path):
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
        # Pozycje chunków otaczających gracza
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
    def __init__(self, position: tuple[int, int], group_list: dict[str, pygame.sprite.Group], textures: dict[str, pygame.Surface]):
        self.position = position
        self.group_list = group_list
        self.textures = textures

        self.blocks: list[Entity] = []

        self.gen_chunk()

    def initialize_underworld_chunk(self, chunk_data):
        height = len(chunk_data)
        width = len(chunk_data[0])
        for x in range(height):
            for y in range(width):
                if random.random() <= CELLAUT_CHANCE_TO_STAY_ALIVE:
                    chunk_data[y][x] = 'stone'
        return chunk_data

    def count_alive_neighbors(self, chunk_data, x, y):
        alive_count = 0
        height = len(chunk_data)
        width = len(chunk_data[0])
        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbor_x = x + i
                neighbor_y = y + j
                if i == 0 and  j == 0:
                    continue
                elif neighbor_x < 0 or neighbor_y < 0 or neighbor_x >= height or neighbor_y >= width:
                    alive_count += 1
                elif chunk_data[neighbor_y][neighbor_x] == 'stone':
                    alive_count += 1
        return alive_count

    def cellaut_sim_step(self, old_chunk_data):
        new_chunk_data = np.empty((CHUNK_SIZE, CHUNK_SIZE), dtype=object)
        height = len(old_chunk_data)
        width = len(old_chunk_data[0])
        for x in range(height):
            for y in range(width):
                alive_neighbors = self.count_alive_neighbors(old_chunk_data, x, y)
                if old_chunk_data[y][x] == 'stone':
                    if alive_neighbors < CELLAUT_DEATH_LIMIT:
                        new_chunk_data[y][x] = 'air'
                    else:
                        new_chunk_data[y][x] = 'stone'
                else:
                    if alive_neighbors > CELLAUT_BIRTH_LIMIT:
                        new_chunk_data[y][x] = 'stone'
                    else:
                        new_chunk_data[y][x] = 'air'
        return new_chunk_data

    def gen_chunk(self):
        # Jeśli chunk znajduje się powyżej poziomu morza, bez generowania
        if self.position[1] < 0:
            self.blocks = []
            return

        # Inicjalizacja tablicy bloków
        chunk_data = np.full((CHUNK_SIZE, CHUNK_SIZE), 'air', dtype=object)

        # Jeśli chunk znajduje się na wysokości poziomu morza, generowanie terenu
        if self.position[1] == 0:
            noise_generator = OpenSimplex(seed=121343)
            heightmap = []

            for x in range(CHUNK_SIZE):
                noise_value = noise_generator.noise2(
                    (x + self.position[0] * CHUNK_SIZE) * 0.05,
                    self.position[1] * 0.1  # Dodatkowy parametr który zmienia wysokości w zależności od y
                )
                height = int((noise_value + 1) * 10 + 5)
                heightmap.append(height)

            # Wypełnianie chunka blokami terenu
            for x in range(CHUNK_SIZE):
                height = heightmap[x]
                for y in range(height):
                    if y == height - 1:
                        chunk_data[x, y] = 'grass'
                    elif y < height - 5:
                        chunk_data[x, y] = 'stone'
                    else:
                        chunk_data[x, y] = 'dirt'

        # Jeśli chunk znajduje się pod ziemią, tworzenie jaskiń
        if self.position[1] > 0:
            chunk_data = self.initialize_underworld_chunk(chunk_data)
            for _ in range(CELLAUT_NUMBER_OF_STEPS):
                chunk_data = self.cellaut_sim_step(chunk_data)

        # Dodanie bloków do listy self.blocks
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                if chunk_data[x, y] != 'air' and chunk_data[x, y]:  # Pominięcie powietrza
                    use_type = items[str(chunk_data[x, y])].use_type
                    groups = [self.group_list[str(group)] for group in items[str(chunk_data[x, y])].groups]
                    self.blocks.append(use_type(groups,
                                                self.textures[chunk_data[x, y]],
                                                (x * TILE_SIZE + CHUNK_PIXEL_SIZE * self.position[0],
                                                 (CHUNK_SIZE - y) * TILE_SIZE + CHUNK_PIXEL_SIZE * self.position[1]),
                                                chunk_data[x, y]))

    def load_chunk(self):
        for block in self.blocks:
            groups = [self.group_list[group] for group in items[block.name].groups]
            for group in groups:
                group.add(block)

    def unload_chunk(self):
        for block in self.blocks:
            block.kill()

    def get_chunk_pos(position: tuple[int, int]):
        return (position[0] // CHUNK_PIXEL_SIZE, position[1] // CHUNK_PIXEL_SIZE)
