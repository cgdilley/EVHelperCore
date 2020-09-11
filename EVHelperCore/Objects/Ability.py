from __future__ import annotations


from EVHelperCore.Interfaces import IJsonExchangeable

from typing import Optional, Iterable, Iterator, Tuple


class Ability(IJsonExchangeable):
    """
    Represents a single passive ability that a Pokémon may have.
    """

    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other: Ability) -> bool:
        return other.name == self.name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def from_json(cls, obj: dict) -> Ability:
        return Ability(name=obj["name"])

    def to_json(self) -> dict:
        return {"name": self.name}


#


class AbilityList(Iterable[Ability], IJsonExchangeable):
    """
    Represents the collection of primary, secondary, and hidden abilities available to a particular
    species of Pokémon.
    """

    def __init__(self, primary_ability: Ability,
                 secondary_ability: Optional[Ability] = None,
                 hidden_ability: Optional[Ability] = None):
        self.primary = primary_ability
        self.secondary = secondary_ability
        self.hidden = hidden_ability

    def __str__(self) -> str:
        return ", ".join(a for a in [
            "1. " + str(self.primary) if self.primary else None,
            "2. " + str(self.secondary) if self.secondary else None,
            "Hidden: " + str(self.hidden) if self.hidden else None
        ] if a)

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> Iterator[Ability]:
        return iter(a for a in self.as_tuple() if a)

    def as_tuple(self) -> Tuple[Optional[Ability], Optional[Ability], Optional[Ability]]:
        return self.primary, self.secondary, self.hidden

    @classmethod
    def from_json(cls, obj: dict) -> AbilityList:
        return AbilityList(primary_ability=Ability.from_json(obj["primary"]),
                           secondary_ability=Ability.from_json(obj["secondary"]) if "secondary" in obj else None,
                           hidden_ability=Ability.from_json(obj["hidden"]) if "hidden" in obj else None)

    def to_json(self) -> dict:
        return {
            k: v for k, v in (("primary", self.primary.to_json()),
                              ("secondary", self.secondary.to_json() if self.secondary else None),
                              ("hidden", self.hidden.to_json() if self.hidden else None))
            if v
        }



