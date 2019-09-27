from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import tcod
import tcod.console
import tcod.event

import action
from fighter import Fighter

if TYPE_CHECKING:
    import gamemap
    import model


def render_bar(
    console: tcod.console.Console,
    x: int,
    y: int,
    width: int,
    text: str,
    fullness: float,
    fg: Tuple[int, int, int],
    bg: Tuple[int, int, int],
) -> None:
    """Render a filled bar with centered text."""
    console.print(x, y, text.center(width)[:width], fg=(255, 255, 255))
    bar_bg = console.tiles2["bg"][x : x + width, y]
    bar_bg[...] = bg
    fill_width = max(0, min(width, int(fullness * width)))
    bar_bg[:fill_width] = fg


class State(tcod.event.EventDispatch):
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

    COMMAND_KEYS = {tcod.event.K_ESCAPE: "quit", tcod.event.K_g: "pickup"}

    def run(self, console: tcod.console.Console) -> None:
        while True:
            self.on_draw(console)
            tcod.console_flush()
            for event in tcod.event.wait():
                self.dispatch(event)

    def on_draw(self, console: tcod.console.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.cmd_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym in self.COMMAND_KEYS:
            getattr(self, f"cmd_{self.COMMAND_KEYS[event.sym]}")()
        elif event.sym in self.MOVE_KEYS:
            self.cmd_move(*self.MOVE_KEYS[event.sym])

    def cmd_quit(self) -> None:
        """Save and quit."""
        raise SystemExit()

    def cmd_move(self, x: int, y: int) -> None:
        pass

    def cmd_pickup(self) -> None:
        pass


class GameState(State):
    def __init__(self, model: model.Model):
        super().__init__()
        self.model = model

    @property
    def active_map(self) -> gamemap.GameMap:
        return self.model.active_map

    def on_draw(self, console: tcod.console.Console) -> None:
        bar_width = 20
        player = self.model.player

        console.clear()
        self.active_map.render(console)

        render_bar(
            console,
            1,
            console.height - 2,
            bar_width,
            f"HP: {player[Fighter].hp:02}/{player[Fighter].max_hp:02}",
            player[Fighter].hp / player[Fighter].max_hp,
            (0x40, 0x80, 0),
            (0x80, 0, 0),
        )

        x = bar_width + 2
        y = console.height
        log_width = console.width - x
        i = 0
        for text in self.model.log[::-1]:
            i += tcod.console.get_height_rect(log_width, text)
            if i >= 7:
                break
            console.print_box(x, y - i, log_width, 0, text)

    def cmd_quit(self) -> None:
        """Save and quit."""
        raise SystemExit()

    def cmd_move(self, x: int, y: int) -> None:
        """Move the player entity."""
        action.move(self.model.player, (x, y))
        self.model.enemy_turn()

    def cmd_pickup(self) -> None:
        action.pickup(self.model.player)
        self.model.enemy_turn()
