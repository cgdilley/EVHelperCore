from __future__ import annotations

from SprelfPkmn.Objects import *
from SprelfPkmn.Implementations import *
from SprelfPkmn.Calculations.Stats import get_stat_value_from_info
from SprelfJSON import JSONModel

from typing import Iterable, TypeVar, Collection
import math

from SprelfPkmn.Utils import ShowdownUtils, FormatUtils


#


def calculate_damage(attacker: PokemonState,
                     defender: PokemonState,
                     move: DamagingMove,
                     board_state: BoardState,
                     critical: bool = False) -> DamageReport:
    # Get relevant offensive and defensive stats
    o_stat = get_stat_value_from_info(attacker.stats, move.offense_stat)
    d_stat = get_stat_value_from_info(defender.stats, move.defense_stat)

    o_stat *= attacker.stats.get_modifier(stat=move.offense_stat, minimum=0 if critical else None).multiplier
    if attacker.ability.name != "Unaware":
        def_mult = defender.stats.get_modifier(stat=move.defense_stat, maximum=0 if critical else None).multiplier
        if def_mult < 1 or MoveProperties.IGNORES_BOOSTS not in move.properties:
            d_stat *= def_mult

    # Stat-modifying conditions (eg. Rock types in Sand)
    stat_conditions = list(move.get_stat_conditions(attacker=attacker,
                                                    defender=defender,
                                                    board_state=board_state))
    for cond in stat_conditions:
        if cond.stat == move.offense_stat and cond.for_attacker:
            o_stat *= cond.multiplier
        if cond.stat == move.defense_stat and not cond.for_attacker:
            d_stat *= cond.multiplier

    # Calculate ratio between offense and defense stats
    damage_ratio = math.floor(o_stat) / math.floor(d_stat)

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
    stab_conditions = list(move.get_stab_modifiers(attacker=attacker,
                                                   defender=defender,
                                                   board_state=board_state))
    if move.type in attacker.typing:
        if len(stab_conditions) > 0:
            for c in stab_conditions:
                stab_multiplier *= c.multiplier
        else:
            stab_multiplier = 1.5

    # Type effectiveness (applied later)
    typing_multiplier = Type.get_damage_multiplier(move.type, defender.typing)

    rolls: list[int] = []
    if base_value == 0 or typing_multiplier == 0 \
            or any(math.isclose(c.multiplier, 0) for c in damage_conditions):
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
            if attacker.status == StatusCondition.BURNED \
                    and move.damage_class == DamageClass.PHYSICAL \
                    and attacker.ability.name != "Guts":
                value = rounding_mult(value, 0.5, hard_round=False)

            # Other multipliers
            for cond in damage_conditions:
                if isinstance(cond, WeatherDamageCondition):
                    continue
                value = rounding_mult(value, cond.multiplier, hard_round=False)

            rolls.append(max(value, 1))

    return DamageReport(rolls=rolls,
                        move=move,
                        attacker=attacker,
                        defender=defender,
                        critical=critical,
                        conditions=damage_conditions + base_power_conditions + stab_conditions + stat_conditions,
                        terrain=board_state.terrain,
                        weather=board_state.weather)


#


