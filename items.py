from sprite import *


class Item:
    def __init__(self, name: str = "empty", quantity: int = 0):
        self.name = name
        self.quantity = quantity

    def __str__(self):
        return f'\nName: {self.name}, Quantity: {self.quantity}'

    def use(self, *args, **kwargs):
        pass

class BlockItem(Item):
    def __init__(self, name: str, quantity: int = 0):
        super().__init__(name, quantity)

    def use(self, player, position: tuple):
        if self.quantity > 0:
            items[self.name].use_type([player.group_list[group] for group in items[self.name].groups], player.textures[self.name], position, self.name)
            self.quantity -= 1
            if self.quantity <= 0:
                self.name = "empty"
        else:
            self.name = "empty"

class ItemData:
    def __init__(self, name: str, quantity: int = 1, groups: list[str] = ['sprites', 'block_group'], use_type: Entity = Entity, item_type: Item = Item):
        self.name = name
        self.quantity = quantity
        self.groups = groups
        self.use_type = use_type
        self.item_type = item_type


items: dict[str, ItemData] = {
    'grass': ItemData('grass', item_type=BlockItem),
    'dirt': ItemData('dirt', item_type=BlockItem),
    'stone': ItemData('stone', item_type=BlockItem),
}