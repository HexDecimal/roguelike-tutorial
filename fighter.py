from __future__ import annotations

from typing import Optional, Tuple, Type, TYPE_CHECKING

import ai
import component
import entity

if TYPE_CHECKING:
    import location


class Fighter(component.Component, base_component=True):
    name: str = "<Unnamed>"
    char: int = ord("!")
    color: Tuple[int, int, int] = (255, 255, 255)

    hp: int = 0
    power: int = 0
    defense: int = 0

    AI: Optional[Type[ai.AI]] = None

    def __init__(self) -> None:
        self.max_hp = self.hp

    @classmethod
    def spawn(cls, location: location.Location) -> entity.Entity:
        AI = cls.AI if cls.AI is not None else ai.BasicMonster
        e = entity.Entity((location, cls(), AI()))
        location.map.entities.append(e)
        return e


class Player(Fighter):
    name = "You"
    char = ord("@")
    color = (255, 255, 255)

    hp = 30
    power = 5
    defense = 2


class Orc(Fighter):
    name = "Orc"
    char = ord("o")
    color = (63, 127, 63)

    hp = 10
    power = 3
    defense = 0


class Troll(Fighter):
    name = "Troll"
    char = ord("T")
    color = (0, 127, 0)

    hp = 16
    power = 4
    defense = 1
