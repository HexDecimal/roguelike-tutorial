from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Iterator

from actions import Impossible
from items import Item

if TYPE_CHECKING:
    from actions import ActionWithItem
    from actor import Actor


class Scroll(Item):
    name = "Scroll"
    char = ord("#")
    color = (255, 255, 255)


class LightningScroll(Scroll):
    name = "Lightning Scroll"
    color = (255, 255, 32)
    damage = 20
    max_range = 3

    @staticmethod
    def iter_targets(action: ActionWithItem) -> Iterator[Actor]:
        for actor in action.map.actors:
            if actor is action.actor:
                continue
            if not action.map.visible[actor.location.xy]:
                continue
            yield actor

    @staticmethod
    def target_distance(owner: Actor, target: Actor) -> int:
        return owner.location.distance_to(*target.location.xy)

    def action_activate(self, action: ActionWithItem) -> None:
        targets = list(self.iter_targets(action))
        if not targets:
            raise Impossible("No enemy is close enough to strike.")
        target = min(targets, key=functools.partial(self.target_distance, action.actor))
        if self.target_distance(action.actor, target) > self.max_range:
            raise Impossible("The enemy is too far away to strike.")
        damage = self.damage
        action.report(
            f"A lighting bolt strikes the {target.fighter.name} for {damage} damage!"
        )
        target.damage(damage)
        self.consume(action)
