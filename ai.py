from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod.path

from action import NoAction, Action
import actions
import states

if TYPE_CHECKING:
    from actor import Actor


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

    def poll(self) -> Action:
        owner = self.actor
        map_ = owner.location.map
        if map_.visible[owner.location.xy]:
            self.path = self.get_path(owner, map_.player.location.xy)
            if len(self.path) >= 25:
                self.path = []
                try:
                    return actions.MoveTowards(owner, map_.player.location.xy).poll()
                except NoAction:
                    pass
        if not self.path:
            return actions.Move(owner, (0, 0)).poll()
        if owner.location.distance_to(*map_.player.location.xy) <= 1:
            return actions.AttackPlayer(owner).poll()
        return actions.MoveTo(owner, self.path.pop(0)).poll()


class PlayerControl(AI):
    def act(self) -> None:
        ticket = self.actor.ticket
        while ticket is self.actor.ticket:
            try:
                states.PlayerReady(self.actor.location.map.model).loop()
            except NoAction as exc:
                self.report(exc.args[0])
