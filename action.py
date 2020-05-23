from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import item as item_

if TYPE_CHECKING:
    from actor import Actor
    from gamemap import GameMap
    from item import Item
    from location import Location
    from model import Model


class NoAction(Exception):
    pass


class Action:
    def __init__(self, actor: Actor):
        self.actor = actor

    def plan(self) -> Action:
        """Return the action to perform."""
        return self

    def act(self) -> None:
        """Execute the action for this class."""
        raise NotImplementedError(self)

    def is_player(self) -> bool:
        """Return True if the active actor is the player entity."""
        return self.location.map.player is self.actor

    def reschedule(self, interval: int) -> None:
        """Reschedule this actor to run after `interval` ticks."""
        assert self.actor.ticket
        self.actor.ticket = self.map.scheduler.reschedule(self.actor.ticket, interval)

    def kill_actor(self, target: Actor) -> None:
        """Kill target and replace with a corpse."""
        if target is self.map.player:
            self.report(f"You die.")
        else:
            self.report(f"The {target.fighter.name} dies.")
        item_.Corpse(target).place(target.location)  # Leave behind corpse.
        # Drop all held items.
        for item in list(target.fighter.inventory.contents):
            item.lift()
            item.place(target.location)
        target.location.map.actors.remove(target)  # Actually remove the actor.
        target.ticket = None  # Disable AI.

    @property
    def location(self) -> Location:
        return self.actor.location

    @property
    def map(self) -> GameMap:
        return self.actor.location.map

    @property
    def model(self) -> Model:
        return self.actor.location.map.model

    def report(self, msg: str) -> None:
        return self.model.report(msg)


class ActionWithPosition(Action):
    def __init__(self, actor: Actor, position: Tuple[int, int]):
        super().__init__(actor)
        self.target_pos = position


class ActionWithDirection(ActionWithPosition):
    def __init__(self, actor: Actor, direction: Tuple[int, int]):
        position = actor.location.x + direction[0], actor.location.y + direction[1]
        super().__init__(actor, position)
        self.direction = direction


class ActionWithEntity(Action):
    def __init__(self, actor: Actor, target: Actor):
        super().__init__(actor)
        self.target = target


class ActionWithItem(Action):
    def __init__(self, actor: Actor, target: Item):
        super().__init__(actor)
        self.item = target
