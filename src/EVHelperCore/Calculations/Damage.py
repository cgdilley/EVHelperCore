from EVHelperCore.Objects import *
from EVHelperCore.Calculations.Stats import get_stat_value_from_info

from typing import Iterable


def calculate_damage(attacker: Pokemon, defender: Pokemon, move: DamagingMove, critical: bool = False) -> Iterable[int]:
    o_stat = get_stat_value_from_info(attacker.stats, move.offense_stat)
    d_stat = get_stat_value_from_info(defender.stats, move.defense_stat)

    o_stat *= attacker.stats.get_modifier(stat=move.offense_stat, minimum=0 if critical else None).multiplier
    d_stat *= defender.stats.get_modifier(stat=move.defense_stat, maximum=0 if critical else None).multiplier

    damage_ratio = o_stat / d_stat

    base_value = (((((2*attacker.stats.level)/5)+2) * move.base_power * damage_ratio) / 50) + 2

    # Multi-target multiplier
    # TODO: Implement
    base_value = rounding_mult(base_value, 1, hard_round=True)

    # Weather
    # TODO: Implement
    base_value = rounding_mult(base_value, 1, hard_round=True)

    # Critical
    base_value = rounding_mult(base_value, 1.5 if critical else 1, hard_round=True)

    # Random factors
    values: Iterable[int] = (rounding_mult(base_value, (r/100), hard_round=True) for r in range(85, 101))

    for value in values:

        # STAB
        if move.type in attacker.data.typing:
            value = rounding_mult(value, 1.5)

        # Type effectiveness
        value = rounding_mult(value, Type.get_damage_multiplier(move.type, defender.data.typing))

        # Status multiplier
        # TODO: Implement

        # Other multipliers
        # TODO: Implement

        yield value


def rounding_mult(v1: float, v2: float, hard_round: bool = False) -> int:
    new_value = v1 * v2
    as_int = int(new_value)
    if hard_round:
        return as_int
    return as_int if new_value - as_int <= 0.5 else as_int + 1
