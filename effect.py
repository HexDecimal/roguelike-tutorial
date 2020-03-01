from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from action import Action
    from actor import Actor


class Effect:
    def apply(self, action: Action, entity: Actor) -> None:
        raise NotImplementedError()


class Healing(Effect):
    def __init__(self, amount: int = 4):
        self.amount = amount

    def apply(self, action: Action, entity: Actor) -> None:
        if not entity.fighter:
            return
        fighter = entity.fighter
        fighter.hp = min(fighter.hp + self.amount, fighter.max_hp)
        action.report(f"{fighter.name} heal {self.amount} hp.")
