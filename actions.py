from __future__ import annotations

from action import Action, ActionWithPosition, ActionWithDirection


class MoveTo(ActionWithPosition):
    """Move an entity to a position, interacting with obstacles."""

    def act(self) -> None:
        if not self.map.is_blocked(*self.target_pos):
            self.actor.location = self.map[self.target_pos]
            if self.is_player():
                self.map.update_fov()
        elif self.map.fighter_at(*self.target_pos):
            return Attack(self.actor, self.target_pos).act()


class Move(ActionWithDirection):
    """Move an entity in a direction, interaction with obstacles."""

    def act(self) -> None:
        return MoveTo(self.actor, self.target_pos).act()


class MoveTowards(ActionWithPosition):
    """Move towards and possibly interact with destination."""

    def act(self) -> None:
        dx = self.target_pos[0] - self.location.x
        dy = self.target_pos[1] - self.location.y
        distance = max(abs(dx), abs(dy))
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        return Move(self.actor, (dx, dy)).act()


class Attack(ActionWithPosition):
    """Make this entities Fighter attack another entity."""

    def act(self) -> None:
        assert self.location.distance_to(*self.target_pos) <= 1
        target = self.map.fighter_at(*self.target_pos)
        assert target
        assert self.actor.fighter
        assert target.fighter

        damage = self.actor.fighter.power - target.fighter.defense

        if self.is_player():
            who_desc = f"You attack the {target.fighter.name}"
        else:
            who_desc = f"{self.actor.fighter.name} attacks {target.fighter.name}"

        if damage > 0:
            target.fighter.hp -= damage
            self.report(f"{who_desc} for {damage} hit points.")
        else:
            self.report(f"{who_desc} but does no damage.")
        if target.fighter.hp <= 0:
            if target == self.map.player:
                self.report(f"You die.")
            else:
                self.report(f"The {target.fighter.name} dies.")
            target.ai = None
            assert target.graphic
            target.graphic.char = ord("%")
            target.graphic.color = (127, 0, 0)
            target.graphic.render_order = 2


class AttackPlayer(Action):
    """Move towards and attack the player."""

    def act(self) -> None:
        assert self.map.player.location
        return MoveTowards(self.actor, self.map.player.location.xy).act()


class Pickup(Action):
    def act(self) -> None:
        assert self.actor.fighter
        assert self.actor.inventory
        for obj in self.map.entities_at(*self.location.xy):
            if obj.item:
                self.report(f"{self.actor.fighter.name} pick up the {obj.item.name}.")
                self.actor.inventory.take(obj)
                return
        self.report("There is nothing to pick up.")
