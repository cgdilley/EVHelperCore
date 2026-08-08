from __future__ import annotations

from enum import IntFlag, Enum
from abc import ABC

from SprelfJSON import JSONModel
from .Type import Type


#


class MoveProperties(IntFlag):
    NONE = 0
    CONTACT = 2 ** 0
    SOUND = 2 ** 1
    SLASHING = 2 ** 2
    PUNCHING = 2 ** 3
    BITING = 2 ** 4
    BULLET = 2 ** 5
    WIND = 2 ** 6
    POWDER = 2 ** 7
    ABSORBING = 2 ** 8
    PULSING = 2 ** 9
    MULTI_TARGET = 2 ** 10
    HAS_SECONDARIES = 2 ** 11
    RECOIL = 2 ** 12
    CRASHING = 2 ** 13
    IGNORES_BOOSTS = 2 ** 14


class DamageClass(Enum):
    PHYSICAL = 1
    SPECIAL = 2


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
    priority: int = 0




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
