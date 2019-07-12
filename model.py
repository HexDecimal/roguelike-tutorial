from __future__ import annotations

from typing import List, TYPE_CHECKING

from ai import AI

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

    def enemy_turn(self) -> None:
        for obj in self.active_map.entities:
            if AI not in obj:
                continue
            if obj is self.player:
                continue
            obj[AI].take_turn(obj)
