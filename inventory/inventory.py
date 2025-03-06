import pygame

from items import *


class Inventory:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.slots = []

        for index in range(5):
            self.slots.append(Item())
        self.slots[1] = BlockItem('grass', 5)
        self.slots[2] = BlockItem('dirt', 3)

        self.active_slot = 0

    def debug(self):
        print(self.slots[self.active_slot])
        print(self.active_slot)

    def use(self, player, position):
        if self.slots[self.active_slot].name != "empty":
            self.slots[self.active_slot].use(player, position)

    def input(self, event):
        if event.key == pygame.K_RIGHT:
            if self.active_slot < len(self.slots) - 1:
                self.active_slot += 1
                self.debug()
        if event.key == pygame.K_LEFT:
            if self.active_slot > 0:
                self.active_slot -= 1
                self.debug()

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
        pass