#!/usr/bin/env python3
import sys
import warnings

import tcod

import g
import states.mainmenu


def main() -> None:
    screen_width = 720
    screen_height = 480

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
        g.console = tcod.Console(*g.context.recommended_console_size())
        states.mainmenu.MainMenu().loop()


if __name__ == "__main__":
    if not sys.warnoptions:
        warnings.simplefilter("default")  # Show all warnings once by default.
    main()
