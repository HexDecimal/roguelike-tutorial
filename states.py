from __future__ import annotations

from typing import Any, TYPE_CHECKING

import tcod
import tcod.console

import actions
from state import State
import rendering

if TYPE_CHECKING:
    from model import Model
    from item import Item


class GameMapState(State):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model

    def on_draw(self, console: tcod.console.Console) -> None:
        rendering.draw_main_view(self.model, console)


class PlayerReady(GameMapState):
    def cmd_quit(self) -> None:
        """Save and quit."""
        raise SystemExit()

    def cmd_move(self, x: int, y: int) -> None:
        """Move the player entity."""
        actions.Move(self.model.player, (x, y)).poll().act()
        self.running = False

    def cmd_pickup(self) -> None:
        actions.Pickup(self.model.player).poll().act()
        self.running = False

    def cmd_inventory(self) -> None:
        state = UseInventory(self.model)
        state.loop()
        self.running = not state.action_taken

    def cmd_drop(self) -> None:
        state = DropInventory(self.model)
        state.loop()
        self.running = not state.action_taken


class GameOver(GameMapState):
    def cmd_quit(self) -> None:
        """Save and quit."""
        raise SystemExit()


class BaseInventoryMenu(GameMapState):
    desc: str  # Banner text.

    def __init__(self, model: Model):
        super().__init__(model)
        self.action_taken = False  # Becomes True if an action was invoked.

    def on_draw(self, console: tcod.console.Console) -> None:
        """Draw inventory menu over the previous state."""
        inventory_ = self.model.player.inventory
        rendering.draw_main_view(self.model, console)
        style: Any = {"fg": (255, 255, 255), "bg": (0, 0, 0)}
        console.print(0, 0, self.desc, **style)
        for i, item in enumerate(inventory_.contents):
            sym = inventory_.symbols[i]
            console.print(0, 2 + i, f"{sym}: {item.name}", **style)

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        # Add check for item based symbols.
        inventory_ = self.model.player.inventory
        if chr(event.sym) in inventory_.symbols:
            index = inventory_.symbols.index(chr(event.sym))
            if index < len(inventory_.contents):
                item = inventory_.contents[index]
                self.pick_item(item)
                return
        super().ev_keydown(event)

    def pick_item(self, item: Item) -> None:
        """Player selected this item."""
        raise NotImplementedError()

    def cmd_quit(self) -> None:
        """Return to previous state."""
        self.running = False


class UseInventory(BaseInventoryMenu):
    desc = "Select an item to USE, or press ESC to exit."

    def pick_item(self, item: Item) -> None:
        self.running = False  # Exit item menu.
        self.action_taken = True
        actions.ActivateItem(self.model.player, item).poll().act()


class DropInventory(BaseInventoryMenu):
    desc = "Select an item to DROP, or press ESC to exit."

    def pick_item(self, item: Item) -> None:
        self.running = False  # Exit item menu.
        self.action_taken = True
        actions.DropItem(self.model.player, item).poll().act()
