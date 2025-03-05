# Delta time
def get_DT(clock):
    return clock.tick(FPS) / 1000

# Stałe ekranu
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
FPS = 60
SCALE = 1
TILE_SIZE = 16

#Stałe gry
ANIMATION_COOLDOWN = 300
GRAVITY = 1000
MAX_Y_VELOCITY = 300
MAX_X_VELOCITY = 0.1