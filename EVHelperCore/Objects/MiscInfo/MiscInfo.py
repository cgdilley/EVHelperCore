from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable, IJsonable
from EVHelperCore.Objects.MiscInfo.EVYield import EVYield
from EVHelperCore.Objects.MiscInfo.Evolution import EvolutionLine
from EVHelperCore.Utils.DictUtils import get_or_default, from_json_or_default, trim_none

from typing import Optional


class MiscInfo(IJsonExchangeable):
    """
    Assorted information about a Pokémon that doesn't belong in any other object type.
    All properties of this class are optional.
    """

    def __init__(self, ev_yield: Optional[EVYield] = None,
                 evolution_line: Optional[EvolutionLine] = None,
                 weight: Optional[float] = None):
        self.ev_yield = ev_yield
        self.evolution_line = evolution_line
        self.weight = weight

    @classmethod
    def from_json(cls, obj: dict) -> MiscInfo:
        return MiscInfo(ev_yield=from_json_or_default(EVYield, obj, "ev_yield", None),
                        evolution_line=from_json_or_default(EvolutionLine, obj, "evolution_line", None),
                        weight=get_or_default(obj, "weight", None))

    def to_json(self) -> dict:
        return trim_none({"ev_yield": IJsonable.to_json_or_default(self.ev_yield),
                          "evolution_line": IJsonable.to_json_or_default(self.evolution_line),
                          "weight": self.weight})
