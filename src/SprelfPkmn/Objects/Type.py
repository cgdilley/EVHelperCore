from __future__ import annotations

from typing import Iterable, Iterator, NamedTuple
from enum import Enum

from SprelfJSON import JSONModel


class Type(Enum):
    NORMAL = "NORMAL"
    FIRE = "FIRE"
    GRASS = "GRASS"
    WATER = "WATER"
    ELECTRIC = "ELECTRIC"
    ICE = "ICE"
    FLYING = "FLYING"
    FIGHTING = "FIGHTING"
    PSYCHIC = "PSYCHIC"
    GHOST = "GHOST"
    DARK = "DARK"
    FAIRY = "FAIRY"
    POISON = "POISON"
    GROUND = "GROUND"
    ROCK = "ROCK"
    DRAGON = "DRAGON"
    STEEL = "STEEL"
    BUG = "BUG"

    @classmethod
    def get_damage_multiplier(cls, attacking: Type | Typing, defending: Typing) -> float:
        if isinstance(attacking, Type):
            attacking = [attacking]

        # Preserving integers for as long as possible before switching to floats
        value = (1, 1)
        for atk_type in attacking:
            for def_type in defending:
                if def_type in ATTACK_EFFECTIVENESS[atk_type].super:
                    value = (value[0] * 2, value[1])
                elif def_type in ATTACK_EFFECTIVENESS[atk_type].not_very:
                    value = (value[0], value[1] * 2)
                elif def_type in ATTACK_EFFECTIVENESS[atk_type].immune:
                    value = (value[0] * 0, value[1])

        return value[0] / value[1]


#

class TypeEffectivenessRecord(NamedTuple):
    super: tuple[Type, ...]
    not_very: tuple[Type, ...]
    immune: tuple[Type, ...]


ATTACK_EFFECTIVENESS: dict[Type, TypeEffectivenessRecord] = {
    Type.NORMAL: TypeEffectivenessRecord((), (Type.ROCK, Type.STEEL), (Type.GHOST,)),
    Type.FIGHTING: TypeEffectivenessRecord((Type.NORMAL, Type.ROCK, Type.STEEL, Type.DARK, Type.ICE),
                                           (Type.FLYING, Type.POISON, Type.BUG, Type.PSYCHIC, Type.FAIRY),
                                           (Type.GHOST,)),
    Type.FLYING: TypeEffectivenessRecord((Type.BUG, Type.GRASS), (Type.ROCK, Type.STEEL, Type.ELECTRIC), ()),
    Type.POISON: TypeEffectivenessRecord((Type.GRASS, Type.FAIRY),
                                         (Type.POISON, Type.GROUND, Type.ROCK, Type.GHOST), (Type.STEEL,)),
    Type.GROUND: TypeEffectivenessRecord((Type.POISON, Type.ROCK, Type.STEEL, Type.FIRE, Type.ELECTRIC),
                                         (Type.BUG, Type.GRASS), (Type.FLYING,)),
    Type.ROCK: TypeEffectivenessRecord((Type.FLYING, Type.BUG, Type.FIRE, Type.ICE),
                                       (Type.FIGHTING, Type.GROUND, Type.STEEL), ()),
    Type.BUG: TypeEffectivenessRecord((Type.GRASS, Type.PSYCHIC, Type.DARK),
                                      (Type.FIGHTING, Type.FLYING, Type.POISON, Type.GHOST, Type.STEEL,
                                       Type.FIRE, Type.FAIRY), ()),
    Type.GHOST: TypeEffectivenessRecord((Type.GHOST, Type.PSYCHIC), (Type.DARK,), (Type.NORMAL,)),
    Type.STEEL: TypeEffectivenessRecord((Type.ROCK, Type.ICE, Type.FAIRY),
                                        (Type.STEEL, Type.FIRE, Type.WATER, Type.ELECTRIC), ()),
    Type.FIRE: TypeEffectivenessRecord((Type.BUG, Type.STEEL, Type.GRASS, Type.ICE),
                                       (Type.ROCK, Type.FIRE, Type.WATER, Type.DRAGON), ()),
    Type.WATER: TypeEffectivenessRecord((Type.GROUND, Type.ROCK, Type.FIRE),
                                        (Type.WATER, Type.GRASS, Type.DRAGON), ()),
    Type.GRASS: TypeEffectivenessRecord((Type.GROUND, Type.ROCK, Type.WATER),
                                        (Type.FLYING, Type.POISON, Type.BUG, Type.STEEL, Type.FIRE,
                                         Type.GRASS, Type.DRAGON), ()),
    Type.ELECTRIC: TypeEffectivenessRecord((Type.FLYING, Type.WATER), (Type.GRASS, Type.ELECTRIC, Type.DRAGON),
                                           (Type.GROUND,)),
    Type.PSYCHIC: TypeEffectivenessRecord((Type.FIGHTING, Type.POISON), (Type.STEEL, Type.PSYCHIC), (Type.DARK,)),
    Type.ICE: TypeEffectivenessRecord((Type.FLYING, Type.GROUND, Type.GRASS, Type.DRAGON),
                                      (Type.STEEL, Type.FIRE, Type.WATER, Type.ICE), ()),
    Type.DRAGON: TypeEffectivenessRecord((Type.DRAGON,), (Type.STEEL,), (Type.FAIRY,)),
    Type.DARK: TypeEffectivenessRecord((Type.GHOST, Type.PSYCHIC), (Type.FIGHTING, Type.DARK, Type.FAIRY), ()),
    Type.FAIRY: TypeEffectivenessRecord((Type.FIGHTING, Type.DRAGON, Type.DARK),
                                        (Type.POISON, Type.STEEL, Type.FIRE), ())
}
DEFENSE_EFFECTIVENESS: dict[Type, TypeEffectivenessRecord] = {
    d_type: TypeEffectivenessRecord(tuple(a_type for a_type, ter in ATTACK_EFFECTIVENESS.items()
                                          if d_type in ter.super),
                                    tuple(a_type for a_type, ter in ATTACK_EFFECTIVENESS.items()
                                          if d_type in ter.not_very),
                                    tuple(a_type for a_type, ter in ATTACK_EFFECTIVENESS.items()
                                          if d_type in ter.immune))
    for d_type in Type
}


#


class Typing(JSONModel, Iterable[Type]):
    """
    Describes the typing of a particular Pokémon, including its primary and secondary typing and any other extra
    typing it may have gained (eg. through Trick-or-Treat).
    """
    primary: Type
    secondary: Type | None = None
    extra: list[Type] = []

    @classmethod
    def of(cls, primary: Type, secondary: Type | None = None, extra: Iterable[Type] | None = None):
        return cls(primary=primary, secondary=secondary, extra=list(extra) if extra else [])

    def __str__(self) -> str:
        return " / ".join(t.name for t in ([self.primary, self.secondary] + self.extra) if t)

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> Iterator[Type]:
        return iter(t for t in self.as_tuple() if t)

    def __contains__(self, t: Type) -> bool:
        return t in self.as_tuple()

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Typing) and self.primary == o.primary and self.secondary == o.secondary and \
            self.extra == o.extra

    def __hash__(self) -> int:
        return hash((self.primary, self.secondary, tuple(self.extra)))

    def has_type(self, t: Type) -> bool:
        return self.primary == t or self.secondary == t or t in self.extra

    def as_tuple(self) -> tuple[Type, ...]:
        return (self.primary,) + ((self.secondary,) if self.secondary else ()) + tuple(self.extra)

    def is_mono_type(self):
        return self.secondary is None

    def is_dual_type(self):
        return self.secondary is not None
