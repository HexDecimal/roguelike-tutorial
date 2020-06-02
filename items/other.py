from __future__ import annotations

from typing import TYPE_CHECKING

from items import Item

if TYPE_CHECKING:
    from actor import Actor


class Corpse(Item):
    char = ord("%")
    color = (127, 0, 0)
    render_order = 2

    def __init__(self, actor: Actor) -> None:
        super().__init__()
        self.name = f"{actor.fighter.name} Corpse"
