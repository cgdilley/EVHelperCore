from __future__ import annotations

from SprelfPkmn.Objects import *
from SprelfPkmn.Calculations.Stats import get_stat_value_from_info
from SprelfJSON import JSONModel

from typing import Iterable, TypeVar
import math

from SprelfPkmn.Utils import ShowdownUtils


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

    immune = False
    # Get base power
    base_power = move.base_power

    base_power_conditions = list(move.get_base_power_modifiers(attacker=attacker,
                                                               defender=defender,
                                                               board_state=board_state))
    for cond in base_power_conditions:
        base_power = rounding_mult(base_power, cond.multiplier, hard_round=False)
        immune |= cond.multiplier == 0

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
    immune |= weather_mult == 0

    # Critical
    base_value = rounding_mult(base_value,
                               1 if not critical else 1.5,
                               hard_round=True)

    # STAB (applied later)
    stab_multiplier = 1
    stab_conditions = list(move.get_stab_modifiers(attacker=attacker,
                                                   defender=defender,
                                                   board_state=board_state))
    if move.type in attacker.data.typing:
        if len(stab_conditions) > 0:
            for c in stab_conditions:
                stab_multiplier *= c.multiplier
        else:
            stab_multiplier = 1.5

    # Type effectiveness (applied later)
    typing_multiplier = Type.get_damage_multiplier(move.type, defender.data.typing)
    immune |= typing_multiplier == 0

    rolls: list[int] = []
    if base_value == 0 or typing_multiplier == 0:
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
                immune |= cond.multiplier == 0

            rolls.append(0 if immune else max(value, 1))

    return DamageReport(rolls=rolls,
                        move=move,
                        attacker=attacker,
                        defender=defender,
                        critical=critical,
                        conditions=damage_conditions + base_power_conditions + stab_conditions + stat_conditions)


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


#

TCond = TypeVar("TCond", bound=CalculationCondition)


