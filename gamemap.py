from __future__ import annotations

import random
from typing import List, Optional, Tuple, Type

import numpy as np  # type: ignore
import tcod.console

import entity
import fighter

WALL = 0
FLOOR = 1


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

    def distance_to(self, other: "Room") -> float:
        """Return an approximate distance from this room to another."""
        x, y = self.center
        other_x, other_y = other.center
        return abs(other_x - x) + abs(other_y - y)

    def place_entities(self, gamemap: GameMap) -> None:
        """Spawn entities within this room."""
        monsters = random.randint(0, 3)
        for _ in range(monsters):
            x = random.randint(self.x1 + 1, self.x2 - 2)
            y = random.randint(self.y1 + 1, self.y2 - 2)
            if gamemap.is_blocked(x, y):
                continue
            monsterCls: Type[fighter.Fighter]
            if random.randint(0, 100) < 80:
                monsterCls = fighter.Orc
            else:
                monsterCls = fighter.Troll
            gamemap.entities.append(entity.Entity(x, y, monsterCls()))


class GameMap:

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
        self.rooms: List[Room] = []

    def generate(self) -> None:
        self.tiles[...] = WALL
        self.rooms = []
        self.entities = []

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
            self.tiles[new_room.inner] = FLOOR
            if self.rooms:
                # Open a tunnel between rooms.
                if random.randint(0, 99) < 80:
                    # 80% of tunnels are to the nearest room.
                    other_room = min(self.rooms, key=new_room.distance_to)
                else:
                    # 20% of tunnels are to the previous generated room.
                    other_room = self.rooms[-1]
                t_start = new_room.center
                t_end = other_room.center
                if random.randint(0, 1):
                    t_middle = t_start[0], t_end[1]
                else:
                    t_middle = t_end[0], t_start[1]
                self.tiles[tcod.line_where(*t_start, *t_middle)] = FLOOR
                self.tiles[tcod.line_where(*t_middle, *t_end)] = FLOOR
            self.rooms.append(new_room)

        for room in self.rooms:
            room.place_entities(self)

        # Add player to the first room.
        self.player = entity.Entity(*self.rooms[0].center, fighter.Player())
        self.entities.append(self.player)
        self.update_fov()

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
