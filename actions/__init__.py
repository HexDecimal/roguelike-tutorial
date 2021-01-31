from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from actor import Actor
    from gamemap import GameMap
    from items import Item
    from location import Location
    from model import Model


class Impossible(Exception):
    """Exception raised when an action can not be performed.

    Includes the reason as the exception message.
    """


class Action:
    def __init__(self, actor: Actor):
        self.actor = actor

    def plan(self) -> Action:
        """Return the action to perform."""
        return self

    def act(self) -> None:
        """Execute the action for this class."""
        raise RuntimeError(f"{self.__class__} has no act implementation.")

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
