from __future__ import annotations

from typing import List, TYPE_CHECKING

import states

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

    @property
    def player(self) -> Actor:
        return self.active_map.player

    def report(self, text: str) -> None:
        print(text)
        if self.log and self.log[-1].text == text:
            self.log[-1].count += 1
        else:
            self.log.append(Message(text))

    def is_player_dead(self) -> bool:
        """True if the player had died."""
        return not self.player.fighter or self.player.fighter.hp <= 0

    def loop(self) -> None:
        while True:
            if self.is_player_dead():
                states.GameOver(self).loop()
                continue
            self.active_map.scheduler.invoke_next()
