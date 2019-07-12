from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod.path

import action
import component
from location import Location
from fighter import Fighter

if TYPE_CHECKING:
    import entity


class AI(component.Component, base_component=True):
    def take_turn(self, owner: entity.Entity) -> None:
        raise NotImplementedError()

    def get_path(
        self, owner: entity.Entity, target_xy: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        map_ = owner[Location].map
        walkable = np.copy(map_.tiles)
        blocker_pos = [e[Location].xy for e in map_.entities if Fighter in e]
        blocker_index = tuple(np.transpose(blocker_pos))
        walkable[blocker_index] = False
        walkable[target_xy] = True
        return tcod.path.AStar(walkable).get_path(*owner[Location].xy, *target_xy)


class BasicMonster(AI):
    def __init__(self) -> None:
        self.path: List[Tuple[int, int]] = []

    def take_turn(self, owner: entity.Entity) -> None:
        map_ = owner[Location].map
        if map_.visible[owner[Location].xy]:
            self.path = self.get_path(owner, map_.player[Location].xy)
            if len(self.path) >= 25:
                self.path = []
                action.move_towards(owner, map_.player[Location].xy)
        if not self.path:
            return
        if owner[Location].distance_to(map_.player[Location]) <= 1:
            action.attack_player(owner)
        else:
            action.move_to(owner, self.path.pop(0))
