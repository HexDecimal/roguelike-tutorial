from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    import entity
    import model


def move(
    model: model.Model, actor: entity.Entity, xy_direction: Tuple[int, int]
) -> None:
    """Move an entity in a direction, interaction with obstacles."""
    player = model.player
    xy_destination = player.relative(*xy_direction)
    map_ = model.active_map
    target = map_.fighter_at(*xy_destination)
    if not map_.is_blocked(*xy_destination):
        player.x, player.y = xy_destination
        map_.update_fov()
    elif target:
        attack(model, actor, target)


def attack(model: model.Model, actor: entity.Entity, target: entity.Entity) -> None:
    """Make this entities Fighter attack another entity."""
    assert abs(actor.x - target.x) <= 1
    assert abs(actor.y - target.y) <= 1
    assert actor.fighter
    assert target.fighter
    damage = actor.fighter.power - target.fighter.defense

    who_desc = f"{actor.fighter.name} attacks {target.fighter.name}"

    if damage > 0:
        target.fighter.hp -= damage
        print(f"{who_desc} for {damage} hit points.")
    else:
        print(f"{who_desc} but does no damage.")
    if target.fighter.hp <= 0:
        print(f"The {target.fighter.name} dies.")
        model.active_map.entities.remove(target)
