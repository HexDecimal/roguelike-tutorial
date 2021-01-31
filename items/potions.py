from __future__ import annotations

from typing import TYPE_CHECKING

import actions.common
import effect
from items import Item

if TYPE_CHECKING:
    from actions import ActionWithItem


class Potion(Item):
    name = "Potion"
    char = ord("!")
    color = (255, 255, 255)

    def __init__(self, my_effect: effect.Effect):
        super().__init__()
        self.my_effect = my_effect

    def plan_activate(self, action: ActionWithItem) -> ActionWithItem:
        """Potions will forward to a drink action."""
        return actions.common.DrinkItem(action.actor, self)

    def action_drink(self, action: ActionWithItem) -> None:
        """Consume this potion and active its effect."""
        self.consume(action)
        self.my_effect.apply(action, action.actor)


class HealingPotion(Potion):
    name = "Healing Potion"
    color = (64, 0, 64)

    def __init__(self) -> None:
        super().__init__(effect.Healing(4))
