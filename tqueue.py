from __future__ import annotations

import heapq
from typing import Callable, List, NamedTuple, Optional


class Ticket(NamedTuple):
    """A Ticket represents a specific time and function to call at that time.
    """

    tick: int
    unique_id: int
    func: Callable[[TurnQueue, Ticket], None]  # type: ignore
    # https://github.com/python/mypy/issues/731


class TurnQueue:
    def __init__(self) -> None:
        self.current_tick = 0
        self.last_unique_id = 0  # Used to sort same-tick ticks in FIFO order.
        self.heap: List[Ticket] = []

    def schedule(
        self, interval: int, func: Callable[[TurnQueue, Ticket], None]
    ) -> Ticket:
        """Add a callable object to the turn queue.

        `interval` is the time to wait from the current time.

        `func` is the function to call during the scheduled time.

        Returns the newly scheduled Ticket instance.
        """
        ticket = Ticket(self.current_tick + interval, self.last_unique_id, func)
        heapq.heappush(self.heap, ticket)
        self.last_unique_id += 1
        return ticket

    def reschedule(
        self,
        ticket: Ticket,
        interval: int,
        func: Optional[Callable[[TurnQueue, Ticket], None]] = None,
    ) -> Ticket:
        """Reschedule a new Ticket in place of the existing one.

        `ticket` must be the currently active Ticket.

        `interval` is the time to wait from the current time.

        `func` is the function to call during the scheduled time.  It may be
        None to reuse the function from `ticket`.

        Returns the newly scheduled Ticket instance.
        """
        assert ticket is not None
        assert self.heap[0] is ticket
        ticket = Ticket(
            self.current_tick + interval,
            self.last_unique_id,
            ticket.func if func is None else func,
        )
        heapq.heappushpop(self.heap, ticket)
        self.last_unique_id += 1
        return ticket

    def unschedule(self, ticket: Ticket) -> None:
        """Explicitly remove the current ticket.

        `ticket` must be the currently active Ticket.
        """
        assert ticket is not None
        assert self.heap[0] is ticket
        heapq.heappop(self.heap)

    def invoke_next(self) -> None:
        """Call the next scheduled function.

        This expects the scheduled function to take care of removing or
        rescheduling its own Ticket object.  It will fail otherwise.
        """
        ticket = self.heap[0]
        self.current_tick = ticket.tick
        ticket.func(self, ticket)
        assert ticket is not self.heap[0], f"{ticket!r} was not rescheduled."
