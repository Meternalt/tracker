import json
from pathlib import Path
from src.models.item import Item, ItemType


class Shop:
    def __init__(self, character, shop_path: str = "data/shop.json"):
        self.character = character
        self.items: list[Item] = self._load_items(shop_path)

    def _load_items(self, path: str) -> list[Item]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        items = []
        for d in data:
            d = dict(d)
            d["item_type"] = ItemType(d["item_type"])
            items.append(Item(**d))
        return items

    def show(self):
        print("\n=== МАГАЗИН ===")
        print(f"Золото: {self.character.gold} | Lvl {self.character.level}\n")
        for i, item in enumerate(self.items, 1):
            ok, msg = item.can_buy(self.character)
            mark = "" if ok else f"  ({msg})"
            print(f"{i}. {item.name} - {item.price} gold{mark}")
            print(f"   {item.description}")

    def buy(self, item_id: str) -> str:
        item = next((i for i in self.items if i.id == item_id), None)
        if not item:
            return "Товар не найден"

        ok, msg = item.can_buy(self.character)
        if not ok:
            return msg

        self.character.gold -= item.price
        self.character.inventory.append(item.id)

        if item.item_type == ItemType.CONSUMABLE:
            self._apply_effect(item)

        return f"Куплено: {item.name}"

    def _apply_effect(self, item: Item):
        c = self.character
        if item.effect == "heal":
            c.heal(int(item.value))
        elif item.effect == "shield":
            c.shield_charges += 1
        elif item.effect == "freeze":
            c.freeze_charges += 1
        elif item.effect == "double_xp":
            c.double_xp_charges += 1