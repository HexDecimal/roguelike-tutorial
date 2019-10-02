from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    import entity


def move_to(actor: entity.Entity, xy_destination: Tuple[int, int]) -> None:
    """Move an entity to a position, interacting with obstacles."""
    assert actor.location
    map_ = actor.location.map
    target = map_.fighter_at(*xy_destination)
    if not map_.is_blocked(*xy_destination):
        actor.location = map_[xy_destination]
        map_.update_fov()
    elif target:
        return attack(actor, target)


def move(actor: entity.Entity, xy_direction: Tuple[int, int]) -> None:
    """Move an entity in a direction, interaction with obstacles."""
    assert actor.location
    move_to(actor, actor.location.relative(*xy_direction))


def move_towards(actor: entity.Entity, destination: Tuple[int, int]) -> None:
    """Move towards and possibly interact with destination."""
    assert actor.location
    dx = destination[0] - actor.location.x
    dy = destination[1] - actor.location.y
    distance = max(abs(dx), abs(dy))
    dx = int(round(dx / distance))
    dy = int(round(dy / distance))
    return move(actor, (dx, dy))


def attack(actor: entity.Entity, target: entity.Entity) -> None:
    """Make this entities Fighter attack another entity."""
    assert actor.location
    assert target.location
    assert actor.fighter
    assert target.fighter
    model = actor.location.map.model
    assert actor.location.distance_to(target.location) <= 1
    damage = actor.fighter.power - target.fighter.defense

    who_desc = f"{actor.fighter.name} attacks {target.fighter.name}"

    if damage > 0:
        target.fighter.hp -= damage
        model.report(f"{who_desc} for {damage} hit points.")
    else:
        model.report(f"{who_desc} but does no damage.")
    if target.fighter.hp <= 0:
        if target == actor.location.map.player:
            model.report(f"You die.")
        else:
            model.report(f"The {target.fighter.name} dies.")
        target.ai = None
        assert target.graphic
        target.graphic.char = ord("%")
        target.graphic.color = (127, 0, 0)
        target.graphic.render_order = 0


def attack_player(actor: entity.Entity) -> None:
    """Move towards and attack the player."""
    assert actor.location
    assert actor.location.map.player.location
    return move_towards(actor, actor.location.map.player.location.xy)


def pickup(actor: entity.Entity) -> None:
    assert actor.location
    assert actor.fighter
    assert actor.inventory
    model = actor.location.map.model
    for obj in actor.location.map.entities_at(*actor.location.xy):
        if obj.item:
            model.report(f"{actor.fighter.name} pick up the {obj.item.name}.")
            actor.inventory.take(obj)
            return
    model.report("There is nothing to pick up.")
