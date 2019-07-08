from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import gamemap
    import entity


class Model:
    """The model contains everything from a session which should be saved."""

    active_map: gamemap.GameMap

    def __init__(self) -> None:
        pass

    @property
    def player(self) -> entity.Entity:
        return self.active_map.player

    def report(self, text: str) -> None:
        print(text)

    def enemy_turn(self) -> None:
        for obj in self.active_map.entities:
            if obj.fighter is None:
                continue
            if obj is self.player:
                continue
            obj.fighter.ai.take_turn(self, obj)
