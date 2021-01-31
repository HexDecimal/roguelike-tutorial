from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

import numpy as np
import tcod

import actions.common
from actions import Action, Impossible
from states import ingame

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
        blocker_pos = [e.location.ij for e in map_.actors]
        blocker_index = tuple(np.transpose(blocker_pos))
        walkable[blocker_index] = 50
        walkable.T[self.dest_xy] = 1
        graph = tcod.path.SimpleGraph(cost=walkable, cardinal=2, diagonal=3)
        pf = tcod.path.Pathfinder(graph)
        pf.add_root(self.actor.location.ij)
        return [(ij[1], ij[0]) for ij in pf.path_to(self.dest_xy[::-1])[1:].tolist()]

    def plan(self) -> Action:
        if not self.path_xy:
            raise Impossible("End of path reached.")
        self.subaction = actions.common.MoveTo(self.actor, self.path_xy[0]).plan()
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
        if map_.visible[owner.location.ij]:
            self.pathfinder = PathTo(owner, map_.player.location.xy)
        if not self.pathfinder:
            return actions.common.Move(owner, (0, 0)).plan()
        if owner.location.distance_to(*map_.player.location.xy) <= 1:
            return actions.common.AttackPlayer(owner).plan()
        try:
            return self.pathfinder.plan()
        except Impossible:
            self.pathfinder = None
            return actions.common.Move(owner, (0, 0)).plan()


class PlayerControl(AI):
    def act(self) -> None:
        ticket = self.actor.ticket
        while ticket is self.actor.ticket:
            next_action = ingame.PlayerReady(self.actor.location.map.model).loop()
            if next_action is None:
                continue
            try:
                next_action.plan().act()
            except Impossible as exc:
                self.report(exc.args[0])
