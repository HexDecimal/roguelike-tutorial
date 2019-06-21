#!/usr/bin/env python3

import sys

import warnings

import tcod
import tcod.event

import state
import gamemap


def main() -> None:
    screen_width = 80
    screen_height = 50
    map_width, map_height = 80, 45

    tcod.console_set_custom_font("cp437-14.png", tcod.FONT_LAYOUT_CP437, 32, 8)

    with tcod.console_init_root(
        screen_width,
        screen_height,
        "libtcod tutorial revised",
        renderer=tcod.RENDERER_SDL2,
        vsync=True,
        order="F",
    ) as console:
        game_map = gamemap.GameMap(map_width, map_height)
        game_map.generate()
        current_state = state.GameState(game_map)

        while current_state:
            current_state.on_draw(console)

            for event in tcod.event.wait():
                current_state.dispatch(event)


if __name__ == "__main__":
    if not sys.warnoptions:
        warnings.simplefilter("default")
    main()
