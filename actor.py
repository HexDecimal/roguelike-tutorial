from __future__ import annotations

import sys

import traceback
from typing import Optional, Type, TYPE_CHECKING

from action import NoAction

if TYPE_CHECKING:
    from ai import AI
    from fighter import Fighter
    from location import Location
    from inventory import Inventory
    from tqueue import TurnQueue, Ticket


class Actor:
    def __init__(self, location: Location, fighter: Fighter, ai_cls: Type[AI]):
        self.location = location
        self.fighter = fighter
        location.map.actors.append(self)
        self.ticket: Optional[Ticket] = location.map.scheduler.schedule(0, self.act)
        self.ai = ai_cls(self)

    def act(self, scheduler: TurnQueue, ticket: Ticket) -> None:
        if ticket is not self.ticket:
            return scheduler.unschedule(ticket)
        try:
            action = self.ai.plan()
        except NoAction:
            print(f"Unresolved action with {self}!", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return self.ai.reschedule(100)
        assert action is action.plan(), f"{action} was not fully resolved, {self}."
        action.act()

    @property
    def inventory(self) -> Inventory:
        return self.fighter.inventory

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.location!r}, {self.fighter!r})"
