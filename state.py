from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
import tcod.event

if TYPE_CHECKING:
    import gamemap
    import model


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

    COMMAND_KEYS = {tcod.event.K_ESCAPE: "quit"}

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


class GameState(State):
    def __init__(self, model: model.Model):
        super().__init__()
        self.model = model

    @property
    def active_map(self) -> gamemap.GameMap:
        return self.model.active_map

    def on_draw(self, console: tcod.console.Console) -> None:
        console.clear()
        self.active_map.render(console)

    def cmd_quit(self) -> None:
        """Save and quit."""
        raise SystemExit()

    def cmd_move(self, x: int, y: int) -> None:
        """Move the player entity."""
        player = self.active_map.player
        target = self.active_map.fighter_at(*player.relative(x, y))
        if not self.active_map.is_blocked(*player.relative(x, y)):
            player.move_by(x, y)
            self.active_map.update_fov()
        elif target:
            player.attack(target)
