from __future__ import annotations


from SprelfJSON import JSONModel

from typing import Optional, Iterable, Iterator, Tuple


class Ability(JSONModel):
    """
    Represents a single passive ability that a Pokémon may have.
    """
    name: str

    def __eq__(self, other: Ability) -> bool:
        return isinstance(other, Ability) and other.name == self.name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)


#


class AbilityList(JSONModel, Iterable[Ability]):
    """
    Represents the collection of primary, secondary, and hidden abilities available to a particular
    species of Pokémon.
    """
    primary: Ability
    secondary: Ability | None = None
    hidden: Ability | None = None

    def __str__(self) -> str:
        return ", ".join(a for a in [
            "1. " + str(self.primary) if self.primary else None,
            "2. " + str(self.secondary) if self.secondary else None,
            "Hidden: " + str(self.hidden) if self.hidden else None
        ] if a)

    def __repr__(self) -> str:
        return str(self)

    def __contains__(self, ability: Ability | str) -> bool:
        return any(ability == x or ability == x.name for x in self)

    def __iter__(self) -> Iterator[Ability]:
        return iter(a for a in self.as_tuple() if a)

    def as_tuple(self) -> Tuple[Optional[Ability], Optional[Ability], Optional[Ability]]:
        return self.primary, self.secondary, self.hidden




