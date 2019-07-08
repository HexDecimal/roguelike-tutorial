from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    import fighter


class Entity:
    """Object used to tie a variety of components to a location on a GameMap."""

    def __init__(self, x: int, y: int, fighter: Optional[fighter.Fighter] = None):
        self.x = x
        self.y = y
        self.fighter = fighter

    @property
    def char(self) -> int:
        if self.fighter:
            return self.fighter.char
        return ord("!")

    @property
    def color(self) -> Tuple[int, int, int]:
        if self.fighter:
            return self.fighter.color
        return (255, 255, 255)

    @property
    def xy(self) -> Tuple[int, int]:
        return self.x, self.y

    @xy.setter
    def xy(self, xy: Tuple[int, int]) -> None:
        self.x, self.y = xy

    @property
    def blocking(self) -> bool:
        """Return True if this entity blocks movement."""
        return self.fighter is not None

    def distance_to(self, other: Entity) -> int:
        """Return the approximate number of steps needed to reach other."""
        return max(abs(self.x - other.x), abs(self.y - other.y))

    def relative(self, x: int, y: int) -> Tuple[int, int]:
        """Return a coordinate relative to this entity."""
        return self.x + x, self.y + y
