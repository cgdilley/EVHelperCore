from __future__ import annotations

from typing import Iterable

from SprelfPkmn.Objects.Move import DamagingMove, MoveProperties, DamageType
from SprelfPkmn.Objects.Type import Type
from SprelfPkmn.Objects.Stats import Stat
from SprelfPkmn.Objects.CalculationCondition import MoveBasePowerCondition, BasePowerCondition
from SprelfPkmn.Objects.PokemonData import Pokemon
from SprelfPkmn.Objects.BoardState import BoardState


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
    damage_type: DamageType = DamageType.PHYSICAL
    offense_stat: Stat = Stat.ATTACK
    defense_stat: Stat = Stat.DEFENSE

    def __init__(self):
        super().__init__(name=self.name, type=self.type, base_power=self.base_power, offense_stat=self.offense_stat,
                         defense_stat=self.defense_stat, damage_type=self.damage_type,
                         properties=self.properties)

    def get_base_power_modifiers(self, attacker: Pokemon,
                                 defender: Pokemon,
                                 board_state: BoardState) -> Iterable[BasePowerCondition]:
        yield from super().get_base_power_modifiers(attacker, defender, board_state)
        yield MoveBasePowerCondition(move_name=self.name, multiplier=2, innate=True)
