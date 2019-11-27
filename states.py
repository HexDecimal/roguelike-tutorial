from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import tcod
import tcod.console

import actions
from state import State
import inventory

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
        assert player.fighter

        console.clear()
        self.active_map.render(console)

        render_bar(
            console,
            1,
            console.height - 2,
            bar_width,
            f"HP: {player.fighter.hp:02}/{player.fighter.max_hp:02}",
            player.fighter.hp / player.fighter.max_hp,
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

    def is_player_dead(self) -> bool:
        """True if the player had died."""
        return not self.model.player.fighter or self.model.player.fighter.hp <= 0

    def cmd_quit(self) -> None:
        """Save and quit."""
        raise SystemExit()

    def cmd_move(self, x: int, y: int) -> None:
        """Move the player entity."""
        if self.is_player_dead():
            return
        actions.Move(self.model.player, (x, y)).act()
        self.model.enemy_turn()

    def cmd_pickup(self) -> None:
        if self.is_player_dead():
            return
        actions.Pickup(self.model.player).act()
        self.model.enemy_turn()

    def cmd_inventory(self) -> None:
        if self.is_player_dead():
            return
        inventory.InventoryMenu(self.model).push()
