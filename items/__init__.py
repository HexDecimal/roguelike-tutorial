from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import graphic
from actions import Impossible

if TYPE_CHECKING:
    from actions import ActionWithItem
    from inventory import Inventory
    from location import Location


class Item(graphic.Graphic):
    render_order = 1

    def __init__(self) -> None:
        self.owner: Optional[Inventory] = None
        self.location: Optional[Location] = None

    def lift(self) -> None:
        """Remove this item from any of its containers."""
        if self.owner:
            self.owner.contents.remove(self)
            self.owner = None
        if self.location:
            item_list = self.location.map.items[self.location.xy]
            item_list.remove(self)
            if not item_list:
                del self.location.map.items[self.location.xy]
            self.location = None

    def place(self, location: Location) -> None:
        """Place this item on the floor at the given location."""
        assert not self.location, "This item already has a location."
        assert not self.owner, "Can't be placed because this item is currently owned."
        self.location = location
        items = location.map.items
        try:
            items[location.xy].append(self)
        except KeyError:
            items[location.xy] = [self]

    def plan_activate(self, action: ActionWithItem) -> ActionWithItem:
        """Item activated as part of an action.

        Assume that action has an actor which is holding this items entity.
        """
        return action

    def action_activate(self, action: ActionWithItem) -> None:
        raise Impossible(f"You can do nothing with the {self.name}.")

    def consume(self, action: ActionWithItem) -> None:
        """Remove this item from the actors inventory."""
        assert action.item is self
        action.item.lift()

    def action_drink(self, action: ActionWithItem) -> None:
        """Drink this item."""
        raise Impossible("You can't drink that.")

    def action_eat(self, action: ActionWithItem) -> None:
        """Eat this item."""
        raise Impossible("You can't eat that.")
