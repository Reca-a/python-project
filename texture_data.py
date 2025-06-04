from settings import *

atlas_texture_data = {
    # Podstawowe bloki
    'grass': {'type':'block', 'position':(0,0), 'size':(TILE_SIZE, TILE_SIZE)},
    'stone': {'type':'block', 'position':(1,0), 'size':(TILE_SIZE, TILE_SIZE)},
    'dirt': {'type':'block', 'position':(0,1), 'size':(TILE_SIZE, TILE_SIZE)},

    # Drewno i liście
    'wood': {'position': (2, 0), 'size': (TILE_SIZE, TILE_SIZE)},
    'leaves': {'position': (2, 1), 'size': (TILE_SIZE, TILE_SIZE)},

    # Rudy
    'coal_ore': {'position': (1, 1), 'size': (TILE_SIZE, TILE_SIZE)},
    'iron_ore': {'position': (0, 2), 'size': (TILE_SIZE, TILE_SIZE)},
    'gold_ore': {'position': (1, 2), 'size': (TILE_SIZE, TILE_SIZE)},
    'diamond_ore': {'position': (2, 2), 'size': (TILE_SIZE, TILE_SIZE)},
}
solo_texture_data = {
    # Reimplementacja tekstur gracza (niezaimplementowana)
    # 'player_static': {'type':'player', 'file_path':'Assets/player/idle/0.png', 'size':(TILE_SIZE, TILE_SIZE)}
    'zombie_static': {'type':'enemy', 'file_path':'Assets/mobs/zombie.png', 'size':(TILE_SIZE, TILE_SIZE)}
}