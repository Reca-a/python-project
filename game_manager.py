import pygame
import json
import gzip
from pathlib import Path
from datetime import datetime
from typing import List


class SaveGameData:
    """Klasa reprezentująca dane zapisanej gry"""

    def __init__(self, save_path: Path):
        self.save_path = save_path
        self.world_name = save_path.stem
        self.is_valid = False
        self.metadata = {}
        self.last_played = None
        self.chunk_count = 0

        self._load_metadata()

    def _load_metadata(self):
        """Wczytuje metadane zapisu"""
        try:
            if self.save_path.suffix == '.dat':
                with gzip.open(self.save_path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)

                metadata = data.get('metadata', {})
                self.metadata = metadata
                self.last_played = datetime.fromtimestamp(metadata.get('last_modified', 0))
                self.chunk_count = metadata.get('chunk_count', 0)
                self.is_valid = True

        except Exception as e:
            print(f"Błąd wczytywania metadanych dla {self.save_path}: {e}")
            self.is_valid = False

    def get_display_name(self) -> str:
        """Zwraca nazwę do wyświetlenia"""
        return self.metadata.get('world_name', self.world_name)

    def get_info_text(self) -> List[str]:
        """Zwraca informacje o zapisie"""
        info = []
        info.append(f"Nazwa: {self.get_display_name()}")
        if self.last_played:
            info.append(f"Ostatnio grane: {self.last_played.strftime('%Y-%m-%d %H:%M')}")
        info.append(f"Chunków: {self.chunk_count}")
        version = self.metadata.get('version', 'nieznana')
        info.append(f"Wersja: {version}")
        return info


