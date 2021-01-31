from __future__ import annotations

from typing import Callable, Generic, Optional, TypeVar

import tcod

import g

CONSOLE_MIN_SIZE = (32, 10)  # The smallest acceptable main console size.

T = TypeVar("T")


class StateBreak(Exception):
    """Breaks out of the active State.loop and makes it return None."""


class SaveAndQuit(Exception):
    pass


class GameOverQuit(Exception):
    pass


class State(Generic[T], tcod.event.EventDispatch[T]):
    MOVE_KEYS = {
        # Arrow keys.
        tcod.event.K_LEFT: (-1, 0),
        tcod.event.K_RIGHT: (1, 0),
        tcod.event.K_UP: (0, -1),
        tcod.event.K_DOWN: (0, 1),
        tcod.event.K_HOME: (-1, -1),
        tcod.event.K_END: (-1, 1),
        tcod.event.K_PAGEUP: (1, -1),
        tcod.event.K_PAGEDOWN: (1, 1),
        tcod.event.K_PERIOD: (0, 0),
        # Numpad keys.
        tcod.event.K_KP_1: (-1, 1),
        tcod.event.K_KP_2: (0, 1),
        tcod.event.K_KP_3: (1, 1),
        tcod.event.K_KP_4: (-1, 0),
        tcod.event.K_KP_5: (0, 0),
        tcod.event.K_CLEAR: (0, 0),
        tcod.event.K_KP_6: (1, 0),
        tcod.event.K_KP_7: (-1, -1),
        tcod.event.K_KP_8: (0, -1),
        tcod.event.K_KP_9: (1, -1),
        # Vi keys.
        tcod.event.K_h: (-1, 0),
        tcod.event.K_j: (0, 1),
        tcod.event.K_k: (0, -1),
        tcod.event.K_l: (1, 0),
        tcod.event.K_y: (-1, -1),
        tcod.event.K_u: (1, -1),
        tcod.event.K_b: (-1, 1),
        tcod.event.K_n: (1, 1),
    }

    COMMAND_KEYS = {
        tcod.event.K_d: "drop",
        tcod.event.K_i: "inventory",
        tcod.event.K_g: "pickup",
        tcod.event.K_ESCAPE: "escape",
        tcod.event.K_RETURN: "confirm",
        tcod.event.K_KP_ENTER: "confirm",
    }

    def loop(self) -> Optional[T]:
        """Run a state based game loop."""
        while True:
            self.on_draw(g.console)
            g.context.present(g.console, keep_aspect=True, integer_scaling=True)
            for event in tcod.event.wait():
                if event.type == "WINDOWRESIZED":
                    g.console = configure_console()
                try:
                    value = self.dispatch(event)
                except StateBreak:
                    return None  # Events may raise StateBreak to exit this state.
                if value is not None:
                    return value

    def on_draw(self, console: tcod.console.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[T]:
        return self.cmd_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[T]:
        func: Callable[[], Optional[T]]
        if event.sym in self.COMMAND_KEYS:
            func = getattr(self, f"cmd_{self.COMMAND_KEYS[event.sym]}")
            return func()
        elif event.sym in self.MOVE_KEYS:
            return self.cmd_move(*self.MOVE_KEYS[event.sym])
        return None

    def cmd_confirm(self) -> Optional[T]:
        pass

    def cmd_escape(self) -> Optional[T]:
        raise StateBreak()

    def cmd_quit(self) -> Optional[T]:
        """Save and quit."""
        raise SystemExit()

    def cmd_move(self, x: int, y: int) -> Optional[T]:
        pass

    def cmd_pickup(self) -> Optional[T]:
        pass

    def cmd_inventory(self) -> Optional[T]:
        pass

    def cmd_drop(self) -> Optional[T]:
        pass


def configure_console() -> tcod.console.Console:
    """Return a new main console with an automatically determined size."""
    return tcod.Console(*g.context.recommended_console_size(*CONSOLE_MIN_SIZE))
