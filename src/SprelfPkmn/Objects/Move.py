from __future__ import annotations

from enum import IntFlag, Enum
from abc import ABC
from typing import Iterator

from SprelfJSON import JSONModel
from .Type import Type, Typing


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

    def __iter__(self):
        return (flag for flag in type(self) if self & flag)


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
    _modified_typing: Typing | None = None

    @property
    def modified_typing(self) -> Typing:
        if self._modified_typing is not None:
            return self._modified_typing
        return Typing(primary=self.type)

    @modified_typing.setter
    def modified_typing(self, value: Typing):
        self._modified_typing = value


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

    def __iter__(self) -> Iterator[Move]:
        return iter(self.moves)

    def __len__(self) -> int:
        return len(self.moves)
