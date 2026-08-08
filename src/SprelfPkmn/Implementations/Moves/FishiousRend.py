from __future__ import annotations

from typing import Iterable

from SprelfPkmn.Objects import *
from .DamagingMove import DamagingMove

#


class Move_FishiousRend(DamagingMove):
    name: str = "Fishious Rend"
    type: Type = Type.WATER
    properties: MoveProperties = MoveProperties.BITING | MoveProperties.CONTACT
    accuracy: int | None = 100
    max_pp: int | None = None
    description: str = ""
    priority: int = 0
    base_power: int = 85
    damage_class: DamageClass = DamageClass.PHYSICAL
    offense_stat: Stat = Stat.ATTACK
    defense_stat: Stat = Stat.DEFENSE

    def get_base_power_modifiers(self, attacker: Pokemon,
                                 defender: Pokemon,
                                 board_state: BoardState) -> Iterable[BasePowerCondition]:
        yield from super().get_base_power_modifiers(attacker, defender, board_state)
        yield MoveBasePowerCondition(move_name=self.name, multiplier=2, innate=True)
