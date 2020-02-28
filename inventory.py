from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Entity


class Inventory:
    symbols = "abcdefghijklmnopqrstuvwxyz"
    capacity = len(symbols)

    def __init__(self) -> None:
        self.contents: List[Entity] = []

    def take(self, entity: Entity) -> None:
        self.contents.append(entity)
        assert entity.location
        entity.location.map.entities.remove(entity)
        entity.location = None
