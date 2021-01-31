from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type

import actor
import graphic
from actions.ai import BasicMonster
from inventory import Inventory

if TYPE_CHECKING:
    from actions import Action
    from location import Location


class Fighter(graphic.Graphic):
    render_order = 0

    hp: int = 0
    power: int = 0
    defense: int = 0

    DEFAULT_AI: Type[Action] = BasicMonster

    def __init__(self, inventory: Optional[Inventory] = None) -> None:
        self.alive = True
        self.max_hp = self.hp
        self.inventory = inventory or Inventory()

    @classmethod
    def spawn(
        cls, location: Location, ai_cls: Optional[Type[Action]] = None
    ) -> actor.Actor:
        self = cls()
        return actor.Actor(location, self, ai_cls or cls.DEFAULT_AI)
