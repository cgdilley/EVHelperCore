from __future__ import annotations

from EVHelperCore.Objects.Stats import Stat, NUMBER_STATS, StatError

from SprelfJSON import JSONConvertible, JSONObject

class EVYield(JSONConvertible):
    """
    Represents information about the number and type of EVs granted when a Pokémon is defeated.
    """

    def __init__(self, *yields: tuple[Stat, int]):
        if any(stat not in NUMBER_STATS or not (1 <= value <= 3) for stat, value in yields):
            raise StatError("Invalid EV yield: %s" % ", ".join("%s=%s" % (stat, value)
                                                               for stat, value in yields))
        self.yields: dict[Stat, int] = {
            stat: val
            for stat, val in yields
        }

    def __str__(self) -> str:
        return ", ".join(f"{stat.name}={val}" for stat, val in self.yields.items())

    def __getitem__(self, stat: Stat) -> int:
        return self.yields[stat]

    def get(self, stat: Stat, default: int = 0) -> int:
        return self.yields.get(stat, default)

    @classmethod
    def from_json(cls, obj: JSONObject, **kwargs) -> EVYield:
        return EVYield(*((Stat(stat), val) for stat, val in obj.items()))

    def to_json(self) -> JSONObject:
        return {stat.name: val for stat, val in self.yields.items()}
