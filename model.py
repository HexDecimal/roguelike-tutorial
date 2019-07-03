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
