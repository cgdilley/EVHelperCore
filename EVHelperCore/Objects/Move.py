from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable
from EVHelperCore.Objects.Type import Type
from EVHelperCore.Objects.Stats import Stat


class Move(IJsonExchangeable):
    """
    Describes a single move learnable by a Pokémon
    """

    @classmethod
    def from_json(cls, obj: dict) -> Move:
        return Move()

    def to_json(self) -> dict:
        return {}


class DamagingMove(Move):

    def __init__(self, name: str, typ: Type, base_power: int, offense_stat: Stat, defense_stat: Stat):
        self.name = name
        self.type = typ
        self.base_power = base_power
        self.offense_stat = offense_stat
        self.defense_stat = defense_stat


class MoveList(IJsonExchangeable):
    """
    Describes a collection of moves that are learnable by a Pokémon
    """

    @classmethod
    def from_json(cls, obj: dict) -> MoveList:
        return MoveList()

    def to_json(self) -> dict:
        return {}


class MoveSet(IJsonExchangeable):
    """
    Describes the set of 4 moves that a single Pokémon knows
    """

    @classmethod
    def from_json(cls, obj: dict) -> MoveSet:
        return MoveSet()

    def to_json(self) -> dict:
        return {}
