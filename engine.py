#!/usr/bin/env python3

import tcod
import tcod.event

import state


def main() -> None:
    screen_width = 80
    screen_height = 50

    tcod.console_set_custom_font("cp437-14.png", tcod.FONT_LAYOUT_CP437, 32, 8)

    with tcod.console_init_root(
        screen_width,
        screen_height,
        "libtcod tutorial revised",
        renderer=tcod.RENDERER_SDL2,
        vsync=True,
        order="F",
    ) as console:
        current_state = state.GameState(console)

        while current_state:
            current_state.on_draw()

            for event in tcod.event.wait():
                current_state.dispatch(event)


if __name__ == "__main__":
    main()