class GameLoaderMenu:
    """Menu do wczytywania zapisanych gier"""

    def __init__(self, app):
        self.app = app
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)

        # Kolory
        self.bg_color = (30, 30, 30)
        self.panel_color = (50, 50, 50)
        self.selected_color = (70, 130, 180)
        self.text_color = (255, 255, 255)
        self.button_color = (60, 60, 60)
        self.button_hover_color = (80, 80, 80)

        # Stan menu
        self.saves: List[SaveGameData] = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible_saves = 8

        self.save_list_rect = pygame.Rect(50, 100, 500, 400)
        self.info_panel_rect = pygame.Rect(600, 100, 350, 400)

        self.buttons = {
            'load': pygame.Rect(50, 530, 120, 60),
            'delete': pygame.Rect(190, 530, 120, 60),
            'create': pygame.Rect(800, 530, 150, 60),
            'refresh': pygame.Rect(330, 530, 120, 60)
        }

        self.button_states = {key: False for key in self.buttons.keys()}
        self.refresh_saves()

    def refresh_saves(self):
        """Odświeża listę dostępnych zapisów"""
        self.saves.clear()
        saves_dir = Path("saves")

        if saves_dir.exists():
            for save_file in saves_dir.iterdir():
                if save_file.is_file() and save_file.suffix == '.dat':
                    save_data = SaveGameData(save_file)
                    if save_data.is_valid:
                        self.saves.append(save_data)

        # Sortuowanie według daty ostatniego grania
        self.saves.sort(key=lambda x: x.last_played or datetime.min, reverse=True)

        if self.saves:
            self.selected_index = min(self.selected_index, len(self.saves) - 1)
        else:
            self.selected_index = 0

    def handle_event(self, event):
        """Obsługuje wydarzenia"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
                self._update_scroll()

            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(self.saves) - 1, self.selected_index + 1)
                self._update_scroll()

            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.saves:
                    return self._load_selected_game()

            elif event.key == pygame.K_DELETE:
                if self.saves:
                    return self._delete_selected_save()

            elif event.key == pygame.K_ESCAPE:
                return {'action': 'back'}

            elif event.key == pygame.K_F5:
                self.refresh_saves()

            elif event.key == pygame.K_n:
                return {'action': 'create_world'}

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos

                if self.save_list_rect.collidepoint(mouse_pos):
                    relative_y = mouse_pos[1] - self.save_list_rect.y
                    clicked_index = (relative_y // 50) + self.scroll_offset
                    if 0 <= clicked_index < len(self.saves):
                        self.selected_index = clicked_index

                for button_name, button_rect in self.buttons.items():
                    if button_rect.collidepoint(mouse_pos):
                        return self._handle_button_click(button_name)

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            for button_name, button_rect in self.buttons.items():
                self.button_states[button_name] = button_rect.collidepoint(mouse_pos)

        elif event.type == pygame.MOUSEWHEEL:
            # Scrollowanie w liście zapisów
            if self.save_list_rect.collidepoint(pygame.mouse.get_pos()):
                if event.y > 0:  # Scroll w górę
                    self.selected_index = max(0, self.selected_index - 1)
                elif event.y < 0:  # Scroll w dół
                    self.selected_index = min(len(self.saves) - 1, self.selected_index + 1)
                self._update_scroll()

        return None

    def _update_scroll(self):
        """Aktualizuje offset scrollowania"""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_saves:
            self.scroll_offset = self.selected_index - self.max_visible_saves + 1

    def _handle_button_click(self, button_name: str):
        """Obsługuje kliknięcie przycisku"""
        if button_name == 'load':
            if self.saves:
                return self._load_selected_game()
        elif button_name == 'delete':
            if self.saves:
                return self._delete_selected_save()
        elif button_name == 'create':
            return {'action': 'create_world'}
        elif button_name == 'refresh':
            self.refresh_saves()

        return None

    def _load_selected_game(self):
        """Wczytuje wybraną grę"""
        if 0 <= self.selected_index < len(self.saves):
            selected_save = self.saves[self.selected_index]
            return {
                'action': 'load_game',
                'save_path': selected_save.save_path
            }
        return None

    def _delete_selected_save(self):
        """Usuwa wybrany zapis"""
        if 0 <= self.selected_index < len(self.saves):
            selected_save = self.saves[self.selected_index]
            try:
                selected_save.save_path.unlink()

                backup_path = selected_save.save_path.with_suffix('.dat.backup')
                if backup_path.exists():
                    backup_path.unlink()

                print(f"Usunięto zapis: {selected_save.get_display_name()}")

                self.refresh_saves()

                return {'action': 'save_deleted'}

            except Exception as e:
                print(f"Błąd usuwania zapisu: {e}")
                return {'action': 'delete_error', 'error': str(e)}

        return None

    def draw(self):
        """Rysuje menu"""
        self.app.screen.fill(self.bg_color)

        # Tytuł
        title_text = self.title_font.render("Wczytaj Grę", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.app.screen.get_width() // 2, 50))
        self.app.screen.blit(title_text, title_rect)

        # Panel z listą zapisów
        pygame.draw.rect(self.app.screen, self.panel_color, self.save_list_rect)
        pygame.draw.rect(self.app.screen, self.text_color, self.save_list_rect, 2)

        # Lista zapisów
        if self.saves:
            for i, save_data in enumerate(self.saves[self.scroll_offset:self.scroll_offset + self.max_visible_saves]):
                actual_index = i + self.scroll_offset
                y_pos = self.save_list_rect.y + i * 50

                # Tło elementu listy
                item_rect = pygame.Rect(self.save_list_rect.x + 5, y_pos + 5, self.save_list_rect.width - 10, 40)

                if actual_index == self.selected_index:
                    pygame.draw.rect(self.app.screen, self.selected_color, item_rect)

                pygame.draw.rect(self.app.screen, self.text_color, item_rect, 1)

                # Nazwa świata
                name_text = self.font.render(save_data.get_display_name(), True, self.text_color)
                self.app.screen.blit(name_text, (item_rect.x + 10, item_rect.y + 5))

                # Data ostatniej gry
                if save_data.last_played:
                    date_text = self.small_font.render(
                        save_data.last_played.strftime('%d.%m.%Y %H:%M'),
                        True, (200, 200, 200)
                    )
                    self.app.screen.blit(date_text, (item_rect.x + 10, item_rect.y + 20))

        else:
            # Brak zapisów
            no_saves_text = self.font.render("Brak zapisanych gier", True, (150, 150, 150))
            text_rect = no_saves_text.get_rect(center=self.save_list_rect.center)
            self.app.screen.blit(no_saves_text, text_rect)

        # Panel informacyjny
        pygame.draw.rect(self.app.screen, self.panel_color, self.info_panel_rect)
        pygame.draw.rect(self.app.screen, self.text_color, self.info_panel_rect, 2)

        # Informacje o wybranym zapisie
        if self.saves and 0 <= self.selected_index < len(self.saves):
            selected_save = self.saves[self.selected_index]
            info_lines = selected_save.get_info_text()

            for i, line in enumerate(info_lines):
                text = self.small_font.render(line, True, self.text_color)
                self.app.screen.blit(text, (self.info_panel_rect.x + 10, self.info_panel_rect.y + 20 + i * 25))

        self._draw_buttons()
        self._draw_instructions()

    def _draw_buttons(self):
        """Rysuje przyciski"""
        button_texts = {
            'load': 'Wczytaj',
            'delete': 'Usuń',
            'create': 'Nowy świat',
            'refresh': 'Odśwież'
        }

        for button_name, button_rect in self.buttons.items():
            if self.button_states[button_name]:
                color = self.button_hover_color
            else:
                color = self.button_color

            pygame.draw.rect(self.app.screen, color, button_rect)
            pygame.draw.rect(self.app.screen, self.text_color, button_rect, 2)

            text = self.font.render(button_texts[button_name], True, self.text_color)
            text_rect = text.get_rect(center=button_rect.center)
            self.app.screen.blit(text, text_rect)

    def _draw_instructions(self):
        """Rysuje instrukcje obsługi"""
        instructions = [
            "strzałki góra/dół - Nawigacja",
            "Enter/Spacja - Wczytaj",
            "Delete - Usuń",
            "N - Nowy świat",
            "F5 - Odśwież"
        ]

        y_start = self.app.screen.get_height() - 140
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, (150, 150, 150))
            self.app.screen.blit(text, (50, y_start + i * 20))

    def update(self):
        pass


class GameManager:
    """Główny menedżer gry obsługujący menu i przełączanie stanów"""

    def __init__(self, app):
        self.app = app
        self.current_state = 'menu'
        self.loader_menu = GameLoaderMenu(app)
        self.scene = None

    def handle_event(self, event):
        """Obsługuje wydarzenia w zależności od aktualnego stanu"""
        if self.current_state == 'loader_menu':
            result = self.loader_menu.handle_event(event)
            if result:
                return self._handle_loader_result(result)
        elif self.current_state == 'game' and self.scene:
            if hasattr(self.scene, 'handle_event'):
                return self.scene.handle_event(event)
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return {'action': 'back_to_menu'}

        return None

    def _handle_loader_result(self, result):
        """Obsługuje wyniki z menu loadera"""
        action = result.get('action')

        if action == 'load_game':
            save_path = result.get('save_path')
            try:
                from scene import Scene
                self.scene = Scene.load_from_save(self.app, save_path)
                self.current_state = 'game'
                return {'action': 'game_loaded'}
            except Exception as e:
                print(f"Błąd wczytywania gry: {e}")
                return {'action': 'load_error', 'error': str(e)}

        elif action == 'create_world':
            return self.create_new_world()

        elif action == 'save_deleted':
            print("Zapis został usunięty")

        elif action == 'delete_error':
            error = result.get('error', 'Nieznany błąd')
            print(f"Błąd usuwania zapisu: {error}")

        elif action == 'back':
            # Powrót do głównego menu lub zamknięcie aplikacji (nie działa)
            return {'action': 'back_to_main'}

        elif action == 'back_to_menu':
            # Powrót z gry do menu loadera (nie działa)
            self.back_to_loader_menu()
            return {'action': 'back_to_loader'}

        return None

    def set_state(self, state):
        """Ustawia aktualny stan gry"""
        self.current_state = state
        if state == 'loader_menu':
            self.loader_menu.refresh_saves()

    def update(self):
        """Aktualizuje aktualny stan"""
        if self.current_state == 'loader_menu':
            self.loader_menu.update()
        elif self.current_state == 'game' and self.scene:
            self.scene.update()

    def draw(self):
        """Rysuje aktualny stan"""
        if self.current_state == 'loader_menu':
            self.loader_menu.draw()
        elif self.current_state == 'game' and self.scene:
            self.scene.draw()

    def create_new_world(self, world_name: str = None):
        """Tworzy nowy świat"""
        try:
            from scene import Scene

            if world_name is None:
                world_name = f"Nowy_Świat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            self.scene = Scene.create_new_world(self.app, world_name)
            self.current_state = 'game'
            print(f"Utworzono nowy świat: {world_name}")
            return {'action': 'world_created', 'world_name': world_name}

        except Exception as e:
            print(f"Błąd tworzenia świata: {e}")
            return {'action': 'create_error', 'error': str(e)}

    def get_current_state(self):
        """Zwraca aktualny stan gry"""
        return self.current_state

    def back_to_loader_menu(self):
        """Powrót do menu loadera (nie działa)"""
        self.current_state = 'loader_menu'
        self.scene = None
        self.loader_menu.refresh_saves()

    def quit_game(self):
        """Wychodzi z gry i zapisuje stan"""
        if self.scene:
            try:
                if hasattr(self.scene, 'save_game'):
                    self.scene.save_game()
                    print("Gra została zapisana przed wyjściem")
                else:
                    print("Scena nie ma metody save_game")
            except Exception as e:
                print(f"Błąd zapisywania gry przed wyjściem: {e}")

        return {'action': 'quit'}