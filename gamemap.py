import random
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

        room_max_size = 10
        room_min_size = 6
        max_rooms = 30

        for i in range(max_rooms):
            # random width and height
            w = random.randint(room_min_size, room_max_size)
            h = random.randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = random.randint(0, self.width - w)
            y = random.randint(0, self.height - h)
            new_room = Room(x, y, w, h)
            if any(new_room.intersects(other) for other in self.rooms):
                continue  # This room intersects with a previous room.

            # Mark room inner area as open.
            self.tiles[new_room.inner] = (1, 1)
            if self.rooms:
                # Open a tunnel between rooms.
                other_room = self.rooms[-1]
                t_start = new_room.center
                t_end = other_room.center
                if random.randint(0, 1):
                    t_middle = t_start[0], t_end[1]
                else:
                    t_middle = t_end[0], t_start[1]
                self.tiles[tcod.line_where(*t_start, *t_middle)] = (1, 1)
                self.tiles[tcod.line_where(*t_middle, *t_end)] = (1, 1)
            self.rooms.append(new_room)

        # Add player to the first room.
        self.player = entity.Entity(*self.rooms[0].center, ord("@"), (255, 255, 255))
        self.entities = [self.player]

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
