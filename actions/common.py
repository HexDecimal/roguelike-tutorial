from __future__ import annotations

from actions import (
    Action,
    ActionWithDirection,
    ActionWithItem,
    ActionWithPosition,
    Impossible,
)


class MoveTo(ActionWithPosition):
    """Move an entity to a position, interacting with obstacles."""

    def plan(self) -> Action:
        if self.actor.location.distance_to(*self.target_pos) > 1:
            # Enforces that the actor is only moving a short distance.
            raise Impossible(
                "Can't move from %s to %s." % (self.actor.location.xy, self.target_pos)
            )
        if self.actor.location.xy == self.target_pos:
            return self
        if self.map.fighter_at(*self.target_pos):
            return Attack(self.actor, self.target_pos).plan()
        if self.map.is_blocked(*self.target_pos):
            raise Impossible("That way is blocked.")
        return self

    def act(self) -> None:
        self.actor.location = self.map[self.target_pos]
        if self.actor.is_player():
            self.map.update_fov()
        self.actor.reschedule(100)


class Move(ActionWithDirection):
    """Move an entity in a direction, interaction with obstacles."""

    def plan(self) -> Action:
        return MoveTo(self.actor, self.target_pos).plan()


class MoveTowards(ActionWithPosition):
    """Move towards and possibly interact with destination."""

    def plan(self) -> Action:
        dx = self.target_pos[0] - self.location.x
        dy = self.target_pos[1] - self.location.y
        distance = max(abs(dx), abs(dy))
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        return Move(self.actor, (dx, dy)).plan()


class Attack(ActionWithPosition):
    """Make this entities Fighter attack another entity."""

    def plan(self) -> Attack:
        if self.location.distance_to(*self.target_pos) > 1:
            raise Impossible("That space is too far away to attack.")
        return self

    def act(self) -> None:
        target = self.map.fighter_at(*self.target_pos)
        assert target

        damage = self.actor.fighter.power - target.fighter.defense

        if self.actor.is_player():
            who_desc = f"You attack the {target.fighter.name}"
        else:
            who_desc = f"{self.actor.fighter.name} attacks {target.fighter.name}"

        if damage > 0:
            self.report(f"{who_desc} for {damage} hit points.")
            target.damage(damage)
        else:
            self.report(f"{who_desc} but does no damage.")
        self.actor.reschedule(100)


class AttackPlayer(Action):
    """Move towards and attack the player."""

    def plan(self) -> Action:
        return MoveTowards(self.actor, self.map.player.location.xy).plan()


class Pickup(Action):
    def plan(self) -> Action:
        if not self.map.items.get(self.location.xy):
            raise Impossible("There is nothing to pick up.")
        return self

    def act(self) -> None:
        for item in self.map.items[self.location.xy]:
            self.report(f"{self.actor.fighter.name} pick up the {item.name}.")
            self.actor.inventory.take(item)
            return self.actor.reschedule(100)


class ActivateItem(ActionWithItem):
    def plan(self) -> ActionWithItem:
        assert self.item in self.actor.inventory.contents
        return self.item.plan_activate(self)

    def act(self) -> None:
        assert self.item in self.actor.inventory.contents
        self.item.action_activate(self)
        self.actor.reschedule(100)


class DropItem(ActionWithItem):
    def act(self) -> None:
        assert self.item in self.actor.inventory.contents
        self.item.lift()
        self.item.place(self.actor.location)
        self.report(f"You drop the {self.item.name}.")
        self.actor.reschedule(100)


class DrinkItem(ActionWithItem):
    def act(self) -> None:
        assert self.item in self.actor.inventory.contents
        self.item.action_drink(self)
        self.actor.reschedule(100)


class EatItem(ActionWithItem):
    def act(self) -> None:
        assert self.item in self.actor.inventory.contents
        self.item.action_eat(self)
        self.actor.reschedule(100)
