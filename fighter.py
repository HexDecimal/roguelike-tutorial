from __future__ import annotations

from typing import Optional, Type, TYPE_CHECKING

import actor
from ai import AI, BasicMonster
import graphic
from inventory import Inventory


if TYPE_CHECKING:
    from location import Location


class Fighter(graphic.Graphic):
    render_order = 0

    hp: int = 0
    power: int = 0
    defense: int = 0

    DEFAULT_AI: Type[AI] = BasicMonster

    def __init__(self, inventory: Optional[Inventory] = None) -> None:
        self.max_hp = self.hp
        self.inventory = inventory or Inventory()

    @classmethod
    def spawn(
        cls, location: Location, ai_cls: Optional[Type[AI]] = None
    ) -> actor.Actor:
        self = cls()
        return actor.Actor(location, self, ai_cls or cls.DEFAULT_AI)


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