def get_damage_rolls(attacker: PokemonState,
                     defender: PokemonState,
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
    attacker: PokemonState
    defender: PokemonState
    critical: bool
    conditions: list[CalculationCondition]
    terrain: Terrain = Terrain.NONE
    weather: Weather = Weather.NONE

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

            # Status modifiers
            if self.attacker.status == StatusCondition.BURNED \
                    and self.move.damage_class == DamageClass.PHYSICAL \
                    and self.attacker.ability.name != "Guts":
                yield "burned"

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

        # Weather modifiers
        weather_conds = self._get_conditions(WeatherCondition)
        weathers = {c.weather for c in weather_conds}
        if len(weathers) > 1:
            raise ValueError("Conflicting weather conditions found")
        has_weather = len(weathers) > 0 and (
                self.max_roll > 0 or any(hasattr(cond, "multiplier") and math.isclose(cond.multiplier, 0)
                                         for cond in weather_conds))
        if has_weather:
            w = next(iter(weathers))
            w_name = " ".join(p.lower().capitalize() for p in w.name.split("_"))
            yield f"in {w_name}"

        # Weather modifiers
        terrain_conds = self._get_conditions(TerrainBasePowerCondition)
        terrains = {c.terrain for c in terrain_conds}
        if len(terrains) > 1:
            raise ValueError("Conflicting terrain conditions found")
        if len(terrains) > 0:
            w = next(iter(terrains))
            w_name = " ".join(p.lower().capitalize() for p in w.name.split("_"))
            yield f"{'and' if has_weather else 'in'} {w_name} Terrain"

        if self.max_roll > 0:
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
        if math.isclose(low_perc, high_perc):
            yield f"({FormatUtils.format_number(low_perc, max_decimals=1)}%)"
        else:
            yield f"({FormatUtils.format_number(low_perc, max_decimals=1)} - {FormatUtils.format_number(high_perc, max_decimals=1)}%)"

        yield "--"

        hp_effects = list(self._get_hp_effects())
        if len(hp_effects) > 0:
            heal_effects = [h for _, h, _ in hp_effects if h > 0]
            dmg_effects = [d for _, d, _ in hp_effects if d < 0]
            ramp_effects = [r for _, _, r in hp_effects if r < 0]
            hits, probability = self.get_knockout_prognosis(heal_effects=heal_effects,
                                                            dmg_effects=dmg_effects,
                                                            ramp_effects=ramp_effects)
        else:
            hits, probability = self.get_knockout_prognosis()

        if hits is None:
            if self.max_roll > 0:
                yield "possibly the worst move ever"
            else:
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
                yield f"{FormatUtils.format_number(probability * 100, max_decimals=2)}% chance to {ko_str}"

            # Healing indications
            if len(hp_effects) > 0:
                if len(hp_effects) > 2:
                    combined = ", ".join(eff for eff, _, _ in hp_effects[:-1]) + f", and {hp_effects[-1][0]}"
                elif len(hp_effects) > 1:
                    combined = f"{hp_effects[0][0]} and {hp_effects[1][0]}"
                else:
                    combined = hp_effects[0][0]
                yield f"after {combined}"

    #

    #

    def get_knockout_prognosis(self,
                               precise_hits: int = 4,
                               heal_effects: Collection[float] = (),
                               dmg_effects: Collection[float] = (),
                               ramp_effects: Collection[float] = ()) -> tuple[int | None, float]:
        if self.max_roll == 0:
            return None, 1.0

        max_hp = get_stat_value_from_info(self.defender.stats, Stat.HP)
        heal_amounts = [max(int(max_hp * h), 1) for h in heal_effects]
        dmg_amounts = [min(int(max_hp * d), -1) for d in dmg_effects]
        hp_per_turn = sum(heal_amounts) + sum(dmg_amounts)

        if len(ramp_effects) == 0 and hp_per_turn >= self.max_roll and self.max_roll < max_hp:
            return None, 1.0

        # turns = hp_goal / roll
        # -> with end-of-turn effects, it's more complicated
        if len(heal_effects) == 0 and len(dmg_effects) == 0 and len(ramp_effects) == 0:
            worst_case = math.ceil(max_hp / self.min_roll)
            best_case = math.ceil(max_hp / self.max_roll)
        else:
            worst_case = self._roll_solve(max_hp, hp_per_turn, ramp_effects, self.min_roll)
            best_case = self._roll_solve(max_hp, hp_per_turn, ramp_effects, self.max_roll)

        if best_case is None:
            return None, 1.0

        if best_case > precise_hits:
            if worst_case == best_case:
                return worst_case, 1.0
            return best_case, 0.0

        distribution: dict[int, int] = {0: 1}
        hp_goal = max_hp
        for hits in range(1, precise_hits + 1):

            new_dist: dict[int, int] = {}

            for damage, ways in distribution.items():
                for roll in self.rolls:
                    new_dist.setdefault(damage + roll, 0)
                    new_dist[damage + roll] += ways

            distribution = new_dist

            # The calculators are bugged.  This line would match calculator behavior.
            # hp_step = hp_per_turn + sum(min(int(max_hp * r * (hits - 1)), -1) for r in ramp_effects) \
            #     if hits > 1 else hp_per_turn
            hp_step = hp_per_turn + sum(min(int(max_hp * r * hits), -1) for r in ramp_effects)

            # Check if knocked out before damage effects
            successful_no_effects = sum(ways
                                        for damage, ways in distribution.items()
                                        if damage >= hp_goal)

            # Check again after end-of-turn HP effects
            successful_with_effects = sum(ways
                                          for damage, ways in distribution.items()
                                          if damage >= hp_goal + hp_step)

            if successful_no_effects > 0 or successful_with_effects > 0:
                successful = max(successful_no_effects, successful_with_effects)
                probability = successful / (len(self.rolls) ** hits)
                return hits, probability

            hp_goal += hp_step

        raise RuntimeError("Unable to build KO prognosis")

    @classmethod
    def _roll_solve(cls, hp_goal: int, hp_per_turn: int, ramp_effects: Collection[float], roll: int,
                    maximum: int = 9) -> int | None:
        accumulated = 0
        for t in range(1, maximum + 2):
            accumulated += roll
            if accumulated >= hp_goal:
                return t
            accumulated -= hp_per_turn
            # Online calculators are bugged.  This line would match calculator behavior.
            # ramp_dmg = sum(min(int(hp_goal * r * (t - 1)), -1) for r in ramp_effects) \
            #     if t > 1 else 0
            ramp_dmg = sum(min(int(hp_goal * r * t), -1) for r in ramp_effects)
            accumulated -= ramp_dmg
            if accumulated >= hp_goal:
                return t
        return None

    def _get_conditions(self, t: type[TCond]) -> list[TCond]:
        return [c for c in self.conditions if isinstance(c, t)]

    def _get_hp_effects(self) -> Iterable[tuple[str, float, float]]:
        if self.weather == Weather.SAND and all(t not in self.defender.typing
                                                for t in (Type.ROCK, Type.GROUND, Type.STEEL)) \
                and self.defender.ability.name != "Magic Guard":
            yield "sandstorm damage", -1 / 16, 0

        if not any(v.name == "Heal Block" for v in self.defender.volatiles):
            if self.terrain == Terrain.GRASSY:
                yield "Grassy Terrain recovery", 1 / 16, 0
            if self.defender.item:
                if self.defender.item.name == "Leftovers":
                    yield "Leftovers recovery", 1 / 16, 0
                if self.defender.item.name == "Black Sludge" and Type.POISON in self.defender.typing:
                    yield "Black Sludge recovery", 1 / 16, 0
            if self.defender.ability.name == "Poison Heal" and self.defender.status in (StatusCondition.POISONED,
                                                                                        StatusCondition.BADLY_POISONED):
                yield "Poison Heal", 1 / 8, 0

        if self.defender.ability.name != "Magic Guard":
            if self.defender.item and self.defender.item.name == "Black Sludge" and Type.POISON not in self.defender.typing:
                yield "Black Sludge damage", -1 / 16, 0
            if self.defender.ability.name != "Poison Heal":
                if self.defender.status == StatusCondition.POISONED:
                    yield "poison damage", -1 / 8, 0
                elif self.defender.status == StatusCondition.BADLY_POISONED:
                    yield "toxic damage", 0, -1 / 16
                    # it seems like damage calcs don't take into account toxic ramping, even though I can.
                    # yield "toxic damage", -1 / 16, 0
            if self.defender.status == StatusCondition.BURNED:
                yield "burn damage", -1 / 16, 0

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
