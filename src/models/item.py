from dataclasses import dataclass
from enum import Enum


class ItemType(Enum):
    COSMETIC = "cosmetic"
    CONSUMABLE = "consumable"
    UPGRADE = "upgrade"


@dataclass
class Item:
    id: str
    name: str
    description: str
    price: int
    item_type: ItemType
    required_level: int = 1
    effect: str | None = None
    value: float = 0

    def can_buy(self, character) -> tuple[bool, str]:
        if character.level < self.required_level:
            return False, f"Нужен уровень {self.required_level}"
        if character.gold < self.price:
            return False, "Недостаточно золота"
        return True, ""