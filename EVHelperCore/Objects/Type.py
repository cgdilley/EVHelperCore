from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable

from typing import Optional, Iterable, Tuple, Iterator, Union, Dict, NamedTuple
from enum import Enum


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
    def get_damage_multiplier(cls, attacking: Union[Type, Typing], defending: Typing) -> float:
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
    super: Tuple[Type, ...]
    not_very: Tuple[Type, ...]
    immune: Tuple[Type, ...]


ATTACK_EFFECTIVENESS: Dict[Type, TypeEffectivenessRecord] = {
    Type.NORMAL: TypeEffectivenessRecord((),(Type.ROCK, Type.STEEL), (Type.GHOST,)),
    Type.FIGHTING: TypeEffectivenessRecord((Type.NORMAL, Type.ROCK, Type.STEEL, Type.DARK, Type. ICE),
                                     (Type.FLYING, Type.POISON, Type.BUG, Type.PSYCHIC, Type.FAIRY), (Type.GHOST,)),
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
DEFENSE_EFFECTIVENESS: Dict[Type, TypeEffectivenessRecord] = {
    d_type: TypeEffectivenessRecord(tuple(a_type for a_type, ter in ATTACK_EFFECTIVENESS.items()
                                          if d_type in ter.super),
                                    tuple(a_type for a_type, ter in ATTACK_EFFECTIVENESS.items()
                                          if d_type in ter.not_very),
                                    tuple(a_type for a_type, ter in ATTACK_EFFECTIVENESS.items()
                                          if d_type in ter.immune))
    for d_type in Type
}


#


class Typing(IJsonExchangeable, Iterable[Type]):
    """
    Describes the typing of a particular Pokémon, including its primary and secondary typing and any other extra
    typing it may have gained (eg. through Trick-or-Treat).
    """

    def __init__(self, primary: Type,
                 secondary: Optional[Type] = None,
                 extra: Optional[Iterable[Type]] = None):
        self.primary = primary
        self.secondary = secondary
        self.extra = extra if extra is not None else []

    def __str__(self) -> str:
        return " / ".join(str(t) for t in ([self.primary, self.secondary] + self.extra) if t)

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> Iterator[Type]:
        return iter(t for t in self.as_tuple() if t)

    def has_type(self, t: Type) -> bool:
        return self.primary == t or self.secondary == t or t in self.extra

    def as_tuple(self) -> Tuple[Type, ...]:
        return (self.primary,) + ((self.secondary,) if self.secondary else ()) + tuple(self.extra)

    def is_mono_type(self):
        return self.secondary is None

    def is_dual_type(self):
        return self.secondary is not None

    @classmethod
    def from_json(cls, obj: dict) -> Typing:
        return Typing(primary=Type(obj["primary"]),
                      secondary=Type(obj["secondary"]) if "secondary" in obj else None,
                      extra=[Type(e) for e in obj["extra"]] if "extra" in obj else None)

    def to_json(self) -> dict:
        return {
            k: v for k, v in {
                "primary": self.primary.name,
                "secondary": self.secondary.name if self.secondary else None,
                "extra": [e.name for e in self.extra] if len(self.extra) > 0 else None
            }.items() if v
        }
