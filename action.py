from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    import entity
    import model


def move_to(
    model: model.Model, actor: entity.Entity, xy_destination: Tuple[int, int]
) -> None:
    """Move an entity to a position, interacting with obstacles."""
    map_ = model.active_map
    target = map_.fighter_at(*xy_destination)
    if not map_.is_blocked(*xy_destination):
        actor.xy = xy_destination
        map_.update_fov()
    elif target:
        return attack(model, actor, target)


def move(
    model: model.Model, actor: entity.Entity, xy_direction: Tuple[int, int]
) -> None:
    """Move an entity in a direction, interaction with obstacles."""
    move_to(model, actor, actor.relative(*xy_direction))


def move_towards(
    model: model.Model, actor: entity.Entity, destination: Tuple[int, int]
) -> None:
    """Move towards and possibly interact with destination."""
    dx = destination[0] - actor.x
    dy = destination[1] - actor.y
    distance = max(abs(dx), abs(dy))
    dx = int(round(dx / distance))
    dy = int(round(dy / distance))
    return move(model, actor, (dx, dy))


def attack(model: model.Model, actor: entity.Entity, target: entity.Entity) -> None:
    """Make this entities Fighter attack another entity."""
    assert actor.distance_to(target) <= 1
    assert actor.fighter
    assert target.fighter
    damage = actor.fighter.power - target.fighter.defense

    who_desc = f"{actor.fighter.name} attacks {target.fighter.name}"

    if damage > 0:
        target.fighter.hp -= damage
        model.report(f"{who_desc} for {damage} hit points.")
    else:
        model.report(f"{who_desc} but does no damage.")
    if target.fighter.hp <= 0:
        model.report(f"The {target.fighter.name} dies.")
        model.active_map.entities.remove(target)


def attack_player(model: model.Model, actor: entity.Entity) -> None:
    """Move towards and attack the player."""
    return move_towards(model, actor, model.player.xy)
