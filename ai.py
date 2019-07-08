from __future__ import annotations

from typing import TYPE_CHECKING

import action

if TYPE_CHECKING:
    import entity
    import model


class AI:
    def take_turn(self, model: model.Model, owner: entity.Entity) -> None:
        raise NotImplementedError()


class BasicMonster(AI):
    def take_turn(self, model: model.Model, owner: entity.Entity) -> None:
        action.attack_player(model, owner)
