from __future__ import annotations

import random
from typing import List, Optional

import numpy as np  # type: ignore
import tcod.console

import entity


class GameMap:
    """An object which holds the tile and entity data for a single floor."""

    COLOR = {
        "dark_wall": (0, 0, 100),
        "dark_ground": (50, 50, 150),
        "light_wall": (130, 110, 50),
        "light_ground": (200, 180, 50),
    }

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
        if self.fighter_at(x, y):
            return True

        return False

    def fighter_at(self, x: int, y: int) -> Optional[entity.Entity]:
        """Return any fighter entity found at this position."""
        for e in self.entities:
            if x == e.x and y == e.y:
                return e
        return None

    def update_fov(self) -> None:
        """Update the field of view around the player."""
        self.visible = tcod.map.compute_fov(
            transparency=self.tiles,
            pov=(self.player.x, self.player.y),
            radius=10,
            light_walls=True,
            algorithm=tcod.FOV_RESTRICTIVE,
        )
        self.explored |= self.visible

    def render(self, console: tcod.console.Console) -> None:
        """Render this maps contents onto a console."""
        console.tiles["ch"][: self.width, : self.height] = ord(" ")

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
        console.tiles["bg"][: self.width, : self.height, :3] = np.select(
            (self.visible[..., np.newaxis], self.explored[..., np.newaxis]),
            (light, dark),
            (0, 0, 0),
        )

        for obj in self.entities:
            if not (0 <= obj.x < console.width and 0 <= obj.y < console.height):
                continue
            if not self.visible[obj.x, obj.y]:
                continue
            console.tiles["ch"][obj.x, obj.y] = obj.char
            console.tiles["fg"][obj.x, obj.y, :3] = obj.color
