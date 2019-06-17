#!/usr/bin/env python3

import tcod
import tcod.event


class GameState(tcod.event.EventDispatch):

    MOVE_KEYS = {
        tcod.event.K_LEFT: (-1, 0),
        tcod.event.K_RIGHT: (1, 0),
        tcod.event.K_UP: (0, -1),
        tcod.event.K_DOWN: (0, 1),
        tcod.event.K_HOME: (-1, -1),
        tcod.event.K_END: (-1, 1),
        tcod.event.K_PAGEUP: (1, -1),
        tcod.event.K_PAGEDOWN: (1, 1),
        tcod.event.K_KP_1: (-1, 1),
        tcod.event.K_KP_2: (0, 1),
        tcod.event.K_KP_3: (1, 1),
        tcod.event.K_KP_4: (-1, 0),
        tcod.event.K_KP_6: (1, 0),
        tcod.event.K_KP_7: (-1, -1),
        tcod.event.K_KP_8: (0, -1),
        tcod.event.K_KP_9: (1, -1),
        tcod.event.K_h: (-1, 0),
        tcod.event.K_j: (0, 1),
        tcod.event.K_k: (0, -1),
        tcod.event.K_l: (1, 0),
        tcod.event.K_y: (-1, -1),
        tcod.event.K_u: (1, -1),
        tcod.event.K_b: (-1, 1),
        tcod.event.K_n: (1, 1),
    }

    def __init__(self, console: tcod.console.Console):
        self.console = console
        self.player_xy = console.width // 2, console.height // 2

    def on_draw(self) -> None:
        self.console.clear()
        if (
            0 <= self.player_xy[0] < self.console.width
            and 0 <= self.player_xy[1] < self.console.height
        ):
            self.console.tiles["ch"][self.player_xy] = ord("@")
        tcod.console_flush()

    def ev_quit(self, event: tcod.event.Quit) -> None:
        raise SystemExit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.K_ESCAPE:
            raise SystemExit()
        elif event.sym in self.MOVE_KEYS:
            x, y = self.MOVE_KEYS[event.sym]
            self.player_xy = self.player_xy[0] + x, self.player_xy[1] + y


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
        state = GameState(console)

        while state:
            state.on_draw()

            for event in tcod.event.wait():
                state.dispatch(event)


if __name__ == "__main__":
    main()
