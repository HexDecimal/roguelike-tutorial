from __future__ import annotations

from typing import TYPE_CHECKING

import effect
from item import Item


if TYPE_CHECKING:
    from actor import Actor
    from actions import ActionWithItem, common


class Potion(Item):
    name = "Potion"
    char = ord("!")
    color = (255, 255, 255)

    def __init__(self, my_effect: effect.Effect):
        super().__init__()
        self.my_effect = my_effect

    def plan_item(self, action: ActionWithItem) -> ActionWithItem:
        """Potions will forward to a drink action."""
        return common.DrinkItem(action.actor, self)

    def action_drink(self, action: ActionWithItem) -> None:
        """Consume this potion and active its effect."""
        self.consume(action)
        self.my_effect.apply(action, action.actor)


class HealingPotion(Potion):
    name = "Healing Potion"
    color = (64, 0, 64)

    def __init__(self) -> None:
        super().__init__(effect.Healing(4))


class Corpse(Item):
    char = ord("%")
    color = (127, 0, 0)
    render_order = 2

    def __init__(self, actor: Actor) -> None:
        super().__init__()
        self.name = f"{actor.fighter.name} Corpse"
