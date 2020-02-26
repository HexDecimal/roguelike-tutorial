from __future__ import annotations

from typing import TYPE_CHECKING

import effect
import graphic

if TYPE_CHECKING:
    from action import ActionWithEntity


class Item(graphic.Graphic):
    render_order = 1

    def activate(self, action: ActionWithEntity) -> None:
        """Item activated as part of an action.

        Assume that action has an actor which is holding this items entity.
        """
        raise NotImplementedError()

    def consume(self, action: ActionWithEntity) -> None:
        """Remove this item from the actors inventory."""
        assert action.actor.inventory
        assert action.target.item is self
        action.actor.inventory.contents.remove(action.target)


class Potion(Item):
    name = "Potion"
    char = ord("!")
    color = (255, 255, 255)

    def __init__(self, my_effect: effect.Effect):
        self.my_effect = my_effect

    def activate(self, action: ActionWithEntity) -> None:
        self.consume(action)
        self.my_effect.apply(action, action.actor)


class HealingPotion(Potion):
    name = "Healing Potion"
    color = (64, 0, 64)

    def __init__(self) -> None:
        super().__init__(effect.Healing(4))
