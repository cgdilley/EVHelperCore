from EVHelperCore.Objects import *
from EVHelperCore.Exceptions import StatError

import math
from typing import Iterable, Tuple


def get_stat_value_from_info(stat_info: Stats, stat: Stat) -> int:
    """
    Calculates the numerical stat value of the specified stat based on the given stat information, including
    base stats, level, EVs, IVs, and nature.

    :param stat_info: A collection of stat information to use as the basis for the calculation
    :param stat: The stat to calculate the value of (eg. ATTACK, HP)
    :return: The numerical value of the specified stat based on the given stat information
    :raises StatError: Raises an error if the specified stat does not have a numerical value
    """
    check_number_stat(stat)
    return get_stat_value(stat=stat,
                          base=stat_info.base_stats.get_stat(stat),
                          iv=stat_info.ivs[stat],
                          ev=stat_info.evs[stat],
                          level=stat_info.level,
                          nature=stat_info.nature)


#


def get_stat_value(stat: Stat, base: int, ev: int, iv: int, level: int, nature: Nature) -> int:
    """
    Calculates the numerical stat value of the specified stat based on the given stat information

    :param stat: The stat to calculate the value of (eg. ATTACK, HP)
    :param base: The base stat value for the specified stat
    :param ev: The EVs invested into the specified stat
    :param iv: The IVs for the specified stat
    :param level: The level of the Pokémon
    :param nature: The stat-modifying nature of the Pokémon
    :return: The numerical value of the specified stat based on the given stat information
    :raises StatError: Raises an error if the specified stat does not have a numerical value,
    or if any the given stat information is invalid.
    """
    check_number_stat(stat)
    if not (0 <= ev <= EV.MAX):
        raise StatError(f"Invalid EV value: {ev}")
    if not (0 <= iv <= IV.MAX):
        raise StatError(f"Invalid IV value: {iv}")
    if not (1 <= level <= 100):
        raise StatError(f"Invalid level: {level}")
    if not (1 <= base <= 255):
        raise StatError(f"Invalid base stat: {base}")

    base = base * 2
    ev = ev // 4
    flat_mod = (level + 10) if stat == Stat.HP else 5
    nature_mod = nature.get_modifier(stat)

    # https://bulbapedia.bulbagarden.net/wiki/Statistic#Determination_of_stats
    internal = ((base + iv + ev) * level) // 100
    return math.floor((internal + flat_mod) * nature_mod)


#


def get_base_stat_from_value(stat: Stat, ev: int, iv: int, level: int, nature: Nature,
                             value: int) -> Iterable[int]:
    """
    With the given numerical stat value, reverse engineer the possible base stat values of the Pokémon based
    on the other given stat information.

    :param stat: The stat to calculate the base value for (eg. ATTACK, HP)
    :param ev: The EVs invested into the specified stat
    :param iv: The IVs for the specified stat
    :param level: The level of the Pokémon
    :param nature: The stat-modifying nature of the Pokémon
    :param value: The final numerical value of the stat to reverse-engineer
    :return: A lazy generator for all of the possible base stat values based on the given stat information
    """
    bases = set()

    ev = ev // 4

    for y in _get_internal_formula_value(stat, level, nature, value):
        lower_bound = math.ceil((-iv - ev + ((100 / level) * y)) / 2)
        upper_bound = math.ceil((-iv - ev + ((100 / level) * (y + 1))) / 2)
        lower_bound = max(1, lower_bound)
        upper_bound = min(256, upper_bound)

        for b in range(lower_bound, upper_bound):
            if b not in bases:
                bases.add(b)
                yield b


#


