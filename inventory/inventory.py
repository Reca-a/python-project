import pygame

from items import *


class Inventory:
    def __init__(self, app, textures):
        self.app = app
        self.screen = app.screen
        self.textures = textures
        self.slots = []
        self.active_slot = 0

        self.font = pygame.font.Font(None, 30)

        for index in range(5):
            self.slots.append(Item())
        self.slots[1] = BlockItem('grass', 5)
        self.slots[2] = BlockItem('dirt', 3)

    def use(self, player, position):
        if self.slots[self.active_slot].name != "empty":
            self.slots[self.active_slot].use(player, position)

    def input(self, event):
        if event.key == pygame.K_RIGHT:
            if self.active_slot < len(self.slots) - 1:
                self.active_slot += 1
        if event.key == pygame.K_LEFT:
            if self.active_slot > 0:
                self.active_slot -= 1

    def add_item(self, item):
        first_available_slot = len(self.slots) # Pierwsze znalezione miejsce w ekwipunku
        target_slot = len(self.slots) # Pierwsze miejsce z tym samym przedmiotem
        for index, slot in enumerate(self.slots):
            if slot.name == "empty" and index < first_available_slot:
                first_available_slot = index
            if slot.name == item.name:
                target_slot = index
        if target_slot < len(self.slots):
            self.slots[target_slot].quantity += items[item.name].quantity
        elif first_available_slot < len(self.slots):
            self.slots[first_available_slot] = items[item.name].item_type(item.name, items[item.name].quantity)

    def update(self):
        pass

    def draw(self):
        #Tło UI ekwipunku
        pygame.draw.rect(self.screen, "gray", pygame.Rect(0,0,TILE_SIZE*2*len(self.slots), TILE_SIZE*2))

        x_offset = TILE_SIZE / 2
        y_offset = TILE_SIZE / 2

        for i in range(len(self.slots)):
            if i == self.active_slot: # Zaznaczenie wybranego indeksu w ekwipunku
                pygame.draw.rect(self.screen, "white", pygame.Rect(i * TILE_SIZE * 2, 0, TILE_SIZE * 2, TILE_SIZE * 2))
            # Krawędzie wewnętrzne
            pygame.draw.rect(self.screen, "black", pygame.Rect(i * TILE_SIZE * 2, 0, TILE_SIZE * 2, TILE_SIZE * 2), 1)
            if self.slots[i].name != "empty": # Rysowanie tekstur przedmiotów
                self.screen.blit(self.textures[self.slots[i].name], (x_offset + (TILE_SIZE * 2) * i, y_offset))

                self.item_amount_text = self.font.render(str(self.slots[i].quantity), True, "black")
                self.screen.blit(self.item_amount_text, (TILE_SIZE * 2 * i + 2, 2))
            #Krawędzie zewnętrzne
            pygame.draw.rect(self.screen, "black", pygame.Rect(0, 0, TILE_SIZE * 2 * len(self.slots), TILE_SIZE * 2), 2)