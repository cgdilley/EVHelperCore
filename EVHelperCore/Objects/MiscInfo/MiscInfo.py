from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable, IJsonable
from EVHelperCore.Objects.MiscInfo.EVYield import EVYield
from EVHelperCore.Objects.MiscInfo.Evolution import EvolutionLine
from EVHelperCore.Utils.DictUtils import get_or_default, from_json_or_default, trim_none
from EVHelperCore.Objects.MiscInfo.EggGroup import EggGroup
from EVHelperCore.Objects.MiscInfo.GenderRatio import GenderRatio

from typing import Optional, List


class MiscInfo(IJsonExchangeable):
    """
    Assorted information about a Pokémon that doesn't belong in any other object type.
    All properties of this class are optional.
    """

    def __init__(self, ev_yield: Optional[EVYield] = None,
                 evolution_line: Optional[EvolutionLine] = None,
                 weight: Optional[float] = None,
                 height: Optional[float] = None,
                 catch_rate: Optional[int] = None,
                 egg_groups: Optional[List[EggGroup]] = None,
                 gender_ratio: Optional[GenderRatio] = None):
        self.ev_yield = ev_yield
        self.evolution_line = evolution_line
        self.weight = weight
        self.height = height
        self.catch_rate = catch_rate
        self.egg_groups = egg_groups
        self.gender_ratio = gender_ratio

    @classmethod
    def from_json(cls, obj: dict) -> MiscInfo:
        return MiscInfo(ev_yield=from_json_or_default(EVYield, obj, "ev_yield", None),
                        evolution_line=from_json_or_default(EvolutionLine, obj, "evolution_line", None),
                        weight=get_or_default(obj, "weight", None),
                        height=get_or_default(obj, "height", None),
                        catch_rate=get_or_default(obj, "catch_rate", None),
                        egg_groups=None if "egg_groups" not in obj else [EggGroup[x] for x in obj["egg_groups"]],
                        gender_ratio=from_json_or_default(GenderRatio, obj, "gender_ratio", None))

    def to_json(self) -> dict:
        return trim_none({"ev_yield": IJsonable.to_json_or_default(self.ev_yield),
                          "evolution_line": IJsonable.to_json_or_default(self.evolution_line),
                          "weight": self.weight,
                          "height": self.height,
                          "gender_ratio": IJsonable.to_json_or_default(self.gender_ratio),
                          "catch_rate": self.catch_rate,
                          "egg_groups": [x.name for x in self.egg_groups] if self.egg_groups else None})