def get_evs_from_value(stat: Stat, base: int, iv: int, level: int, nature: Nature, value: int) -> Iterable[int]:
    """
    With the given numerical stat value, reverse engineer the possible EV values of the Pokémon based
    on the other given stat information.

    :param stat: The stat to calculate the base value for (eg. ATTACK, HP)
    :param base: The base stat value for the specified stat
    :param iv: The IVs for the specified stat
    :param level: The level of the Pokémon
    :param nature: The stat-modifying nature of the Pokémon
    :param value: The final numerical value of the stat to reverse-engineer
    :return: A lazy generator for all of the possible EV values based on the given stat information
    """
    evs = set()

    for y in _get_internal_formula_value(stat, level, nature, value):
        lower_bound = math.ceil(-(2 * base) - iv + ((100 / level) * y))
        upper_bound = math.ceil(-(2 * base) - iv + ((100 / level) * (y + 1)))
        lower_bound = max(0, lower_bound)
        upper_bound = min((EV.MAX // 4) + 1, upper_bound)

        for ev in range(lower_bound, upper_bound):
            if ev not in evs:
                evs.add(ev * 4)
                yield ev


#


def get_ivs_from_value(stat: Stat, base: int, ev: int, level: int, nature: Nature, value: int) -> Iterable[int]:
    """
    With the given numerical stat value, reverse engineer the possible IV values of the Pokémon based
    on the other given stat information.

    :param stat: The stat to calculate the base value for (eg. ATTACK, HP)
    :param base: The base stat value for the specified stat
    :param ev: The EVs invested into the specified stat
    :param level: The level of the Pokémon
    :param nature: The stat-modifying nature of the Pokémon
    :param value: The final numerical value of the stat to reverse-engineer
    :return: A lazy generator for all of the possible IV values based on the given stat information
    """
    ivs = set()

    ev = ev // 4

    for y in _get_internal_formula_value(stat, level, nature, value):
        lower_bound = math.ceil(-(2 * base) - ev + ((100 / level) * y))
        upper_bound = math.ceil(-(2 * base) - ev + ((100 / level) * (y + 1)))
        lower_bound = max(0, lower_bound)
        upper_bound = min(IV.MAX + 1, upper_bound)

        for iv in range(lower_bound, upper_bound):
            if iv not in ivs:
                ivs.add(iv)
                yield iv


#


def _get_internal_formula_value(stat: Stat, level: int, nature: Nature, value: int) -> Iterable[int]:
    """
    Calculation to determine the possible values of the inner floor portion of the stat formula after flooring,
    based on the given level and nature, for the given numerical stat value.  This means that this internal formula
    portion (which incorporates based stats, EVs, and IVs) must floor down to one of the returned values.
    This may be used to further narrow down the possible values for those internal formula stats.

    This executes lazily.
    """
    check_number_stat(stat)
    flat_mod = (level + 10) if stat == Stat.HP else 5
    nature_mod = nature.get_modifier(stat)

    lower_bound = math.ceil((value / nature_mod) - flat_mod)
    upper_bound = math.ceil(((value + 1) / nature_mod) - flat_mod)

    yield from range(lower_bound, upper_bound)


#


def get_stat_range(stat: Stat, base: int, level: int) -> Tuple[int, int]:
    """
    Calculate the theoretical minimum and maximum stat values for the specified stat on a Pokémon with the
    given base stat value and level.  The minimum value includes 0 EVs, 0 IVs, and a hindering nature.  The
    maximum value includes max EVs, max IVs, and a boosting nature.  The values are returned as a tuple.

    :param stat: The stat to calculate the base value for (eg. ATTACK, HP)
    :param base: The base stat value for the specified stat
    :param level: The level of the Pokémon
    :return: A tuple with the following values:
        0: The minimum possible numerical value for the given stat, with the given base stat value and level
        1: The maximum possible numerical value for the given stat, with the given base stat value and level
    :raises StatError: Raises an error if the specified stat does not have a numerical value
    """
    return (get_stat_value(stat=stat,
                           base=base,
                           ev=0,
                           iv=0,
                           level=level,
                           nature=Nature.build_hindering(stat)),
            get_stat_value(stat=stat,
                           base=base,
                           ev=EV.MAX,
                           iv=IV.MAX,
                           level=level,
                           nature=Nature.build_boosting(stat)))
