from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from fighter import Fighter
    from location import Location
    from inventory import Inventory
    from tqueue import TurnQueue, Ticket


class Actor:
    def __init__(self, location: Location, fighter: Fighter):
        self.location = location
        self.fighter = fighter
        location.map.actors.append(self)
        self.ticket: Optional[Ticket] = location.map.scheduler.schedule(0, self.act)

    def act(self, scheduler: TurnQueue, ticket: Ticket) -> None:
        if ticket is not self.ticket:
            return scheduler.unschedule(ticket)
        self.fighter.ai.take_turn(self)

    @property
    def inventory(self) -> Inventory:
        return self.fighter.inventory

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.location!r}, {self.fighter!r})"
