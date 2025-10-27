from __future__ import annotations

from SprelfPkmn.Objects.Type import Type
from SprelfPkmn.Objects.Stats import Stat

from enum import IntFlag
from abc import ABC

from SprelfJSON import JSONModel


#


class MoveProperties(IntFlag):
    NONE = 0
    CONTACT = 1
    SOUND = 2
    SLASHING = 4
    PUNCHING = 8
    BITING = 16
    BULLET = 32
    WIND = 64
    POWDER = 128
    ABSORBING = 256


class Move(JSONModel, ABC):
    """
    Describes a single move learnable by a Pokémon
    """
    name: str
    type: Type
    properties: MoveProperties = MoveProperties.NONE
    __name_field__ = "category"
    __name_field_required__ = True
    accuracy: int | None = 100
    max_pp: int | None = None
    description: str = ""


class DamagingMove(Move):
    base_power: int
    offense_stat: Stat
    defense_stat: Stat

    def __init__(self, name: str, type: Type, base_power: int, offense_stat: Stat,
                 defense_stat: Stat | None = None,
                 accuracy: int | None = None,  description: str = "", max_pp: int | None = None,
                 properties: MoveProperties = MoveProperties.NONE):
        if defense_stat is None:
            defense_stat = Stat.DEFENSE if offense_stat == Stat.ATTACK else Stat.SP_DEFENSE
        super().__init__(name=name, type=type, base_power=base_power, offense_stat=offense_stat,
                         defense_stat=defense_stat, accuracy=accuracy, description=description,
                         max_pp=max_pp, properties=properties)

    def __str__(self) -> str:
        return f"[{type(self).__name__}] {self.name} : {self.type.name.capitalize()} ({self.base_power})"


class StatusMove(Move):

    def __str__(self) -> str:
        return f"[{type(self).__name__}] {self.name} : {self.type.name.capitalize()}"


class MoveList(JSONModel):
    """
    Describes a collection of moves that are learnable by a Pokémon
    """
    moves: list[Move] = []


class MoveSet(JSONModel):
    """
    Describes the set of 4 moves that a single Pokémon knows
    """
    moves: list[Move] = []

