import sys
import pygame

from settings import *
from scene import Scene


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = Scene(self)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
                self.scene.inventory.input(event)

        self.scene.update()

        pygame.display.update()

    def draw(self):
        self.scene.draw()
        pygame.display.flip()

    def close(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while self.running:
            DT = get_DT(self.clock) / 60
            self.update()
            self.draw()
        self.close()


game = Game()
game.run()
