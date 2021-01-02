from __future__ import annotations

from typing import TYPE_CHECKING

import effect
from items import Item
import actions.common

if TYPE_CHECKING:
    from actor import Actor
    from actions import ActionWithItem

class Eatable(Item):

    def __init__(self, my_effect: effect.Effect):
        super().__init__()
        self.my_effect = my_effect

    def plan_activate(self, action: ActionWithItem) -> ActionWithItem:
        """Foods will forward to a food action."""
        return actions.common.EatItem(action.actor, self)

    def action_eat(self, action: ActionWithItem) -> None:
        """Consume this food and active its effect."""
        self.consume(action)
        self.my_effect.apply(action, action.actor)


class Corpse(Eatable):
    char = ord("%")
    color = (127, 0, 0)
    render_order = 2

    def __init__(self, actor: Actor) -> None:
        super().__init__(effect.Healing(1))
        self.name = f"{actor.fighter.name} Corpse"

class FoodRation(Eatable):
    char = ord("%")
    color = (127, 0, 0)
    render_order = 2

    def __init__(self) -> None:
        super().__init__(effect.Healing(2))
        self.name = "Food ration"
