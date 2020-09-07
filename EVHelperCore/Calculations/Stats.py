from EVHelperCore.Objects import *
from EVHelperCore.Exceptions import StatError

import math
from typing import Iterable, Tuple


def get_stat_value_from_info(stat_info: Stats, stat: Stat) -> int:
    if stat not in NUMBER_STATS:
        raise StatError(f"Stat '{stat}' does not have a numerical value.")

    return get_stat_value(stat=stat,
                          base=stat_info.base_stats.get_stat(stat),
                          iv=stat_info.ivs[stat],
                          ev=stat_info.evs[stat],
                          level=stat_info.level,
                          nature=stat_info.nature)


def get_stat_value(stat: Stat, base: int, ev: int, iv: int, level: int, nature: Nature) -> int:
    base = base * 2
    ev = ev // 4
    flat_mod = (level + 10) if stat == Stat.HP else 5
    nature_mod = nature.get_modifier(stat)

    # https://bulbapedia.bulbagarden.net/wiki/Statistic#Determination_of_stats
    internal = ((base + iv + ev) * level) // 100
    return math.floor((internal + flat_mod) * nature_mod)


def get_base_stat_from_value(stat: Stat, ev: int, iv: int, level: int, nature: Nature,
                             value: int) -> Iterable[int]:
    bases = set()

    ev = ev // 4

    for y in _get_internal_formula_value(stat, level, nature, value):
        lower_bound = math.ceil((-iv - ev + ((100 / level) * y)) / 2)
        upper_bound = math.ceil((-iv - ev + ((100 / level) * (y + 1))) / 2)
        lower_bound = max(1, lower_bound)
        upper_bound = min(256, upper_bound)

        for b in range(lower_bound, upper_bound):
            bases.add(b)

    return bases


def get_evs_from_value(stat: Stat, base: int, iv: int, level: int, nature: Nature, value: int) -> Iterable[int]:
    evs = set()

    for y in _get_internal_formula_value(stat, level, nature, value):
        lower_bound = math.ceil(-(2 * base) - iv + ((100 / level) * y))
        upper_bound = math.ceil(-(2 * base) - iv + ((100 / level) * (y + 1)))
        lower_bound = max(0, lower_bound)
        upper_bound = min((EV.MAX // 4) + 1, upper_bound)

        for ev in range(lower_bound, upper_bound):
            evs.add(ev * 4)

    return evs


def get_ivs_from_value(stat: Stat, base: int, ev: int, level: int, nature: Nature, value: int) -> Iterable[int]:
    ivs = set()

    ev = ev // 4

    for y in _get_internal_formula_value(stat, level, nature, value):
        lower_bound = math.ceil(-(2 * base) - ev + ((100 / level) * y))
        upper_bound = math.ceil(-(2 * base) - ev + ((100 / level) * (y + 1)))
        lower_bound = max(0, lower_bound)
        upper_bound = min(IV.MAX + 1, upper_bound)

        for iv in range(lower_bound, upper_bound):
            ivs.add(iv)

    return ivs


def _get_internal_formula_value(stat: Stat, level: int, nature: Nature, value: int) -> Iterable[int]:
    flat_mod = (level + 10) if stat == Stat.HP else 5
    nature_mod = nature.get_modifier(stat)

    lower_bound = math.ceil((value / nature_mod) - flat_mod)
    upper_bound = math.ceil(((value + 1) / nature_mod) - flat_mod)

    yield from range(lower_bound, upper_bound)


def get_stat_range(stat: Stat, base: int, level: int) -> Tuple[int, int]:
    return get_stat_value(stat=stat,
                          base=base,
                          ev=0,
                          iv=0,
                          level=level,
                          nature=Nature.build_hindering(stat)), \
           get_stat_value(stat=stat,
                          base=base,
                          ev=EV.MAX,
                          iv=IV.MAX,
                          level=level,
                          nature=Nature.build_boosting(stat))
