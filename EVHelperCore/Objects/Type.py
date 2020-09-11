from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable

from typing import Optional, Iterable, Tuple, Iterator
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
