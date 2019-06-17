#!/usr/bin/env python3

import tcod
import tcod.event


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
        while True:
            console.tiles["ch"][1, 1] = ord("@")
            tcod.console_flush()

            for event in tcod.event.wait():
                if event.type == "QUIT":
                    raise SystemExit()
                elif event.type == "KEYDOWN":
                    if event.sym == tcod.event.K_ESCAPE:
                        raise SystemExit()


if __name__ == "__main__":
    main()
