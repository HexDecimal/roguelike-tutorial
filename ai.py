from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod.path

import actions
import states

if TYPE_CHECKING:
    import entity


class AI:
    def take_turn(self, owner: entity.Entity) -> None:
        raise NotImplementedError()

    def get_path(
        self, owner: entity.Entity, target_xy: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        assert owner.location
        map_ = owner.location.map
        walkable = np.copy(map_.tiles["move_cost"])
        blocker_pos = [
            e.location.xy
            for e in map_.entities
            if e.fighter and e.fighter.hp > 0 and e.location
        ]
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
                actions.MoveTowards(owner, map_.player.location.xy).act()
        if not self.path:
            actions.Move(owner, (0, 0)).act()
            return
        if owner.location.distance_to(*map_.player.location.xy) <= 1:
            actions.AttackPlayer(owner).act()
        else:
            actions.MoveTo(owner, self.path.pop(0)).act()


class PlayerControl(AI):
    def take_turn(self, owner: entity.Entity) -> None:
        assert owner.location
        ticket = owner.ticket
        while ticket is owner.ticket:
            states.PlayerReady(owner.location.map.model).loop()
