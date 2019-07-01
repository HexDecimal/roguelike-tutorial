from typing import Optional, Tuple

import fighter


class Entity:
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
        return self.x + x, self.y + y

    def move_by(self, x: int, y: int) -> None:
        self.x, self.y = self.relative(x, y)
