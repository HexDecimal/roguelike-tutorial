from typing import Tuple


class Entity:
    def __init__(self, x: int, y: int, char: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def relative(self, x: int, y: int) -> Tuple[int, int]:
        return self.x + x, self.y + y

    def move_by(self, x: int, y: int) -> None:
        self.x, self.y = self.relative(x, y)
