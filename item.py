from __future__ import annotations

import graphic


class Item(graphic.Graphic):
    render_order = 1


class HealingPotion(Item):
    name = "Healing Potion"
    char = ord("!")
    color = (64, 0, 64)
