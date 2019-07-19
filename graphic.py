from __future__ import annotations

from typing import Tuple


class Graphic:
    char: int = ord("!")
    color: Tuple[int, int, int] = (255, 255, 255)
    render_order: int = 0
