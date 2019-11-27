from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

import actions
import state

import tcod

if TYPE_CHECKING:
    from entity import Entity
    from model import Model


class Inventory:
    symbols = "abcdefghijklmnopqrstuvwxyz"
    capacity = len(symbols)

    def __init__(self) -> None:
        self.contents: List[Entity] = []

    def take(self, entity: Entity) -> None:
        self.contents.append(entity)
        assert entity.location
        entity.location.map.entities.remove(entity)
        entity.location = None


class InventoryMenu(state.State):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model

    def on_draw(self, console: tcod.console.Console) -> None:
        """Draw inventory menu over the previous state."""
        assert self.model.player.inventory
        self.parent.on_draw(console)
        style: Any = {"fg": (255, 255, 255), "bg": (0, 0, 0)}
        console.print(0, 0, "Inventory:", **style)
        for i, e in enumerate(self.model.player.inventory.contents):
            assert e.item
            sym = Inventory.symbols[i]
            console.print(0, 2 + i, f"{sym}: {e.item.name}", **style)

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        # Add check for item based symbols.
        assert self.model.player.inventory
        if chr(event.sym) in Inventory.symbols:
            index = Inventory.symbols.index(chr(event.sym))
            if index < len(self.model.player.inventory.contents):
                item = self.model.player.inventory.contents[index]
                self.pick_item(item)
                return
        super().ev_keydown(event)

    def pick_item(self, item: Entity) -> None:
        """Player selected this item."""
        self.pop()  # Exit item menu.
        actions.ActivateItem(self.model.player, item).act()
        self.model.enemy_turn()

    def cmd_quit(self) -> None:
        """Return to previous state."""
        self.pop()
