from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable
from EVHelperCore.Objects.Stats import Stat, Nature, NUMBER_STATS
from EVHelperCore.Exceptions import StatError

from typing import Optional, Union, Iterable, List


class StatTemplate(IJsonExchangeable):

    def __init__(self,
                 stat: Stat,
                 base: Optional[Union[int, Iterable[int]]] = None,
                 ev: Optional[Union[int, Iterable[int]]] = None,
                 iv: Optional[Union[int, Iterable[int]]] = None,
                 level: Optional[Union[int, Iterable[int]]] = None,
                 nature: Optional[Union[Nature, Iterable[Nature]]] = None):
        if stat not in NUMBER_STATS:
            raise StatError(f"Stat '{stat}' does not have a numerical value.")

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
