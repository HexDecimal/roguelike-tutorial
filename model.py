from __future__ import annotations

from typing import List, TYPE_CHECKING

import states

if TYPE_CHECKING:
    import gamemap
    import entity


class Model:
    """The model contains everything from a session which should be saved."""

    active_map: gamemap.GameMap

    def __init__(self) -> None:
        self.log: List[str] = []

    @property
    def player(self) -> entity.Entity:
        return self.active_map.player

    def report(self, text: str) -> None:
        print(text)
        self.log.append(text)

    def is_player_dead(self) -> bool:
        """True if the player had died."""
        return not self.player.fighter or self.player.fighter.hp <= 0

    def loop(self) -> None:
        while True:
            if self.is_player_dead():
                states.GameOver(self).loop()
                continue
            states.PlayerReady(self).loop()
            self.enemy_turn()

    def enemy_turn(self) -> None:
        for obj in self.active_map.entities:
            if not obj.ai:
                continue
            if obj is self.player:
                continue
            obj.ai.take_turn(obj)
