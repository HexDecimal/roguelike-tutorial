from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import component

if TYPE_CHECKING:
    import gamemap


class Location(component.Component, base_component=True):
    map: gamemap.GameMap
    x: int
    y: int

    @property
    def xy(self) -> Tuple[int, int]:
        return self.x, self.y

    @xy.setter
    def xy(self, xy: Tuple[int, int]) -> None:
        self.x, self.y = xy

    def distance_to(self, other: Location) -> int:
        """Return the approximate number of steps needed to reach other."""
        return max(abs(self.x - other.x), abs(self.y - other.y))

    def relative(self, x: int, y: int) -> Tuple[int, int]:
        """Return a coordinate relative to this entity."""
        return self.x + x, self.y + y
