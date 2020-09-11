from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable
from EVHelperCore.Objects.Stats import Stat, Nature, NUMBER_STATS, check_number_stat
from EVHelperCore.Exceptions import StatError

from typing import Optional, Union, Iterable, List


class StatTemplate(IJsonExchangeable):
    """
    A collection of restrictions on stat information options (EV, IV, level, nature, base stat), used as a filter
    when calculating all the possible combinations of these that leads to a particular stat value.
    For example, if you wanted to calculate what the base Speed stat of a Pokémon with a certain numerical Speed stat,
    assuming that Pokémon has maximum EVs and a boosting nature (and at a particular level),
    you can create a StatTemplate that includes those restrictions and come up with the result you want when passing
    that StatTemplate to the relevant calculation functions.
    """

    def __init__(self,
                 stat: Stat,
                 base: Optional[Union[int, Iterable[int]]] = None,
                 ev: Optional[Union[int, Iterable[int]]] = None,
                 iv: Optional[Union[int, Iterable[int]]] = None,
                 level: Optional[Union[int, Iterable[int]]] = None,
                 nature: Optional[Union[Nature, Iterable[Nature]]] = None):
        """
        :param stat: The stat to create the stat template for
        :param base: The base stat value for the specified stat
        :param ev: The EVs invested into the specified stat
        :param iv: The IVs for the specified stat
        :param level: The level of the Pokémon
        :param nature: The stat-modifying nature of the Pokémon
        """
        check_number_stat(stat)

        def _standardize(val, expected_type: type):
            if val is None:
                return None
            if type(val) == expected_type:
                return [val]
            if len(val) == 0:
                return None
            return sorted(list(val)) if hasattr(expected_type, "__cmp__") else list(val)

        self.stat = stat
        self.base: List[int] = _standardize(base, int)
        self.ev: List[int] = _standardize(ev, int)
        self.iv: List[int] = _standardize(iv, int)
        self.level: List[int] = _standardize(level, int)
        self.nature: List[Nature] = _standardize(nature, Nature)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, StatTemplate) and \
               self.stat == o.stat and \
               self.base == o.base and \
               self.ev == o.ev and \
               self.iv == o.ev and \
               self.level == o.level and \
               self.nature == o.nature

    def __hash__(self) -> int:
        return hash((self.stat, frozenset(self.base), frozenset(self.ev), frozenset(self.iv),
                     frozenset(self.level), frozenset(self.nature)))

    def __str__(self) -> str:
        return " | ".join("%s = %s" % (k, v) for k, v in
                          (("stat", self.stat),
                           ("base", ", ".join(str(b) for b in self.base)),
                           ("ev", ", ".join(str(e) for e in self.ev)),
                           ("iv", ", ".join(str(i) for i in self.iv)),
                           ("level", ", ".join(str(level) for level in self.level)),
                           ("nature", ", ".join(n.get_mod_as_string(self.stat) for n in self.nature)))
                          if v is not None)

    def __repr__(self) -> str:
        return super().__repr__()

    def is_complete(self) -> bool:
        """
        A stat template is considered complete when it has exactly one option for every stat information type
        (EVs, IVs, etc.), and thus represents exactly one combination.
        """
        return all(len(x) == 1 for x in (self.base, self.ev, self.iv, self.level, self.nature))

    @classmethod
    def from_json(cls, obj: dict) -> IJsonExchangeable:
        return StatTemplate(stat=Stat(obj["stat"]),
                            ev=obj["ev"] if "ev" in obj else None,
                            iv=obj["iv"] if "iv" in obj else None,
                            base=obj["base"] if "base" in obj else None,
                            level=obj["level"] if "level" in obj else None,
                            nature=[Nature.from_json(n) for n in obj["nature"]] if "nature" in obj else None)

    def to_json(self) -> dict:
        return {
            k: v for k, v in (("stat", self.stat.name),
                              ("base", self.base),
                              ("ev", self.ev),
                              ("iv", self.iv),
                              ("level", self.level),
                              ("nature", [n.to_json() for n in self.nature] if self.nature else None))
            if v is not None
        }
