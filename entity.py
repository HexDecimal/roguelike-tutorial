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

    def relative(self, x: int, y: int) -> Tuple[int, int]:
        """Return a coordinate relative to this entity."""
        return self.x + x, self.y + y
