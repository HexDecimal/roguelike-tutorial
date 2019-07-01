from typing import Tuple


class Fighter:
    char: int = ord("!")
    color: Tuple[int, int, int] = (255, 255, 255)


class Player(Fighter):
    char = ord("@")
    color = (255, 255, 255)
