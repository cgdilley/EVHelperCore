from __future__ import annotations

from SprelfPkmn.Objects.MiscInfo.EVYield import EVYield
from SprelfPkmn.Objects.MiscInfo.Evolution import EvolutionLine
from SprelfPkmn.Objects.MiscInfo.EggGroup import EggGroup
from SprelfPkmn.Objects.MiscInfo.GenderRatio import GenderRatio

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
