from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING, Optional

import numpy as np  # type: ignore
import tcod.path

from action import Impossible, Action
import actions
import states

if TYPE_CHECKING:
    from actor import Actor


class PathTo(Action):
    def __init__(self, actor: Actor, dest_xy: Tuple[int, int]) -> None:
        super().__init__(actor)
        self.subaction: Optional[Action] = None
        self.dest_xy = dest_xy
        self.path_xy: List[Tuple[int, int]] = self.compute_path()

    def compute_path(self) -> List[Tuple[int, int]]:
        map_ = self.actor.location.map
        walkable = np.copy(map_.tiles["move_cost"])
        blocker_pos = [e.location.xy for e in map_.actors]
        blocker_index = tuple(np.transpose(blocker_pos))
        walkable[blocker_index] = 50
        walkable[self.dest_xy] = 1
        return tcod.path.AStar(walkable).get_path(
            *self.actor.location.xy, *self.dest_xy
        )

    def plan(self) -> Action:
        if not self.path_xy:
            raise Impossible("End of path reached.")
        self.subaction = actions.MoveTo(self.actor, self.path_xy[0]).plan()
        return self

    def act(self) -> None:
        assert self.subaction
        self.subaction.act()
        if self.path_xy[0] == self.actor.location.xy:
            self.path_xy.pop(0)


class AI(Action):
    pass


class BasicMonster(AI):
    def __init__(self, actor: Actor) -> None:
        super().__init__(actor)
        self.pathfinder: Optional[PathTo] = None

    def plan(self) -> Action:
        owner = self.actor
        map_ = owner.location.map
        if map_.visible[owner.location.xy]:
            self.pathfinder = PathTo(owner, map_.player.location.xy)
        if not self.pathfinder:
            return actions.Move(owner, (0, 0)).plan()
        if owner.location.distance_to(*map_.player.location.xy) <= 1:
            return actions.AttackPlayer(owner).plan()
        return self.pathfinder.plan()


class PlayerControl(AI):
    def act(self) -> None:
        ticket = self.actor.ticket
        while ticket is self.actor.ticket:
            next_action = states.PlayerReady(self.actor.location.map.model).loop()
            if next_action is None:
                continue
            try:
                next_action.plan().act()
            except Impossible as exc:
                self.report(exc.args[0])
