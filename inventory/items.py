from sprites.sprite import *


class ItemData:
    def __init__(self, name: str, quantity: int = 1, groups: list[str] = ['sprites', 'block_group'], use_type: Entity = Entity, item_type: None = None):
        self.name = name
        self.quantity = quantity
        self.groups = groups
        self.use_type = use_type
        self.item_type = item_type or Item

class Item:
    def __init__(self, data: ItemData, quantity: int = 0):
        self.data = data
        self.quantity = quantity

    @property
    def name(self) -> str:
        return self.data.name

    def use(self, *args, **kwargs):
        pass

class BlockItem(Item):
    def __init__(self, data: ItemData, quantity: int = 0):
        super().__init__(data, quantity)

    def use(self, player, position: tuple):
        if self.quantity <= 0:
            return

        block_class = self.data.use_type
        groups = [player.group_list[g] for g in self.data.groups]
        # Stawianie bloku
        block_class(
            groups,
            player.textures[self.name],
            position,
            self.name
        )

        self.quantity -= 1

class EmptyItem(Item):
    def use(self, *args, **kwargs):
        # Pusty slot nic nie robi
        pass

class ItemRegistry:
    def __init__(self):
        self._data: dict[str, ItemData] = {}

    def get_data(self, name: str) -> ItemData:
        return self._data[name]

    def register(self, data: ItemData):
        self._data[data.name] = data

    def create(self, name: str, quantity: int = 1) -> 'Item':
        info = self._data.get(name)
        if not info:
            raise KeyError(f"Item '{name}' not found")
        return info.item_type(info, quantity)

# Rejestr przedmiotów
registry = ItemRegistry()

# Podstawowe bloki
registry.register(ItemData('grass', item_type=BlockItem))
registry.register(ItemData('dirt', item_type=BlockItem))
registry.register(ItemData('stone', item_type=BlockItem))

# Drewno i liście
registry.register(ItemData('wood', item_type=BlockItem))
registry.register(ItemData('leaves', item_type=BlockItem))

# Rudy
registry.register(ItemData('coal_ore', item_type=BlockItem))
registry.register(ItemData('iron_ore', item_type=BlockItem))
registry.register(ItemData('gold_ore', item_type=BlockItem))
registry.register(ItemData('diamond_ore', item_type=BlockItem))

# Pusty slot
registry.register(ItemData('empty', item_type=EmptyItem))