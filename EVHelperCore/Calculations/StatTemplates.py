from EVHelperCore.Calculations.Stats import get_evs_from_value, get_base_stat_from_value, get_stat_value, \
    get_ivs_from_value
from EVHelperCore.Objects import StatTemplate, EV, IV, Nature, Stat

from typing import Iterable, Callable, Dict, Union, Set
import itertools


def get_combinations_for_value(stats: StatTemplate, value: int) -> Iterable[StatTemplate]:
    evs = stats.ev if stats.ev is not None else range(0, EV.MAX + 1, 4)
    ivs = stats.iv if stats.iv is not None else range(0, IV.MAX + 1)
    natures = stats.nature if stats.nature is not None else {Nature.build_boosting(stats.stat),
                                                             Nature.build_neutral(),
                                                             Nature.build_hindering(stats.stat)}
    levels = stats.level if stats.level is not None else (50, 100)
    bases = stats.base if stats.base is not None else range(0, 256)

    combinations = set()

    def _yield_unique(st: StatTemplate) -> Iterable[StatTemplate]:
        if st in combinations:
            return []
        combinations.add(st)
        return [st]

    def _calc_all_combinations(to_calc: str, calc_func: Callable) -> Iterable[StatTemplate]:
        # This weird stuff with known_keys is to ensure ordering, since dicts are unordered.
        # There is probably a way to clean this up to be more intuitive.
        known = {k: v for k, v in (("ev", evs), ("iv", ivs), ("nature", natures), ("level", levels), ("base", bases))
                 if k != to_calc}
        known_keys = list(known.keys())

        # This creates a collection of all possible combinations of all of the values in all of the separate
        # collections of values, as tuples... eg. (ev, iv, nature, level)
        combos = itertools.product(*(known[k] for k in known_keys))
        for combo in combos:
            args = {known_keys[i]: combo_val for i, combo_val in enumerate(combo)}
            for calc in calc_func(stat=stats.stat, value=value, **args):
                yield from _yield_unique(StatTemplate(stat=stats.stat, **{**args, to_calc: calc}))

    if stats.base is None:
        yield from _calc_all_combinations(to_calc="base", calc_func=get_base_stat_from_value)
    if stats.ev is None:
        yield from _calc_all_combinations(to_calc="ev", calc_func=get_evs_from_value)
    if stats.iv is None:
        yield from _calc_all_combinations(to_calc="iv", calc_func=get_ivs_from_value)

    if all(x is not None for x in (stats.base, stats.ev, stats.iv)):
        for base, ev, iv, level, nature in itertools.product(bases, evs, ivs, levels, natures):
            if get_stat_value(stats.stat, base, ev, iv, level, nature) == value:
                yield from _yield_unique(StatTemplate(stat=stats.stat, base=base, ev=ev,
                                                      iv=iv, level=level, nature=nature))


#
