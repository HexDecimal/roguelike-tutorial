from __future__ import annotations

from typing import TYPE_CHECKING

import effect
from item import Item


if TYPE_CHECKING:
    from actor import Actor
    from action import ActionWithItem


class Potion(Item):
    name = "Potion"
    char = ord("!")
    color = (255, 255, 255)

    def __init__(self, my_effect: effect.Effect):
        super().__init__()
        self.my_effect = my_effect

    def activate(self, action: ActionWithItem) -> None:
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
