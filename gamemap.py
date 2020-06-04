from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod

from location import Location
from tqueue import TurnQueue

if TYPE_CHECKING:
    import tcod.console
    from actor import Actor
    from graphic import Graphic
    from items import Item
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
    player: Actor

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.shape = width, height
        self.tiles = np.zeros(self.shape, dtype=tile_dt, order="F")
        self.explored = np.zeros(self.shape, dtype=bool, order="F")
        self.visible = np.zeros(self.shape, dtype=bool, order="F")
        self.actors: List[Actor] = []
        self.items: Dict[Tuple[int, int], List[Item]] = {}
        self.camera_xy = (0, 0)  # Camera center position.
        self.scheduler = TurnQueue()

    def is_blocked(self, x: int, y: int) -> bool:
        """Return True if this position is impassible."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        if not self.tiles[x, y]["move_cost"]:
            return True
        if any(actor.location.xy == (x, y) for actor in self.actors):
            return True

        return False

    def fighter_at(self, x: int, y: int) -> Optional[Actor]:
        """Return any fighter entity found at this position."""
        for actor in self.actors:
            if actor.location.xy == (x, y):
                return actor
        return None

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

    def get_camera_pos(self, console: tcod.console.Console) -> Tuple[int, int]:
        """Get the upper left camera position, assuming camera_xy is the center."""
        cam_x = self.camera_xy[0] - console.width // 2
        cam_y = self.camera_xy[1] - console.height // 2
        return cam_x, cam_y

    def get_camera_views(
        self, console: tcod.console.Console
    ) -> Tuple[Tuple[slice, slice], Tuple[slice, slice]]:
        """Return (screen_view, world_view) as 2D slices for use with NumPy."""
        cam_x, cam_y = self.get_camera_pos(console)

        screen_left = max(0, -cam_x)
        screen_top = max(0, -cam_y)

        world_left = max(0, cam_x)
        world_top = max(0, cam_y)

        screen_width = min(console.width - screen_left, self.width - world_left)
        screen_height = min(console.height - screen_top, self.height - world_top)

        screen_view = np.s_[
            screen_left : screen_left + screen_width,
            screen_top : screen_top + screen_height,
        ]
        world_view = np.s_[
            world_left : world_left + screen_width,
            world_top : world_top + screen_height,
        ]

        return screen_view, world_view

    def render(self, console: tcod.console.Console) -> None:
        """Render this maps contents onto a console."""
        cam_x, cam_y = self.get_camera_pos(console)

        # Get the screen and world view slices.
        screen_view, world_view = self.get_camera_views(console)

        # Draw the console based on visible or explored areas.
        console.tiles_rgb[screen_view] = np.select(
            (self.visible[world_view], self.explored[world_view]),
            (self.tiles["light"][world_view], self.tiles["dark"][world_view]),
            self.DARKNESS,
        )

        # Collect and filter the various entity objects.
        visible_objs: Dict[Tuple[int, int], List[Graphic]] = defaultdict(list)
        for obj in self.actors:
            obj_x, obj_y = obj.location.x - cam_x, obj.location.y - cam_y
            if not (0 <= obj_x < console.width and 0 <= obj_y < console.height):
                continue
            if not self.visible[obj.location.xy]:
                continue
            visible_objs[obj_x, obj_y].append(obj.fighter)
        for (item_x, item_y), items in self.items.items():
            obj_x, obj_y = item_x - cam_x, item_y - cam_y
            if not (0 <= obj_x < console.width and 0 <= obj_y < console.height):
                continue
            if not self.visible[item_x, item_y]:
                continue
            visible_objs[obj_x, obj_y].extend(items)

        # Draw the visible entities.
        for xy, graphics in visible_objs.items():
            graphic = min(graphics)
            console.tiles_rgb[["ch", "fg"]][xy] = graphic.char, graphic.color

    def __getitem__(self, key: Tuple[int, int]) -> MapLocation:
        return MapLocation(self, *key)
