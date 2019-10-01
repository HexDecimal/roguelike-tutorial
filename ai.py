from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod.path

import action
import component

if TYPE_CHECKING:
    import entity


class AI(component.Component, base_component=True):
    def take_turn(self, owner: entity.Entity) -> None:
        raise NotImplementedError()

    def get_path(
        self, owner: entity.Entity, target_xy: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        assert owner.location
        map_ = owner.location.map
        walkable = np.copy(map_.tiles)
        blocker_pos = [e.location.xy for e in map_.entities if e.fighter and e.location]
        blocker_index = tuple(np.transpose(blocker_pos))
        walkable[blocker_index] = False
        walkable[target_xy] = True
        return tcod.path.AStar(walkable).get_path(*owner.location.xy, *target_xy)


class BasicMonster(AI):
    def __init__(self) -> None:
        self.path: List[Tuple[int, int]] = []

    def take_turn(self, owner: entity.Entity) -> None:
        assert owner.location
        map_ = owner.location.map
        assert map_.player.location
        if map_.visible[owner.location.xy]:
            self.path = self.get_path(owner, map_.player.location.xy)
            if len(self.path) >= 25:
                self.path = []
                action.move_towards(owner, map_.player.location.xy)
        if not self.path:
            return
        if owner.location.distance_to(map_.player.location) <= 1:
            action.attack_player(owner)
        else:
            action.move_to(owner, self.path.pop(0))
