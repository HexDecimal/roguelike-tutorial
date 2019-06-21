from typing import List, Tuple

import numpy as np  # type: ignore
import tcod.console

import entity


class Room:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def outer(self) -> Tuple[slice, slice]:
        """Return the NumPy index for the whole room."""
        index: Tuple[slice, slice] = np.s_[self.x1 : self.x2, self.y1 : self.y2]
        return index

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the NumPy index for the inner room area."""
        index: Tuple[slice, slice] = np.s_[
            self.x1 + 1 : self.x2 - 1, self.y1 + 1 : self.y2 - 1
        ]
        return index

    @property
    def center(self) -> Tuple[int, int]:
        """Return the index for the rooms center coordinate."""
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    def intersects(self, other: "Room") -> bool:
        """Return True if this room intersects with another."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


class GameMap:

    DTYPE = [("transparent", bool), ("walkable", bool)]

    COLOR = {"dark_wall": (0, 0, 100), "dark_ground": (50, 50, 150)}

    player: entity.Entity

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.shape = width, height
        self.tiles = np.empty(self.shape, dtype=self.DTYPE, order="F")
        self.tiles[...] = (1, 1)
        self.entities: List[entity.Entity] = []
        self.rooms: List[Room] = []

    def generate(self) -> None:
        self.tiles[...] = (0, 0)
        self.rooms = []

        room1 = Room(20, 15, 10, 15)
        room2 = Room(35, 15, 10, 15)

        self.tiles[room1.inner] = (1, 1)
        self.tiles[room2.inner] = (1, 1)
        self.tiles[tcod.line_where(*room1.center, *room2.center)] = (1, 1)

        self.player = entity.Entity(
            self.width // 2, self.height // 2, ord("@"), (255, 255, 255)
        )
        npc = entity.Entity(
            self.player.x - 5, self.player.y - 5, ord("@"), (255, 255, 0)
        )
        self.entities = [npc, self.player]

    def is_blocked(self, x: int, y: int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        if not self.tiles[x, y]["walkable"]:
            return True

        return False

    def render(self, console: tcod.console.Console) -> None:
        console.tiles["ch"][: self.width, : self.height] = ord(" ")

        dark = np.where(
            self.tiles["transparent"][..., np.newaxis],
            self.COLOR["dark_ground"],
            self.COLOR["dark_wall"],
        )

        console.tiles["bg"][: self.width, : self.height, :3] = dark

        for obj in self.entities:
            if 0 <= obj.x < console.width and 0 <= obj.y < console.height:
                console.tiles["ch"][obj.x, obj.y] = obj.char
                console.tiles["fg"][obj.x, obj.y, :3] = obj.color
