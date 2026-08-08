from __future__ import annotations

from SprelfJSON import JSONModel
from .PokemonData import Pokemon
from .Stats import StatModifier, Stat
from .BoardState import Entity
from SprelfPkmn.Calculations.Stats import get_stat_value_from_info

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
    name: str
    hidden: bool = False


class MoveLimitingVolatile(VolatileStatusCondition):
    move_name: str


class UntilNextActionVolatile(VolatileStatusCondition):
    ...


class TemporaryVolatile(VolatileStatusCondition):
    duration: int
    turn_counter: int = 0


class MoveLimitingTemporaryVolatile(TemporaryVolatile, MoveLimitingVolatile):
    ...


# EXAMPLES:
# taunt = TemporaryVolatile(name="Taunt", duration=3)
# encore = MoveLimitingTemporaryVolatile(name="Encore", duration=3, move_name="Dragon Dance")
# choice_lock = MoveLimitingVolatile(name="Choice Locked", move_name="Last Respects", hidden=True)
# destiny_bond = UntilNextActionVolatile(name="Destiny Bond")
# last_move_failed = UntilNextActionVolatile(name="Last Move Failed", hidden=True) # For Stomping Tantrum


#


#


class PokemonState(Pokemon, Entity):
    hp: int
    status: StatusCondition = StatusCondition.NONE
    volatiles: list[VolatileStatusCondition] = []

    @classmethod
    def fresh(cls, pokemon: Pokemon, team: int, slot: int) -> PokemonState:
        hp = get_stat_value_from_info(pokemon.stats, Stat.HP)
        return PokemonState(
            data=pokemon.data,
            typing=pokemon.typing,
            ability=pokemon.ability,
            moveset=pokemon.moveset,
            stats=pokemon.stats,
            item=pokemon.item,
            team=team,
            slot=slot,
            hp=hp,
            status=StatusCondition.NONE,
            volatiles=[])

    @property
    def modifiers(self) -> dict[Stat, int]:
        return self.stats.modifiers

    def add_modifiers(self, *stat_mods: StatModifier):
        self.stats.add_modifiers(*stat_mods)
