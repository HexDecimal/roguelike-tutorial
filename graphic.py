from __future__ import annotations

from typing import Tuple


class Graphic:
    name: str = "<Unnamed>"
    char: int = ord("!")
    color: Tuple[int, int, int] = (255, 255, 255)
    render_order: int = 0

    def __lt__(self, other: Graphic) -> bool:
        """Sort Graphic instances by render_order."""
        return self.render_order < other.render_order
