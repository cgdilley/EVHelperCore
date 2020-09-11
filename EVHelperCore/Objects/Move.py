from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable


class Move(IJsonExchangeable):
    """
    Describes a single move learnable by a Pokémon
    """

    @classmethod
    def from_json(cls, obj: dict) -> Move:
        return Move()

    def to_json(self) -> dict:
        return {}


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

