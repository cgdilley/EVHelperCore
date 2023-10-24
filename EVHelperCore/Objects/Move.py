from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable
from EVHelperCore.Objects.Type import Type
from EVHelperCore.Objects.Stats import Stat

from typing import Optional
from enum import IntFlag
from abc import ABC, abstractmethod


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


class Move(IJsonExchangeable, ABC):
    """
    Describes a single move learnable by a Pokémon
    """

    def __init__(self, name: str, typ: Type, pp: int, accuracy: Optional[int], description: str,
                 properties: MoveProperties = MoveProperties.NONE):
        self.name = name
        self.type = typ
        self.max_pp = pp
        self.accuracy = accuracy
        self.description = description
        self.properties = properties

    @classmethod
    def from_json(cls, obj: dict) -> Move:
        if obj["category"] == DamagingMove.__name__:
            return DamagingMove.from_json(obj)
        elif obj["category"] == StatusMove.__name__:
            return StatusMove.from_json(obj)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "type": self.type.name,
            "pp": self.max_pp,
            "description": self.description,
            "properties": self.properties.value,
            "category": type(self).__name__,
            **({"accuracy": self.accuracy} if self.accuracy is not None else {})
        }


class DamagingMove(Move):

    def __init__(self, name: str, typ: Type, pp: int, accuracy: int, description: str,
                 base_power: int, offense_stat: Stat, defense_stat: Stat,
                 properties: MoveProperties = MoveProperties.NONE):
        super(DamagingMove, self).__init__(name, typ, pp, accuracy, description, properties)
        self.base_power = base_power
        self.offense_stat = offense_stat
        self.defense_stat = defense_stat

    def __str__(self) -> str:
        return f"[{type(self).__name__}] {self.name} : {self.type.name.capitalize()} ({self.base_power})"

    @classmethod
    def from_json(cls, obj: dict) -> DamagingMove:
        return DamagingMove(name=obj["name"],
                            typ=Type[obj["type"]],
                            pp=obj["pp"],
                            accuracy=obj.get("accuracy", None),
                            description=obj["description"],
                            base_power=obj["base_power"],
                            offense_stat=Stat[obj["offense_stat"]],
                            defense_stat=Stat[obj["defense_stat"]],
                            properties=MoveProperties(obj["properties"]))

    def to_json(self) -> dict:
        return {
            **super().to_json(),
            "base_power": self.base_power,
            "offense_stat": self.offense_stat.name,
            "defense_stat": self.defense_stat.name
        }


class StatusMove(Move):

    def __init__(self, name: str, typ: Type, pp: int, accuracy: Optional[int], description: str,
                 properties: MoveProperties = MoveProperties.NONE):
        super(StatusMove, self).__init__(name, typ, pp, accuracy, description, properties)

    def __str__(self) -> str:
        return f"[{type(self).__name__}] {self.name} : {self.type.name.capitalize()}"

    @classmethod
    def from_json(cls, obj: dict) -> StatusMove:
        return StatusMove(name=obj["name"],
                          typ=Type[obj["type"]],
                          pp=obj["pp"],
                          accuracy=obj.get("accuracy", None),
                          description=obj["description"],
                          properties=MoveProperties(obj["properties"]))


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
