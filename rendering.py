from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import tcod.console

if TYPE_CHECKING:
    from tcod.console import Console
    from model import Model


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
    bar_bg = console.tiles_rgb["bg"][x : x + width, y]
    bar_bg[...] = bg
    fill_width = max(0, min(width, int(fullness * width)))
    bar_bg[:fill_width] = fg


def draw_main_view(model: Model, console: Console) -> None:
    bar_width = 20
    player = model.player
    if player.location:
        model.active_map.camera_xy = player.location.xy

    console.clear()
    model.active_map.render(console)

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
    for text in model.log[::-1]:
        i += tcod.console.get_height_rect(log_width, str(text))
        if i >= 7:
            break
        console.print_box(x, y - i, log_width, 0, str(text))
