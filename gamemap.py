from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterator, List, Optional, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod

from location import Location

if TYPE_CHECKING:
    import tcod.console
    import entity
    from graphic import Graphic
    from model import Model


class MapLocation(Location):
    def __init__(self, gamemap: GameMap, x: int, y: int):
        self.map = gamemap
        self.x = x
        self.y = y


class GameMap:
    """An object which holds the tile and entity data for a single floor."""

    COLOR = {
        "dark_wall": (0, 0, 100),
        "dark_ground": (50, 50, 150),
        "light_wall": (130, 110, 50),
        "light_ground": (200, 180, 50),
    }

    model: Model
    player: entity.Entity

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.shape = width, height
        self.tiles = np.zeros(self.shape, dtype=bool, order="F")
        self.explored = np.zeros(self.shape, dtype=bool, order="F")
        self.visible = np.zeros(self.shape, dtype=bool, order="F")
        self.entities: List[entity.Entity] = []

    def is_blocked(self, x: int, y: int) -> bool:
        """Return True if this position is impassible."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        if not self.tiles[x, y]:
            return True
        for e in self.entities:
            if (
                e.fighter
                and e.fighter.hp > 0
                and e.location
                and e.location.xy == (x, y)
            ):
                return True

        return False

    def fighter_at(self, x: int, y: int) -> Optional[entity.Entity]:
        """Return any fighter entity found at this position."""
        for e in self.entities:
            if (
                e.fighter
                and e.fighter.hp > 0
                and e.location
                and e.location.xy == (x, y)
            ):
                return e
        return None

    def entities_at(self, x: int, y: int) -> Iterator[entity.Entity]:
        """Return all entities at x,y."""
        for e in self.entities:
            if e.location and e.location.xy == (x, y):
                yield e

    def update_fov(self) -> None:
        """Update the field of view around the player."""
        if not self.player.location:
            return
        self.visible = tcod.map.compute_fov(
            transparency=self.tiles,
            pov=self.player.location.xy,
            radius=10,
            light_walls=True,
            algorithm=tcod.FOV_RESTRICTIVE,
        )
        self.explored |= self.visible

    def render(self, console: tcod.console.Console) -> None:
        """Render this maps contents onto a console."""
        console.tiles2["ch"][: self.width, : self.height] = ord(" ")

        dark = np.where(
            self.tiles[..., np.newaxis],
            self.COLOR["dark_ground"],
            self.COLOR["dark_wall"],
        )
        light = np.where(
            self.tiles[..., np.newaxis],
            self.COLOR["light_ground"],
            self.COLOR["light_wall"],
        )
        console.tiles2["bg"][: self.width, : self.height] = np.select(
            (self.visible[..., np.newaxis], self.explored[..., np.newaxis]),
            (light, dark),
            (0, 0, 0),
        )

        visible_objs: Dict[Tuple[int, int], List[Graphic]] = defaultdict(list)
        for obj in self.entities:
            if obj.graphic is None or obj.location is None:
                continue
            xy = obj.location.xy
            if not (0 <= xy[0] < console.width and 0 <= xy[1] < console.height):
                continue
            if not self.visible[xy]:
                continue
            visible_objs[xy].append(obj.graphic)

        for xy, graphics in visible_objs.items():
            graphic = max(graphics, key=lambda x: x.render_order)
            console.tiles2[["ch", "fg"]][xy] = graphic.char, graphic.color

    def __getitem__(self, key: Tuple[int, int]) -> MapLocation:
        return MapLocation(self, *key)
