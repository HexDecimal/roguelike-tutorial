from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar, TYPE_CHECKING

import tcod
import tcod.console

from actions import common
from states import State, StateBreak
import rendering

if TYPE_CHECKING:
    import actions
    from model import Model
    from items import Item

T = TypeVar("T")


class GameMapState(Generic[T], State[T]):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model

    def on_draw(self, console: tcod.console.Console) -> None:
        rendering.draw_main_view(self.model, console)


class PlayerReady(GameMapState["actions.Action"]):
    def cmd_quit(self) -> None:
        """Save and quit."""
        raise SystemExit()

    def cmd_move(self, x: int, y: int) -> actions.Action:
        """Move the player entity."""
        return common.Move(self.model.player, (x, y))

    def cmd_pickup(self) -> actions.Action:
        return common.Pickup(self.model.player)

    def cmd_inventory(self) -> Optional[actions.Action]:
        state = UseInventory(self.model)
        return state.loop()

    def cmd_drop(self) -> Optional[actions.Action]:
        state = DropInventory(self.model)
        return state.loop()


class GameOver(GameMapState[None]):
    def cmd_quit(self) -> None:
        """Save and quit."""
        raise SystemExit()


class BaseInventoryMenu(GameMapState["actions.Action"]):
    desc: str  # Banner text.

    def __init__(self, model: Model):
        super().__init__(model)

    def on_draw(self, console: tcod.console.Console) -> None:
        """Draw inventory menu over the previous state."""
        inventory_ = self.model.player.inventory
        rendering.draw_main_view(self.model, console)
        style: Any = {"fg": (255, 255, 255), "bg": (0, 0, 0)}
        console.print(0, 0, self.desc, **style)
        for i, item in enumerate(inventory_.contents):
            sym = inventory_.symbols[i]
            console.print(0, 2 + i, f"{sym}: {item.name}", **style)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[actions.Action]:
        # Add check for item based symbols.
        inventory_ = self.model.player.inventory
        char: Optional[str] = None
        try:
            char = chr(event.sym)
        except ValueError:
            pass  # Suppress exceptions for non-character keys.
        if char and char in inventory_.symbols:
            index = inventory_.symbols.index(char)
            if index < len(inventory_.contents):
                item = inventory_.contents[index]
                return self.pick_item(item)
        return super().ev_keydown(event)

    def pick_item(self, item: Item) -> Optional[actions.Action]:
        """Player selected this item."""
        raise NotImplementedError()

    def cmd_quit(self) -> None:
        """Return to previous state."""
        raise StateBreak()


class UseInventory(BaseInventoryMenu):
    desc = "Select an item to USE, or press ESC to exit."

    def pick_item(self, item: Item) -> actions.Action:
        return common.ActivateItem(self.model.player, item)


class DropInventory(BaseInventoryMenu):
    desc = "Select an item to DROP, or press ESC to exit."

    def pick_item(self, item: Item) -> actions.Action:
        return common.DropItem(self.model.player, item)
