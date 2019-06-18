from typing import List

import numpy as np  # type: ignore
import tcod.console

import entity


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

    def generate(self) -> None:
        self.tiles[...] = (1, 1)

        self.tiles[30:33, 22] = (0, 0)

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
