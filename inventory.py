from __future__ import annotations

from typing import List, TYPE_CHECKING

import component
from location import Location

if TYPE_CHECKING:
    from entity import Entity


class Inventory(component.Component, base_component=True):
    capacity = 26

    def __init__(self) -> None:
        self.contents: List[Entity] = []

    def take(self, entity: Entity) -> None:
        self.contents.append(entity)
        entity[Location].map.entities.remove(entity)
        del entity[Location]
