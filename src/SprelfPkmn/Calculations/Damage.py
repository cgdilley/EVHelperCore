from SprelfPkmn.Objects import *
from SprelfPkmn.Calculations.Stats import get_stat_value_from_info
from SprelfJSON import JSONModel

from typing import Iterable
import math

from SprelfPkmn.Objects.Move import WeatherDamageCondition, CalculationCondition


#


class DamageReport(JSONModel):
    rolls: list[int]
    move: DamagingMove
    attacker: Pokemon
    defender: Pokemon
    critical: bool
    conditions: list[CalculationCondition]

    def __str__(self) -> str:
        # TODO: Standardized damage calc string
        raise NotImplementedError()


#


def calculate_damage(attacker: Pokemon, defender: Pokemon,
                     move: DamagingMove,
                     board_state: BoardState,
                     critical: bool = False) -> DamageReport:
    # Get relevant offensive and defensive stats
    o_stat = get_stat_value_from_info(attacker.stats, move.offense_stat)
    d_stat = get_stat_value_from_info(defender.stats, move.defense_stat)

    o_stat *= attacker.stats.get_modifier(stat=move.offense_stat, minimum=0 if critical else None).multiplier
    d_stat *= defender.stats.get_modifier(stat=move.defense_stat, maximum=0 if critical else None).multiplier

    damage_ratio = math.floor(o_stat) / math.floor(d_stat)

    # Stat-modifying conditions (eg. Rock types in Sand)
    stat_conditions = list(move.get_stat_conditions(attacker=attacker,
                                                    defender=defender,
                                                    board_state=board_state))
    for cond in stat_conditions:
        if cond.stat == move.offense_stat and cond.for_attacker:
            o_stat *= cond.multiplier
        if cond.stat == move.defense_stat and not cond.for_attacker:
            d_stat *= cond.multiplier

    # Get base power
    base_power = move.base_power

    base_power_conditions = list(move.get_base_power_modifiers(attacker=attacker,
                                                               defender=defender,
                                                               board_state=board_state))
    for cond in base_power_conditions:
        base_power = rounding_mult(base_power, cond.multiplier, hard_round=False)

    # BASELINE DAMAGE CALC BEFORE DAMAGE MODIFIERS
    level_factor = ((2 * attacker.stats.level) // 5) + 2
    numerator = (level_factor * base_power * damage_ratio) // 1
    base_value = (numerator // 50) + 2
    # ---------------------------------------------

    # Get damage conditions
    damage_conditions = list(move.get_damage_conditions(attacker=attacker,
                                                        defender=defender,
                                                        board_state=board_state,
                                                        critical=critical))

    # Multi-target multiplier
    multi_mult = 0.75 if board_state.is_doubles and MoveProperties.MULTI_TARGET in move.properties else 1
    base_value = rounding_mult(base_value, multi_mult, hard_round=False)

    # Weather
    weather_mult = 1
    for c in damage_conditions:
        if not isinstance(c, WeatherDamageCondition):
            continue
        weather_mult *= c.multiplier
    base_value = rounding_mult(base_value, weather_mult, hard_round=False)

    # Critical
    base_value = rounding_mult(base_value,
                               1 if not critical else 1.5,
                               hard_round=True)

    # STAB (applied later)
    stab_multiplier = 1
    if move.type in attacker.data.typing:
        stab_multiplier = 2 if attacker.ability.name == "Adaptability" else 1.5

    # Type effectiveness (applied later)
    typing_multiplier = Type.get_damage_multiplier(move.type, defender.data.typing)

    rolls: list[int] = []
    if base_power == 0 or typing_multiplier == 0:
        rolls = [0] * 16
    else:
        # Random factors
        values: Iterable[int] = (rounding_mult(base_value, (r / 100), hard_round=True) for r in range(85, 101))

        for value in values:
            # STAB
            value = rounding_mult(value, stab_multiplier, hard_round=False)

            # Type effectiveness
            value = rounding_mult(value, typing_multiplier, hard_round=True)

            # Status multiplier
            # TODO: Implement

            # Other multipliers
            for cond in damage_conditions:
                if isinstance(cond, WeatherDamageCondition):
                    continue
                value = rounding_mult(value, cond.multiplier, hard_round=False)

            rolls.append(value)

    return DamageReport(rolls=rolls,
                        move=move,
                        attacker=attacker,
                        defender=defender,
                        critical=critical,
                        conditions=damage_conditions + base_power_conditions + stat_conditions)


#


def get_damage_rolls(attacker: Pokemon,
                     defender: Pokemon,
                     move: DamagingMove,
                     board_state: BoardState,
                     critical: bool = False) -> Iterable[int]:
    report = calculate_damage(attacker, defender, move, board_state, critical)
    return report.rolls


def rounding_mult(v1: float, v2: float, hard_round: bool = False) -> int:
    new_value = v1 * v2
    as_int = int(new_value)
    if hard_round:
        return as_int
    return as_int if math.isclose(new_value - as_int, 0.5) or new_value - as_int <= 0.5 else as_int + 1
