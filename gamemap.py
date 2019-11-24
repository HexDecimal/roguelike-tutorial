from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterator, List, NamedTuple, Optional, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod

from location import Location

if TYPE_CHECKING:
    import tcod.console
    import entity
    from graphic import Graphic
    from model import Model

# Data types for handling game map tiles:
tile_graphic = np.dtype([("ch", np.int), ("fg", "3B"), ("bg", "3B")])
tile_dt = np.dtype(
    [
        ("move_cost", np.uint8),
        ("transparent", np.bool),
        ("light", tile_graphic),
        ("dark", tile_graphic),
    ]
)


class Tile(NamedTuple):
    """A NamedTuple type broadcastable to any tile_dt array."""

    move_cost: int
    transparent: bool
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]


class MapLocation(Location):
    def __init__(self, gamemap: GameMap, x: int, y: int):
        self.map = gamemap
        self.x = x
        self.y = y


class GameMap:
    """An object which holds the tile and entity data for a single floor."""

    DARKNESS = np.asarray((0, (0, 0, 0), (0, 0, 0)), dtype=tile_graphic)

    model: Model
    player: entity.Entity

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.shape = width, height
        self.tiles = np.zeros(self.shape, dtype=tile_dt, order="F")
        self.explored = np.zeros(self.shape, dtype=bool, order="F")
        self.visible = np.zeros(self.shape, dtype=bool, order="F")
        self.entities: List[entity.Entity] = []

    def is_blocked(self, x: int, y: int) -> bool:
        """Return True if this position is impassible."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        if not self.tiles[x, y]["move_cost"]:
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
            transparency=self.tiles["transparent"],
            pov=self.player.location.xy,
            radius=10,
            light_walls=True,
            algorithm=tcod.FOV_RESTRICTIVE,
        )
        self.explored |= self.visible

    def render(self, console: tcod.console.Console) -> None:
        """Render this maps contents onto a console."""
        console.tiles2[: self.width, : self.height] = np.select(
            (self.visible, self.explored),
            (self.tiles["light"], self.tiles["dark"]),
            self.DARKNESS,
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
            graphic = min(graphics)
            console.tiles2[["ch", "fg"]][xy] = graphic.char, graphic.color

    def __getitem__(self, key: Tuple[int, int]) -> MapLocation:
        return MapLocation(self, *key)
