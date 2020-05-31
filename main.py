#!/usr/bin/env python3
import sys

import warnings

import tcod

import model
import procgen.dungeon
import g


def main() -> None:
    screen_width = 720
    screen_height = 480
    map_width, map_height = 80, 45

    tileset = tcod.tileset.load_tilesheet(
        "data/cp437-14.png", 32, 8, tcod.tileset.CHARMAP_CP437
    )
    with tcod.context.new_window(
        width=screen_width,
        height=screen_height,
        tileset=tileset,
        title="libtcod tutorial revised",
        renderer=tcod.RENDERER_SDL2,
        vsync=True,
    ) as g.context:
        g.console = tcod.Console(*g.context.recommended_console_size(), order="F")
        model_ = model.Model()
        model_.active_map = procgen.dungeon.generate(map_width, map_height)
        model_.active_map.model = model_
        model_.loop()


if __name__ == "__main__":
    if not sys.warnoptions:
        warnings.simplefilter("default")  # Show all warnings once by default.
    main()
