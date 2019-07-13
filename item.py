from __future__ import annotations

from typing import Tuple

import component


class Item(component.Component, base_component=True):
    name: str = "<Unnamed>"
    char: int = ord("!")
    color: Tuple[int, int, int] = (255, 255, 255)


class HealingPotion(Item):
    name = "Healing Potion"
    char = ord("!")
    color = (64, 0, 64)
