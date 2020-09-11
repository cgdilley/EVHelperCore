from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable
from EVHelperCore.Objects.Stats import Stat, NUMBER_STATS
from EVHelperCore.Exceptions import StatError

from typing import Iterable, Tuple, Dict


class EVYield(IJsonExchangeable):
    """
    Represents information about the number and type of EVs granted when a Pokémon is defeated.
    """

    def __init__(self, *yields: Tuple[Stat, int]):
        if any(stat not in NUMBER_STATS or not (1 <= value <= 3) for stat, value in yields):
            raise StatError("Invalid EV yield: %s" % ", ".join("%s=%s" % (stat, value)
                                                               for stat, value in yields))
        self.yields: Dict[Stat, int] = {
            stat: val
            for stat, val in yields
        }

    @classmethod
    def from_json(cls, obj: dict) -> EVYield:
        return EVYield(*((Stat(stat), val) for stat, val in obj.items()))

    def to_json(self) -> dict:
        return {stat.name: val for stat, val in self.yields.items()}
