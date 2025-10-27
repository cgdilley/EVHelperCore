from __future__ import annotations

from EVHelperCore.Objects.MiscInfo.EVYield import EVYield
from EVHelperCore.Objects.MiscInfo.Evolution import EvolutionLine
from EVHelperCore.Objects.MiscInfo.EggGroup import EggGroup
from EVHelperCore.Objects.MiscInfo.GenderRatio import GenderRatio

from SprelfJSON import JSONModel


class MiscInfo(JSONModel):
    """
    Assorted information about a Pokémon that doesn't belong in any other object type.
    All properties of this class are optional.
    """
    ev_yield: EVYield | None = None
    evolution_line: EvolutionLine | None = None
    weight: float | None = None
    height: float | None = None
    catch_rate: int | None = None
    egg_groups: list[EggGroup] | None = None
    gender_ratio: GenderRatio | None = None
