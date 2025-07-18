# Delta time
def get_DT(clock):
    return clock.tick(FPS) / 1000

# Stałe ekranu
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
FPS = 60
SCALE = 1
TILE_SIZE = 16
CHUNK_SIZE = 30
CHUNK_PIXEL_SIZE = CHUNK_SIZE * TILE_SIZE

# Stałe gry
GAME_TITLE = "Terraria from Temu"
ANIMATION_COOLDOWN = 300
GRAVITY = 1000
MAX_Y_VELOCITY = 300
MAX_X_VELOCITY = 4

# Stałe generowania jaskiń za pomocą techniki cellular automata
CELLAUT_CHANCE_TO_STAY_ALIVE = 0.7
CELLAUT_DEATH_LIMIT = 5
CELLAUT_BIRTH_LIMIT = 6
CELLAUT_NUMBER_OF_STEPS = 4

# Stałe generowania drzew
TREE_GENERATION_THRESHOLD = 0.6  # Im wyższa wartość, tym mniej drzew

# Stałe generowania rud (im niższa wartość, tym rzadsze rudy)
COAL_GENERATION_THRESHOLD = 0.7     # Węgiel - najczęstszy
IRON_GENERATION_THRESHOLD = 0.8     # Żelazo - średnio rzadkie
GOLD_GENERATION_THRESHOLD = 0.85    # Złoto - rzadkie
DIAMOND_GENERATION_THRESHOLD = 0.9  # Diamenty - najrzadsze