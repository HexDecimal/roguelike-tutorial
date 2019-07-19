from __future__ import annotations

import component
import graphic


class Item(graphic.Graphic, component.Component, base_component=True):
    render_order = 1
    name: str = "<Unnamed>"


class HealingPotion(Item):
    name = "Healing Potion"
    char = ord("!")
    color = (64, 0, 64)
