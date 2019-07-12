from __future__ import annotations

from typing import Tuple, TYPE_CHECKING
from location import Location
from fighter import Fighter

if TYPE_CHECKING:
    import entity


def move_to(actor: entity.Entity, xy_destination: Tuple[int, int]) -> None:
    """Move an entity to a position, interacting with obstacles."""
    map_ = actor[Location].map
    target = map_.fighter_at(*xy_destination)
    if not map_.is_blocked(*xy_destination):
        actor[Location] = map_[xy_destination]
        map_.update_fov()
    elif target:
        return attack(actor, target)


def move(actor: entity.Entity, xy_direction: Tuple[int, int]) -> None:
    """Move an entity in a direction, interaction with obstacles."""
    move_to(actor, actor[Location].relative(*xy_direction))


def move_towards(actor: entity.Entity, destination: Tuple[int, int]) -> None:
    """Move towards and possibly interact with destination."""
    dx = destination[0] - actor[Location].x
    dy = destination[1] - actor[Location].y
    distance = max(abs(dx), abs(dy))
    dx = int(round(dx / distance))
    dy = int(round(dy / distance))
    return move(actor, (dx, dy))


def attack(actor: entity.Entity, target: entity.Entity) -> None:
    """Make this entities Fighter attack another entity."""
    model = actor[Location].map.model
    assert actor[Location].distance_to(target[Location]) <= 1
    damage = actor[Fighter].power - target[Fighter].defense

    who_desc = f"{actor[Fighter].name} attacks {target[Fighter].name}"

    if damage > 0:
        target[Fighter].hp -= damage
        model.report(f"{who_desc} for {damage} hit points.")
    else:
        model.report(f"{who_desc} but does no damage.")
    if target[Fighter].hp <= 0:
        model.report(f"The {target[Fighter].name} dies.")
        actor[Location].map.entities.remove(target)


def attack_player(actor: entity.Entity) -> None:
    """Move towards and attack the player."""
    return move_towards(actor, actor[Location].map.player[Location].xy)
