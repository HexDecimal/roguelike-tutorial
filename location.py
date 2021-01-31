from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    import gamemap


class Location:
    map: gamemap.GameMap
    x: int
    y: int

    @property
    def xy(self) -> Tuple[int, int]:
        return self.x, self.y

    @xy.setter
    def xy(self, xy: Tuple[int, int]) -> None:
        self.x, self.y = xy

    @property
    def ij(self) -> Tuple[int, int]:
        return self.y, self.x

    def distance_to(self, x: int, y: int) -> int:
        """Return the approximate number of steps needed to reach x,y."""
        return max(abs(self.x - x), abs(self.y - y))

    def relative(self, x: int, y: int) -> Tuple[int, int]:
        """Return a coordinate relative to this entity."""
        return self.x + x, self.y + y
