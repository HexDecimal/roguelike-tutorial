from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import effect
import graphic

if TYPE_CHECKING:
    from actor import Actor
    from action import ActionWithItem
    from location import Location
    from inventory import Inventory


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

    def activate(self, action: ActionWithItem) -> None:
        """Item activated as part of an action.

        Assume that action has an actor which is holding this items entity.
        """
        action.report(f"You can do nothing with the {self.name}.")
        raise NotImplementedError()

    def consume(self, action: ActionWithItem) -> None:
        """Remove this item from the actors inventory."""
        assert action.item is self
        action.item.lift()


class Potion(Item):
    name = "Potion"
    char = ord("!")
    color = (255, 255, 255)

    def __init__(self, my_effect: effect.Effect):
        super().__init__()
        self.my_effect = my_effect

    def activate(self, action: ActionWithItem) -> None:
        self.consume(action)
        self.my_effect.apply(action, action.actor)


class HealingPotion(Potion):
    name = "Healing Potion"
    color = (64, 0, 64)

    def __init__(self) -> None:
        super().__init__(effect.Healing(4))


class Corpse(Item):
    char = ord("%")
    color = (127, 0, 0)
    render_order = 2

    def __init__(self, actor: Actor) -> None:
        super().__init__()
        self.name = f"{actor.fighter.name} Corpse"
