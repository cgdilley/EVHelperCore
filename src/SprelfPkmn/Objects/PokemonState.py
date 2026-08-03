from __future__ import annotations

from SprelfJSON import JSONModel
from .PokemonData import Pokemon
from .Stats import StatModifier, Stat

from enum import Enum


class StatusCondition(Enum):
    NONE = 0
    BURNED = 1
    ASLEEP = 2
    PARALYZED = 3
    POISONED = 4
    BADLY_POISONED = 5
    FROZEN = 6
    POKERUS = 10


class VolatileStatusCondition(JSONModel):
    ...

class TurnLimitedVolatileStatusCondition(VolatileStatusCondition):
    duration: int
    turns_burned: int


class Confusion(TurnLimitedVolatileStatusCondition):
    ...


class Taunt(TurnLimitedVolatileStatusCondition):
    ...


class Encore(TurnLimitedVolatileStatusCondition):
    duration: int = 3


#


#


class PokemonState(JSONModel):
    pokemon: Pokemon
    hp: int
    status: StatusCondition = StatusCondition.NONE
    volatiles: list[VolatileStatusCondition] = []

    @property
    def modifiers(self) -> dict[Stat, int]:
        return self.pokemon.stats.modifiers

    def add_modifiers(self, *stat_mods: StatModifier):
        self.pokemon.stats.add_modifiers(*stat_mods)