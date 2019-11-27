from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    import entity
    from gamemap import GameMap
    from location import Location
    from model import Model


class Action:
    def __init__(self, actor: entity.Entity):
        self.actor = actor

    def act(self) -> None:
        raise NotImplementedError()

    def is_player(self) -> bool:
        """Return True if the active actor is the player entity."""
        return self.location.map.player is self.actor

    @property
    def location(self) -> Location:
        assert self.actor.location, self.actor
        return self.actor.location

    @property
    def map(self) -> GameMap:
        assert self.actor.location, self.actor
        return self.actor.location.map

    @property
    def model(self) -> Model:
        assert self.actor.location, self.actor
        return self.actor.location.map.model

    def report(self, msg: str) -> None:
        return self.model.report(msg)


class ActionWithPosition(Action):
    def __init__(self, actor: entity.Entity, position: Tuple[int, int]):
        super().__init__(actor)
        self.target_pos = position


class ActionWithDirection(ActionWithPosition):
    def __init__(self, actor: entity.Entity, direction: Tuple[int, int]):
        assert actor.location
        position = actor.location.x + direction[0], actor.location.y + direction[1]
        super().__init__(actor, position)
        self.direction = direction


class ActionWithEntity(Action):
    def __init__(self, actor: entity.Entity, target: entity.Entity):
        super().__init__(actor)
        self.target = target
