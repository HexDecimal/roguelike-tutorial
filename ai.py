from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod.path

from action import NoAction, Action
import actions
import states

if TYPE_CHECKING:
    from actor import Actor


class Pathfinder(Action):
    def __init__(self, actor: Actor, dest_xy: Tuple[int, int]) -> None:
        super().__init__(actor)

        map_ = self.actor.location.map
        walkable = np.copy(map_.tiles["move_cost"])
        blocker_pos = [e.location.xy for e in map_.actors]
        blocker_index = tuple(np.transpose(blocker_pos))
        walkable[blocker_index] = False
        walkable[dest_xy] = True
        self.path: List[Tuple[int, int]] = tcod.path.AStar(walkable).get_path(*self.actor.location.xy, *dest_xy)

    def plan(self) -> Action:
        if not self.path:
            raise NoAction("End of path reached.")
        return actions.MoveTo(self.actor, self.path.pop(0)).plan()


class AI(Action):
    def get_path(
        self, owner: Actor, target_xy: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        map_ = owner.location.map
        walkable = np.copy(map_.tiles["move_cost"])
        blocker_pos = [e.location.xy for e in map_.actors]
        blocker_index = tuple(np.transpose(blocker_pos))
        walkable[blocker_index] = False
        walkable[target_xy] = True
        return tcod.path.AStar(walkable).get_path(*owner.location.xy, *target_xy)


class BasicMonster(AI):
    def __init__(self, actor: Actor) -> None:
        super().__init__(actor)
        self.path: List[Tuple[int, int]] = []

    def plan(self) -> Action:
        owner = self.actor
        map_ = owner.location.map
        if map_.visible[owner.location.xy]:
            self.path = self.get_path(owner, map_.player.location.xy)
            if len(self.path) >= 25:
                self.path = []
                try:
                    return actions.MoveTowards(owner, map_.player.location.xy).plan()
                except NoAction:
                    pass
        if not self.path:
            return actions.Move(owner, (0, 0)).plan()
        if owner.location.distance_to(*map_.player.location.xy) <= 1:
            return actions.AttackPlayer(owner).plan()
        return actions.MoveTo(owner, self.path.pop(0)).plan()


class PlayerControl(AI):
    def act(self) -> None:
        ticket = self.actor.ticket
        while ticket is self.actor.ticket:
            try:
                states.PlayerReady(self.actor.location.map.model).loop()
            except NoAction as exc:
                self.report(exc.args[0])
