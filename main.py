import sys
import pygame

from settings import *
from game_manager import GameManager


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)

        pygame.display.set_icon(pygame.image.load("Assets/mobs/zombie.png"))
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.game_manager = GameManager(self)

        self.game_manager.set_state('loader_menu')

    def handle_events(self):
        """Obsługuje wydarzenia systemowe i przekazuje je do GameManager"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and pygame.key.get_pressed()[pygame.K_LALT]:
                    self.running = False
                    return

                # Obsługa nawigacji w ekwipunku tylko gdy jesteśmy w grze
                if (self.game_manager.get_current_state() == 'game' and
                        self.game_manager.scene and
                        (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT)):
                    self.game_manager.scene.inventory.input(event)
                    continue

            result = self.game_manager.handle_event(event)
            if result:
                self._handle_game_manager_result(result)

    def _handle_game_manager_result(self, result):
        """Obsługuje wyniki zwracane przez GameManager"""
        action = result.get('action')

        if action == 'game_loaded':
            print("Gra została wczytana pomyślnie")
        elif action == 'world_created':
            print("Nowy świat został utworzony")
        elif action == 'back_to_menu':
            print("Powrót do menu głównego (nie ma)")
        elif action == 'load_error':
            error = result.get('error', 'Nieznany błąd')
            print(f"Błąd wczytywania gry: {error}")
        elif action == 'create_error':
            error = result.get('error', 'Nieznany błąd')
            print(f"Błąd tworzenia świata: {error}")

    def update(self):
        """Aktualizuje stan gry"""
        self.handle_events()
        self.game_manager.update()
        pygame.display.update()

    def draw(self):
        """Rysuje aktualny stan gry"""
        self.screen.fill('lightblue')
        self.game_manager.draw()
        pygame.display.flip()

    def close(self):
        """Zamyka grę i zapisuje dane"""
        if (self.game_manager.get_current_state() == 'game' and
                self.game_manager.scene):
            try:
                self.game_manager.scene.save_world_data()
                print("Dane gry zostały zapisane przed zamknięciem")
            except:
                print("Błąd podczas zapisywania danych")

        pygame.quit()
        sys.exit()

    def create_new_world(self, world_name: str = None):
        """Tworzy nowy świat i przełącza do trybu gry"""
        result = self.game_manager.create_new_world(world_name)
        self._handle_game_manager_result(result)

    def load_game_menu(self):
        """Przełącza do menu wczytywania gry"""
        self.game_manager.set_state('loader_menu')

    def run(self):
        while self.running:
            DT = get_DT(self.clock) / 60

            self.update()
            self.draw()

        self.close()


# Uruchomienie gry
if __name__ == "__main__":
    game = Game()
    game.run()