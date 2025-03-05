from settings import *

atlas_texture_data = {
    'grass': {'type':'block', 'size':(TILE_SIZE, TILE_SIZE), 'position':(0,0)},
    'stone': {'type':'block', 'size':(TILE_SIZE, TILE_SIZE), 'position':(1,0)},
    'dirt': {'type':'block', 'size':(TILE_SIZE, TILE_SIZE), 'position':(0,1)}
}
solo_texture_data = {
    # Reimplementacja tekstur gracza
    # 'player_static': {'type':'player', 'file_path':'Assets/player/idle/0.png', 'size':(TILE_SIZE, TILE_SIZE)}
    'zombie_static': {'type':'enemy', 'file_path':'Assets/mobs/zombie.png', 'size':(TILE_SIZE, TILE_SIZE)}
}