from __future__ import annotations

from typing import TYPE_CHECKING

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


class HealingPotion(Item):
    name = "Healing Potion"
    char = ord("!")
    color = (64, 0, 64)

    def activate(self, action: ActionWithEntity) -> None:
        self.consume(action)
        assert action.actor.fighter
        fighter = action.actor.fighter
        fighter.hp = min(fighter.hp + 4, fighter.max_hp)
        action.report(f"{fighter.name} heal 4 hp.")
