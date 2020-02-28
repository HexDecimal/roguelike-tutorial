#!/usr/bin/env python3
import sys

import warnings

import tcod

import model
import state
import procgen


def main() -> None:
    screen_width = 80
    screen_height = 50
    map_width, map_height = 80, 45

    tcod.console_set_custom_font("data/cp437-14.png", tcod.FONT_LAYOUT_CP437, 32, 8)

    with tcod.console_init_root(
        screen_width,
        screen_height,
        "libtcod tutorial revised",
        renderer=tcod.RENDERER_SDL2,
        vsync=True,
        order="F",
    ) as state.g_console:
        model_ = model.Model()
        model_.active_map = procgen.generate(map_width, map_height)
        model_.active_map.model = model_
        model_.loop()


if __name__ == "__main__":
    if not sys.warnoptions:
        warnings.simplefilter("default")  # Show all warnings once by default.
    main()
