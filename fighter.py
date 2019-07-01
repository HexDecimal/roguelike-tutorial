from typing import Tuple

import tcod


class Fighter:
    name: str = "<Unnamed>"
    char: int = ord("!")
    color: Tuple[int, int, int] = (255, 255, 255)


class Player(Fighter):
    name = "You"
    char = ord("@")
    color = (255, 255, 255)


class Orc(Fighter):
    name = "Orc"
    char = ord("o")
    color = (63, 127, 63)


class Troll(Fighter):
    name = "Troll"
    char = ord("T")
    color = (0, 127, 0)
