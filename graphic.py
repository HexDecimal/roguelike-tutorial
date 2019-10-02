from __future__ import annotations

from typing import Tuple


class Graphic:
    name: str = "<Unnamed>"
    char: int = ord("!")
    color: Tuple[int, int, int] = (255, 255, 255)
    render_order: int = 0
