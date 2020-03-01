from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from item import Item


class Inventory:
    symbols = "abcdefghijklmnopqrstuvwxyz"
    capacity = len(symbols)

    def __init__(self) -> None:
        self.contents: List[Item] = []

    def take(self, item: Item) -> None:
        """Take an item from its current location and put it in self."""
        assert item.owner is not self
        item.lift()
        self.contents.append(item)
        item.owner = self