class DamageReport(JSONModel):
    rolls: list[int]
    move: DamagingMove
    attacker: Pokemon
    defender: Pokemon
    critical: bool
    conditions: list[CalculationCondition]

    def __str__(self) -> str:
        return " ".join(self.get_report_components()).replace(" :", ":")

    def __repr__(self) -> str:
        return str(self)

    @property
    def max_roll(self) -> int:
        return self.rolls[-1]

    @property
    def min_roll(self) -> int:
        return self.rolls[0]

    def get_report_components(self) -> Iterable[str]:
        if self.max_roll > 0:
            # Stat modifiers
            stat_stages = self.attacker.stats.modifiers.get(self.move.offense_stat, 0)
            if stat_stages > 0:
                yield f"+{stat_stages}"
            elif stat_stages < 0 and not self.critical:
                yield f"{stat_stages}"

            # EVs and Nature for attacker
            yield self._get_ev_component(self.attacker.stats, self.move.offense_stat)

            # Item modifiers
            yield from (c.item.name for c in self._get_conditions(ItemCondition)
                        if getattr(c, "for_attacker", True))

            # Ability modifiers
            yield from (c.ability.name for c in self._get_conditions(AbilityCondition)
                        if getattr(c, "for_attacker", True))

        # Pokemon and Move
        yield ShowdownUtils.format_name(self.attacker.data.name.base_name(),
                                                    self.attacker.data.variant)
        yield self.move.name

        if self.max_roll > 0:
            base_power_conds = [bpc for bpc in self._get_conditions(BasePowerCondition)
                                if bpc.innate]
            if len(base_power_conds) > 0:
                base_power = self.move.base_power
                for bpc in base_power_conds:
                    base_power = rounding_mult(base_power, bpc.multiplier, hard_round=False)
                yield f"({base_power} BP)"

        yield "vs."

        if self.max_roll > 0:
            # Stat modifiers for defender
            stat_stages = self.defender.stats.modifiers.get(self.move.defense_stat, 0)
            if stat_stages > 0 and not self.critical:
                yield f"+{stat_stages}"
            elif stat_stages < 0:
                yield f"{stat_stages}"

            # EVs and Nature for defender
            hp_evs = self.defender.stats.evs[Stat.HP].number
            yield f"{hp_evs} HP"
            yield "/"
            yield self._get_ev_component(self.defender.stats, self.move.defense_stat)

            # Item modifiers
            yield from (c.item.name for c in self._get_conditions(ItemCondition)
                        if not getattr(c, "for_attacker", True))

        # Ability modifiers
        yield from (c.ability.name for c in self._get_conditions(AbilityCondition)
                    if not getattr(c, "for_attacker", True)
                    and (self.max_roll > 0
                         or any(math.isclose(getattr(c, "multiplier", -1), 0)
                                for c in self._get_conditions(AbilityCondition))))

        yield f"{ShowdownUtils.format_name(self.defender.data.name.base_name(), self.defender.data.variant)}"

        if self.max_roll > 0:
            # Weather modifiers
            weathers = {c.weather for c in self._get_conditions(WeatherCondition)}
            if len(weathers) > 1:
                raise ValueError("Multiple weather conditions found")
            if len(weathers) > 0:
                w = next(iter(weathers))
                w_name = " ".join(p.lower().capitalize() for p in w.name.split("_"))
                yield f"in {w_name}"

            # Screens
            screens = {c.effect for c in self._get_conditions(ScreensDamageCondition)}
            if len(screens) > 0:
                s = next(iter(screens))
                s_name = " ".join(p.lower().capitalize() for p in s.name.split("_"))
                yield f"through {s_name}"

            # Critical hits
            if self.critical:
                yield "on a critical hit"

        yield ":"

        # Rolls
        if math.isclose(self.rolls[0], self.rolls[-1]):
            yield f"{self.rolls[0]}"
        else:
            yield f"{self.rolls[0]}-{self.rolls[-1]}"
        def_hp = get_stat_value_from_info(self.defender.stats, Stat.HP)
        low_perc = int(1000 * self.rolls[0] / def_hp) / 10
        high_perc = int(1000 * self.rolls[-1] / def_hp) / 10
        low_perc = int(low_perc) if low_perc == int(low_perc) else low_perc
        high_perc = int(high_perc) if high_perc == int(high_perc) else high_perc
        if math.isclose(low_perc, high_perc):
            yield f"({low_perc}%)"
        else:
            yield f"({low_perc} - {high_perc}%)"

        yield "--"

        hits, probability = self.get_knockout_prognosis()
        if hits is None:
            yield "No damage for you"
        elif hits > 9:
            yield "possibly the worst move ever"
        else:
            ko_str = "OHKO" if hits == 1 else f"{hits}HKO"
            if math.isclose(probability, 1):
                yield f"guaranteed {ko_str}"
            elif math.isclose(probability, 0):
                yield f"possible {ko_str}"
            else:
                yield f"{probability:.2%} chance to {ko_str}"

    #

    #

    def get_knockout_prognosis(self, precise_hits: int = 4) -> tuple[int | None, float]:
        distribution: dict[int, int] = {0: 1}
        hp_goal = get_stat_value_from_info(self.defender.stats, Stat.HP)

        if self.max_roll == 0:
            return None, 1.0
        worst_case = math.ceil(hp_goal / self.min_roll)
        best_case = math.ceil(hp_goal / self.max_roll)
        if best_case > precise_hits:
            if worst_case == best_case:
                return worst_case, 1.0
            return best_case, 0.0

        for hits in range(1, precise_hits + 1):

            new_dist: dict[int, int] = {}

            for damage, ways in distribution.items():
                for roll in self.rolls:
                    new_dist.setdefault(damage + roll, 0)
                    new_dist[damage + roll] += ways

            distribution = new_dist

            successful = sum(ways
                for damage, ways in distribution.items()
                if damage >= hp_goal)

            probability = successful / (len(self.rolls) ** hits)

            if probability > 0:
                return hits, probability

        raise RuntimeError("Unable to build KO prognosis")


    def _get_conditions(self, t: type[TCond]) -> list[TCond]:
        return [c for c in self.conditions if isinstance(c, t)]


    def _get_ev_component(self, stats: Stats, relevant_stat: Stat):
        ev = stats.evs[relevant_stat].number
        nature_mod = stats.nature.get_modifier(relevant_stat)
        abbr = self._stat_abbreviation(relevant_stat)
        if nature_mod > 1:
            return f"{ev}+ {abbr}"
        elif nature_mod < 1:
            return f"{ev}- {abbr}"
        else:
            return f"{ev} {abbr}"

    @classmethod
    def _stat_abbreviation(cls, stat: Stat):
        match stat:
            case Stat.HP:
                return "HP"
            case Stat.ATTACK:
                return "Atk"
            case Stat.DEFENSE:
                return "Def"
            case Stat.SP_ATTACK:
                return "SpA"
            case Stat.SP_DEFENSE:
                return "SpD"
            case Stat.SPEED:
                return "Spe"
            case _:
                raise ValueError(f"Stat has no abbreviation: {stat}")


