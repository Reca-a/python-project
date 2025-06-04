import random
from chunk import Chunk
from pathlib import Path
import time
from collections import deque
import numpy as np
from opensimplex import OpenSimplex

from inventory.inventory import Inventory
from sprites.player import Player
from texture_data import atlas_texture_data, solo_texture_data
from sprites.camera import Camera
from inventory.items import *
from world_manager import WorldManager


class Scene:
    def __init__(self, app, world_name: str = 'default_world', save_path: Path = None) -> None:
        self.app = app
        self.game_version = '0.2.0'
        self.sprites = Camera()
        self.blocks = pygame.sprite.Group()
        self.group_list: dict[str, pygame.sprite.Group] = {
            'sprites': self.sprites,
            'block_group': self.blocks
        }

        # Zasięg renderowania chunków
        self.chunk_render_distance = 3

        # Wczytanie tekstur
        self.atlas_textures = self.gen_atlas_textures('Assets/blocks/atlas.png')
        self.solo_textures = self.gen_solo_textures('Assets/mobs/zombie.png')

        # Ekwipunek
        self.inventory = Inventory(self.app, self.atlas_textures)

        # Inicjalizacja World Manager
        self.world_manager = self._initialize_world_manager(world_name, save_path)

        # Seed z world managera
        world_info = self.world_manager.get_world_info()
        self.world_seed = world_info['seed']

        # Stworzenie gracza
        self.player = Player([self.sprites], 0, 0, parameters={
            'textures': self.atlas_textures, 'group_list': self.group_list, 'inventory': self.inventory})

        # Stworzenie moba
        Mob([self.sprites],
            pygame.transform.scale(pygame.image.load('Assets/mobs/zombie.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            (200, 400), parameters={'block_group': self.blocks, 'player': self.player, 'speed': 5})

        # Generacja świata
        self.chunks: dict[tuple[int, int], Chunk] = {}
        self.active_chunks: dict[tuple[int, int], Chunk] = {}

        # Asynchroniczne ładowanie chunków
        self.chunk_load_queue = deque()

        # Automatyczne zapisywanie co 30 sekund
        self.last_save_time = time.time()
        self.auto_save_interval = 30

    def _initialize_world_manager(self, world_name: str = None, save_path: Path = None) -> WorldManager:
        """Inicjalizuje WorldManager"""
        if save_path:
            world_name = save_path.stem
            return WorldManager(world_name, self.game_version)
        else:
            world_name = world_name or "default_world"
            return WorldManager(world_name, self.game_version)

    @classmethod
    def load_from_save(cls, app, save_path: Path):
        """Tworzy Scene z zapisanego pliku"""
        return cls(app, save_path=save_path)

    @classmethod
    def create_new_world(cls, app, world_name: str = None):
        """Tworzy nowy świat"""
        return cls(app, world_name=world_name)

    def load_chunk_data(self, chunk_pos: tuple[int, int]) -> dict:
        """Wczytuje dane chunka przez WorldManager"""
        return self.world_manager.load_chunk_data(chunk_pos)

    def save_world_data(self):
        """Zapisuje wszystkie dane świata przez WorldManager"""
        self.world_manager.save_world_data(self.chunks)

    def gen_solo_textures(self, file_path):
        textures = {}
        for name, data in solo_texture_data.items():
            textures[name] = pygame.transform.scale(pygame.image.load(data['file_path']).convert_alpha(), data['size'])
        return textures

    def gen_atlas_textures(self, file_path):
        textures = {}
        atlas_img = pygame.transform.scale(pygame.image.load(file_path).convert_alpha(),
                                           (TILE_SIZE * 16, TILE_SIZE * 16))

        for name, data in atlas_texture_data.items():
            textures[name] = pygame.Surface.subsurface(atlas_img, pygame.Rect(data['position'][0] * TILE_SIZE,
                                                                              data['position'][1] * TILE_SIZE,
                                                                              data['size'][0],
                                                                              data['size'][1]))
        return textures

    def get_chunks_in_range(self, center_pos: tuple[int, int], distance: int) -> list[tuple[int, int]]:
        """Zwraca listę pozycji chunków w określonym zasięgu od centrum"""
        positions = []
        for x in range(center_pos[0] - distance, center_pos[0] + distance + 1):
            for y in range(center_pos[1] - distance, center_pos[1] + distance + 1):
                positions.append((x, y))
        return positions

    def get_chunks_by_priority(self, center_pos: tuple[int, int], positions: list) -> list:
        """Sortuje chunki według odległości od gracza (najbliższe najpierw)"""

        def distance_to_player(pos):
            return abs(pos[0] - center_pos[0]) + abs(pos[1] - center_pos[1])

        return sorted(positions, key=distance_to_player)

    def update(self):
        self.sprites.update()
        self.player.update_animation()
        self.inventory.update()

        player_chunk_pos = Chunk.get_chunk_pos(self.player.rect.center)

        # Generuj pozycje chunków w zasięgu renderowania
        positions = self.get_chunks_in_range(player_chunk_pos, self.chunk_render_distance)
        positions = self.get_chunks_by_priority(player_chunk_pos, positions)

        chunks_loaded_this_frame = 0
        max_chunks_per_frame = 2

        for position in positions:
            if position not in self.active_chunks:
                if chunks_loaded_this_frame >= max_chunks_per_frame:
                    if position not in self.chunk_load_queue:
                        self.chunk_load_queue.append(position)
                    continue

                if position in self.chunks:
                    self.chunks[position].load_chunk()
                    self.active_chunks[position] = self.chunks[position]
                else:
                    self.chunks[position] = Chunk(position, self.group_list, self.atlas_textures, self.world_seed, self)
                    self.active_chunks[position] = self.chunks[position]

                chunks_loaded_this_frame += 1

        # Przetworzenie kolejki ładowania chunków
        while self.chunk_load_queue and chunks_loaded_this_frame < max_chunks_per_frame:
            position = self.chunk_load_queue.popleft()
            if position not in self.active_chunks and position in positions:
                if position in self.chunks:
                    self.chunks[position].load_chunk()
                    self.active_chunks[position] = self.chunks[position]
                else:
                    self.chunks[position] = Chunk(position, self.group_list, self.atlas_textures, self.world_seed, self)
                    self.active_chunks[position] = self.chunks[position]
                chunks_loaded_this_frame += 1

        # Rozładowywanie chunków poza zasięgiem
        chunks_to_unload = [pos for pos, chunk in self.active_chunks.items() if pos not in positions]

        # Ograniczenie rozładowywania chunków na klatkę
        max_unload_per_frame = 3
        for i, pos in enumerate(chunks_to_unload):
            if i >= max_unload_per_frame:
                break
            self.active_chunks[pos].unload_chunk()
            self.active_chunks.pop(pos)

        # Automatyczne zapisywanie
        current_time = time.time()
        if current_time - self.last_save_time > self.auto_save_interval:
            self.save_world_data()
            self.last_save_time = current_time

    def draw(self):
        self.app.screen.fill('lightblue')
        self.sprites.draw(self.player, self.app.screen)
        self.inventory.draw()

    def set_render_distance(self, distance: int):
        """Pozwala na dynamiczną zmianę zasięgu renderowania (niezaimplementowane)"""
        if distance > 0:
            self.chunk_render_distance = distance

    def get_active_chunks_count(self) -> int:
        """Zwraca liczbę aktualnie załadowanych chunków"""
        return len(self.active_chunks)

    def get_world_info(self) -> dict:
        """Zwraca informacje o aktualnym świecie"""
        return self.world_manager.get_world_info()

    def __del__(self):
        """Zapisz dane przy zamykaniu"""
        try:
            self.save_world_data()
        except:
            pass


class Chunk:
    def __init__(self, position: tuple[int, int], group_list: dict[str, pygame.sprite.Group],
                 textures: dict[str, pygame.Surface], world_seed: int, scene):
        self.position = position
        self.group_list = group_list
        self.textures = textures
        self.world_seed = world_seed
        self.scene = scene
        self.blocks: list[Entity] = []
        self.noise_generator = OpenSimplex(seed=world_seed)

        # Próba wczytania zapisanego chunka
        saved_data = self.scene.load_chunk_data(position)
        if saved_data:
            self.load_from_data(saved_data)
        else:
            self.gen_chunk()

    def load_from_data(self, data: dict):
        """Wczytuje chunk z zapisanych danych"""
        for block_info in data.get('blocks', []):
            name = block_info['name']
            x = block_info['x']
            y = block_info['y']

            if name and name != 'air':
                try:
                    item_data = registry.get_data(name)
                    use_type = item_data.use_type
                    groups = [self.group_list[group] for group in item_data.groups]
                    block = use_type(groups, self.textures[name], (x, y), name)
                    self.blocks.append(block)
                except KeyError:
                    continue

    def get_save_data(self):
        """Zwraca dane chunka do zapisu"""
        data = {
            'position': self.position,
            'blocks': []
        }

        for block in self.blocks:
            data['blocks'].append({
                'name': block.name,
                'x': block.rect.x,
                'y': block.rect.y
            })

        return data

    def initialize_underground_chunk(self, chunk_data):
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
                if i == 0 and j == 0:
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

    def generate_trees(self, chunk_data, heightmap):
        """Generuje drzewa na powierzchni terenu"""
        for x in range(CHUNK_SIZE):
            tree_noise = self.noise_generator.noise2(
                (x + self.position[0] * CHUNK_SIZE) * 0.25,
                self.position[1] * 0.1
            )

            random_factor = random.random() * 0.3
            tree_chance = tree_noise + random_factor

            if tree_chance > 0.5 and heightmap[x] > 5:
                tree_height = random.randint(4, 8)
                ground_level = heightmap[x]

                if ground_level + tree_height >= CHUNK_SIZE:
                    tree_height = CHUNK_SIZE - ground_level - 1

                # Pień drzewa
                for trunk_y in range(ground_level, min(ground_level + tree_height, CHUNK_SIZE)):
                    if trunk_y < CHUNK_SIZE:
                        chunk_data[x, trunk_y] = 'wood'

                # Korona drzewa
                crown_start = max(0, min(ground_level + tree_height - 3, CHUNK_SIZE - 1))
                crown_size = random.randint(2, 3)

                for crown_x in range(max(0, x - crown_size), min(CHUNK_SIZE, x + crown_size + 1)):
                    for crown_y in range(crown_start, min(crown_start + crown_size + 2, CHUNK_SIZE)):
                        distance = ((crown_x - x) ** 2 + (crown_y - crown_start - crown_size // 2) ** 2) ** 0.5
                        if distance <= crown_size and chunk_data[crown_x, crown_y] == 'air':
                            if random.random() > 0.15:
                                chunk_data[crown_x, crown_y] = 'leaves'

    def generate_ores(self, chunk_data):
        """Generuje rudy w podziemnych chunkach"""
        if self.position[1] <= 0:
            return

        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                if chunk_data[x, y] == 'stone':
                    ore_noise = self.noise_generator.noise3(
                        (x + self.position[0] * CHUNK_SIZE) * 0.1,
                        (y + self.position[1] * CHUNK_SIZE) * 0.1,
                        self.position[1] * 0.5
                    )

                    depth = self.position[1]

                    if ore_noise > COAL_GENERATION_THRESHOLD:
                        chunk_data[x, y] = 'coal_ore'
                    elif ore_noise > IRON_GENERATION_THRESHOLD and depth >= 2:
                        chunk_data[x, y] = 'iron_ore'
                    elif ore_noise > GOLD_GENERATION_THRESHOLD and depth >= 4:
                        chunk_data[x, y] = 'gold_ore'
                    elif ore_noise > DIAMOND_GENERATION_THRESHOLD and depth >= 6:
                        chunk_data[x, y] = 'diamond_ore'

    def gen_chunk(self):
        if self.position[1] < 0:
            self.blocks = []
            return

        chunk_data = np.full((CHUNK_SIZE, CHUNK_SIZE), 'air', dtype=object)

        if self.position[1] == 0:
            heightmap = []

            for x in range(CHUNK_SIZE):
                noise_value = self.noise_generator.noise2(
                    (x + self.position[0] * CHUNK_SIZE) * 0.05,
                    self.position[1] * 0.1
                )
                height = int((noise_value + 1) * 10 + 5)
                heightmap.append(height)

            for x in range(CHUNK_SIZE):
                height = heightmap[x]
                for y in range(height):
                    if y == height - 1:
                        chunk_data[x, y] = 'grass'
                    elif y < height - 5:
                        chunk_data[x, y] = 'stone'
                    else:
                        chunk_data[x, y] = 'dirt'

            self.generate_trees(chunk_data, heightmap)

        if self.position[1] > 0:
            chunk_data = self.initialize_underground_chunk(chunk_data)
            for _ in range(CELLAUT_NUMBER_OF_STEPS):
                chunk_data = self.cellaut_sim_step(chunk_data)
            self.generate_ores(chunk_data)

        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                if chunk_data[x, y] != 'air' and chunk_data[x, y]:
                    name = chunk_data[x, y]
                    if name and name != 'air':
                        try:
                            item_data = registry.get_data(name)
                            use_type = item_data.use_type
                            groups = [self.group_list[group] for group in item_data.groups]
                            world_x = x * TILE_SIZE + CHUNK_PIXEL_SIZE * self.position[0]
                            world_y = (CHUNK_SIZE - y) * TILE_SIZE + CHUNK_PIXEL_SIZE * self.position[1]
                            block = use_type(groups, self.textures[name], (world_x, world_y), name)
                            self.blocks.append(block)
                        except KeyError:
                            continue

    def load_chunk(self):
        for block in self.blocks:
            try:
                item_data = registry.get_data(block.name)
                for group_name in item_data.groups:
                    self.group_list[group_name].add(block)
            except KeyError:
                continue

    def unload_chunk(self):
        for block in self.blocks:
            block.kill()

    @staticmethod
    def get_chunk_pos(position: tuple[int, int]):
        return (position[0] // CHUNK_PIXEL_SIZE, position[1] // CHUNK_PIXEL_SIZE)