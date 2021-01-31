from __future__ import annotations

from typing import TYPE_CHECKING, List

import states.ingame
import tqueue

if TYPE_CHECKING:
    from actor import Actor
    from gamemap import GameMap


class Message:
    def __init__(self, text: str) -> None:
        self.text = text
        self.count = 1

    def __str__(self) -> str:
        if self.count > 1:
            return f"{self.text} (x{self.count})"
        return self.text


class Model:
    """The model contains everything from a session which should be saved."""

    active_map: GameMap

    def __init__(self) -> None:
        self.log: List[Message] = []
        self.scheduler = tqueue.TurnQueue()

    @property
    def player(self) -> Actor:
        return self.active_map.player

    def report(self, text: str) -> None:
        print(text)
        if self.log and self.log[-1].text == text:
            self.log[-1].count += 1
        else:
            self.log.append(Message(text))

    @property
    def is_player_dead(self) -> bool:
        """True if the player had died."""
        return not self.player.fighter or self.player.fighter.hp <= 0

    def loop(self) -> None:
        while True:
            if self.is_player_dead:
                states.ingame.GameOver(self).loop()
                continue
            self.scheduler.invoke_next()
