from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from fighter import Fighter
    from location import Location
    from graphic import Graphic
    from ai import AI
    from inventory import Inventory
    from item import Item
    from tqueue import TurnQueue, Ticket


@dataclass
class Entity:
    """Object used to tie a variety of components to a location on a GameMap."""

    location: Optional[Location] = None
    graphic: Optional[Graphic] = None
    fighter: Optional[Fighter] = None
    ai: Optional[AI] = None
    inventory: Optional[Inventory] = None
    item: Optional[Item] = None
    ticket: Optional[Ticket] = None

    def act(self, scheduler: TurnQueue, ticket: Ticket) -> None:
        if ticket is not self.ticket or self.ai is None:
            return scheduler.unschedule(ticket)
        self.ai.take_turn(self)
