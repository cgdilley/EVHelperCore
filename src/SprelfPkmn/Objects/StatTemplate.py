from __future__ import annotations

from SprelfJSON import JSONModel

from SprelfPkmn.Objects.Stats import Stat, Nature, StatError

from typing import Iterable


class StatTemplate(JSONModel):
    """
    A collection of restrictions on stat information options (EV, IV, level, nature, base stat), used as a filter
    when calculating all the possible combinations of these that leads to a particular stat value.
    For example, if you wanted to calculate what the base Speed stat of a Pokémon with a certain numerical Speed stat,
    assuming that Pokémon has maximum EVs and a boosting nature (and at a particular level),
    you can create a StatTemplate that includes those restrictions and come up with the result you want when passing
    that StatTemplate to the relevant calculation functions.
    """
    stat: Stat
    base: list[int] | None = None
    ev: list[int] | None = None
    iv: list[int] | None = None
    level: list[int] | None = None
    nature: list[Nature] | None = None

    def __init__(self,
                 stat: Stat,
                 base: int | Iterable[int] | None = None,
                 ev: int | Iterable[int] | None = None,
                 iv: int | Iterable[int] | None = None,
                 level: int | Iterable[int] | None = None,
                 nature: Nature | Iterable[Nature] | None = None):
        """
        :param stat: The stat to create the stat template for
        :param base: The base stat value for the specified stat
        :param ev: The EVs invested into the specified stat
        :param iv: The IVs for the specified stat
        :param level: The level of the Pokémon
        :param nature: The stat-modifying nature of the Pokémon
        """

        def _standardize(val, expected_type: type):
            if val is None:
                return None
            if type(val) == expected_type:
                return [val]
            if len(val) == 0:
                return None
            return sorted(list(val)) if hasattr(expected_type, "__cmp__") else list(val)

        super().__init__(stat=stat, base=_standardize(base, int),
                         ev=_standardize(ev, int),
                         iv=_standardize(iv, int),
                         level=_standardize(level, int),
                         nature=_standardize(nature, Nature))
        StatError.check_number_stat(self.stat)

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
