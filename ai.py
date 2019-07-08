from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod.path

import action

if TYPE_CHECKING:
    import entity
    import model


class AI:
    def take_turn(self, model: model.Model, owner: entity.Entity) -> None:
        raise NotImplementedError()

    def get_path(
        self, model: model.Model, owner: entity.Entity, target_xy: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        walkable = np.copy(model.active_map.tiles)
        blocker_pos = [e.xy for e in model.active_map.entities if e.blocking]
        blocker_index = tuple(np.transpose(blocker_pos))
        walkable[blocker_index] = False
        walkable[target_xy] = True
        return tcod.path.AStar(walkable).get_path(*owner.xy, *target_xy)


class BasicMonster(AI):
    def __init__(self) -> None:
        self.path: List[Tuple[int, int]] = []

    def take_turn(self, model: model.Model, owner: entity.Entity) -> None:
        if model.active_map.visible[owner.xy]:
            self.path = self.get_path(model, owner, model.player.xy)
            if len(self.path) >= 25:
                self.path = []
                action.move_towards(model, owner, model.player.xy)
        if not self.path:
            return
        if owner.distance_to(model.player) <= 1:
            action.attack_player(model, owner)
        else:
            action.move_to(model, owner, self.path.pop(0))
