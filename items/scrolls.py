from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Iterator

from actions import Impossible
from items import Item
import states.ingame

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
            if not action.map.visible[actor.location.ij]:
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


class FireballScroll(Scroll):
    name = "Fireball Scroll"
    color = (255, 32, 32)
    damage = 12
    radius = 3

    def action_activate(self, action: ActionWithItem) -> None:
        selected_xy = states.ingame.PickLocation(
            action.model, "Select where to cast a fireball.", action.actor.location.xy
        ).loop()
        if not selected_xy:
            raise Impossible("Targeting canceled.")
        if not action.map.visible.T[selected_xy]:
            raise Impossible("You cannot target a tile outside your field of view")

        action.report(
            f"The fireball explodes, burning everything within {self.radius} tiles!"
        )

        # Use a copy of the actors list since it may be edited during the loop.
        for actor in list(action.map.actors):
            if actor.location.distance_to(*selected_xy) > self.radius:
                continue
            action.report(
                f"The {actor.fighter.name} gets burned for {self.damage} hit points"
            )
            actor.damage(self.damage)
        self.consume(action)


class GenocideScroll(Scroll):
    name = "Genocide Scroll"
    color = (32, 32, 0)

    def action_activate(self, action: ActionWithItem) -> None:
        selected_xy = states.ingame.PickLocation(
            action.model, "Select who to genecide.", action.actor.location.xy
        ).loop()
        if not selected_xy:
            raise Impossible("Targeting canceled.")
        if not action.map.visible.T[selected_xy]:
            raise Impossible("You cannot target a enemy outside your field of view.")

        selected_actor = action.map.fighter_at(*selected_xy)
        if not selected_actor or selected_actor.is_player():
            raise Impossible("No enemy selected to genocide.")

        type_fighter = type(selected_actor.fighter)
        # Use a copy of the actors list since it may be edited during the loop.
        for actor in list(action.map.actors):
            if isinstance(actor.fighter, type_fighter):
                actor.die()

        action.report(
            f"The {selected_actor.fighter.name} has been genocided"
        )
        self.consume(action)


class TeleportScroll(Scroll):
    name = "Teleport Scroll"
    color = (32, 32, 255)

    def action_activate(self, action: ActionWithItem) -> None:
        selected_xy = states.ingame.PickLocation(
            action.model, "Select where to cast a teleport.", action.actor.location.xy
        ).loop()
        if not selected_xy:
            raise Impossible("Targeting canceled.")
        if not action.map.visible.T[selected_xy]:
            raise Impossible("You cannot target a tile outside your field of view.")
        if action.map.is_blocked(*selected_xy):
            raise Impossible("This tile is blocked.")

        action.actor.location = action.map[selected_xy]
        action.map.update_fov()
        self.consume(action)
