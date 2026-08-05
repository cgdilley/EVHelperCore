from __future__ import annotations

from SprelfJSON import AbstractJSONModel, JSONModel
from .Ability import Ability
from .Item import Item
from .BoardState import Weather, Terrain, BoardEffect, BoardEffectType, BoardState
from .Stats import Stat
from .Type import Type

from abc import ABC


# +

class CalculationCondition(AbstractJSONModel, ABC):
    ...


class DamageCondition(CalculationCondition, ABC):
    multiplier: float
    for_attacker: bool = True


class STABCondition(CalculationCondition, ABC):
    source: str
    multiplier: float


class StatCondition(CalculationCondition, ABC):
    for_attacker: bool
    stat: Stat
    multiplier: float


class BasePowerCondition(CalculationCondition, ABC):
    multiplier: float
    innate: bool = False


class AbilityCondition(CalculationCondition, ABC):
    ability: Ability


class ItemCondition(CalculationCondition, ABC):
    item: Item


class BoardEffectCondition(CalculationCondition, ABC):
    effect: BoardEffectType
    for_attacker: bool


class AbilityBasePowerCondition(BasePowerCondition, AbilityCondition):
    ...


class TerrainBasePowerCondition(BasePowerCondition):
    terrain: Terrain


class BoardEffectBasePowerCondition(BasePowerCondition, BoardEffectCondition):
    effect: BoardEffectType
    for_attacker: bool = True


class ItemBasePowerCondition(BasePowerCondition, ItemCondition):
    ...


class MoveBasePowerCondition(BasePowerCondition):
    move_name: str


class ItemStatCondition(StatCondition, ItemCondition):
    ...


class ItemDamageCondition(DamageCondition, ItemCondition):
    ...


class TypeChangeCondition(CalculationCondition):
    source: str
    new_type: Type


class WeatherCondition(CalculationCondition, ABC):
    weather: Weather


class WeatherDamageCondition(DamageCondition, WeatherCondition):
    ...


class WeatherStatCondition(StatCondition, WeatherCondition):
    ...

class BoardEffectDamageCondition(DamageCondition, BoardEffectCondition):
    ...


class ScreensDamageCondition(BoardEffectDamageCondition):
    ...


class AbilityDamageCondition(DamageCondition, AbilityCondition):
    ...


class AbilityStatCondition(StatCondition, AbilityCondition):
    ...
