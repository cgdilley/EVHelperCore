from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable


class Move(IJsonExchangeable):

    @classmethod
    def from_json(cls, obj: dict) -> Move:
        return Move()

    def to_json(self) -> dict:
        return {}


class MoveList(IJsonExchangeable):

    @classmethod
    def from_json(cls, obj: dict) -> MoveList:
        return MoveList()

    def to_json(self) -> dict:
        return {}
