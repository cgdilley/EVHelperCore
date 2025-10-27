from __future__ import annotations

from enum import Enum
from abc import ABCMeta
from typing import Iterable, Iterator

from SprelfJSON import JSONModel, JSONConvertible, JSONObject


class Stat(Enum):
    ATTACK = "ATTACK"
    DEFENSE = "DEFENSE"
    SP_ATTACK = "SP_ATTACK"
    SP_DEFENSE = "SP_DEFENSE"
    SPEED = "SPEED"
    HP = "HP"

    ACCURACY = "ACCURACY"
    EVASION = "EVASION"
    CRITICAL = "CRITICAL"


NUMBER_STATS = {Stat.ATTACK, Stat.DEFENSE, Stat.SP_ATTACK, Stat.SP_DEFENSE, Stat.SPEED, Stat.HP}


class StatError(Exception):

    @classmethod
    def check_number_stat(cls, stat: Stat):
        if stat not in NUMBER_STATS and stat != Stat.HP:
            raise StatError(f"Stat '{stat}' does not have a numerical value.")


class BaseStats(JSONConvertible, Iterable[tuple[Stat, int]]):

    def __init__(self, attack: int,
                 defense: int,
                 special_attack: int,
                 special_defense: int,
                 speed: int,
                 hp: int):
        self.stats: dict[Stat, int] = {
            Stat.ATTACK: attack,
            Stat.DEFENSE: defense,
            Stat.SP_ATTACK: special_attack,
            Stat.SP_DEFENSE: special_defense,
            Stat.SPEED: speed,
            Stat.HP: hp
        }

    def __str__(self) -> str:
        return " | ".join(f"{stat}: {value}" for stat, value in self.stats.items())

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> Iterator[tuple[Stat, int]]:
        return iter((s, v) for s, v in self.stats.items())

    def __eq__(self, o: object) -> bool:
        return isinstance(o, BaseStats) and all(self.stats[s] == o.stats[s] for s in self.stats.keys())

    def __ne__(self, o: object) -> bool:
        return not (self == o)

    def __hash__(self) -> int:
        return hash((self.stats[Stat.HP], self.stats[Stat.ATTACK], self.stats[Stat.DEFENSE],
                     self.stats[Stat.SP_ATTACK], self.stats[Stat.SP_DEFENSE], self.stats[Stat.SPEED]))

    def total(self) -> int:
        return sum(self.stats.values())

    def get_stat(self, stat: Stat) -> int:
        try:
            return self.stats[stat]
        except KeyError:
            raise StatError(f"Base stats do no have the requested stat: {stat}")

    @classmethod
    def from_json(cls, obj: dict, **kwargs) -> BaseStats:
        return BaseStats(attack=obj[Stat.ATTACK.name],
                         defense=obj[Stat.DEFENSE.name],
                         special_attack=obj[Stat.SP_ATTACK.name],
                         special_defense=obj[Stat.SP_DEFENSE.name],
                         speed=obj[Stat.SPEED.name],
                         hp=obj[Stat.HP.name])

    def to_json(self) -> JSONObject:
        return {stat.name: self.get_stat(stat) for stat in NUMBER_STATS}


#


class StatModifier(JSONModel):
    stat: Stat
    modifier: int

    def __init__(self, stat: Stat, modifier: int, adjust_to_cap: bool = False):
        mod_min = -6 if stat != Stat.CRITICAL else 0
        mod_max = 6 if stat != Stat.CRITICAL else 3
        if stat == stat.HP or (not adjust_to_cap and not (mod_min <= modifier <= mod_max)):
            raise StatError(f"Invalid stat modifier: {stat} | {modifier}")
        modifier = mod_min if modifier < mod_min else mod_max if modifier > mod_max else modifier
        super().__init__(stat=stat, modifier=modifier)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, StatModifier) and self.stat == o.stat and self.modifier == o.modifier

    def __hash__(self) -> int:
        return hash((self.stat, self.modifier))

    @property
    def multiplier(self) -> float:
        if self.stat not in NUMBER_STATS:
            raise NotImplemented()
        if self.modifier >= 0:
            return (2 + self.modifier) / 2
        else:
            return 2 / (2 + self.modifier)


#

EV_MAX = 252


class EV(JSONModel):
    stat: Stat
    value: int

    def __init__(self, stat: Stat, value: int, round_off: bool = False):
        if stat not in NUMBER_STATS:
            raise StatError(f"Cannot apply EVs to stat '{stat}'.")
        if (not round_off and value % 4 != 0) or not (0 <= value <= EV_MAX):
            raise StatError(f"Invalid EV value: {value}")
        value = value if not round_off else ((value // 4) * 4)
        super().__init__(stat=stat, value=value)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, EV) and self.stat == o.stat and self.value == o.value

    def __hash__(self) -> int:
        return hash((self.stat, self.value))


IV_MAX = 31


class IV(JSONModel):
    stat: Stat
    value: int

    def __init__(self, stat: Stat, value: int):
        if stat not in NUMBER_STATS:
            raise StatError(f"Cannot apply IVs to stat '{stat}'.")
        if not 0 <= value <= IV_MAX:
            raise StatError(f"Invalid IV value: {value}")
        super().__init__(stat=stat, value=value)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, IV) and self.stat == o.stat and self.value == o.value

    def __hash__(self) -> int:
        return hash((self.stat, self.value))


NATURE_MAP = {
    (Stat.ATTACK, Stat.ATTACK): "Hardy",
    (Stat.ATTACK, Stat.DEFENSE): "Lonely",
    (Stat.ATTACK, Stat.SP_ATTACK): "Adamant",
    (Stat.ATTACK, Stat.SP_DEFENSE): "Naughty",
    (Stat.ATTACK, Stat.SPEED): "Brave",
    (Stat.DEFENSE, Stat.ATTACK): "Bold",
    (Stat.DEFENSE, Stat.DEFENSE): "Docile",
    (Stat.DEFENSE, Stat.SP_ATTACK): "Impish",
    (Stat.DEFENSE, Stat.SP_DEFENSE): "Lax",
    (Stat.DEFENSE, Stat.SPEED): "Relaxed",
    (Stat.SP_ATTACK, Stat.ATTACK): "Modest",
    (Stat.SP_ATTACK, Stat.DEFENSE): "Mild",
    (Stat.SP_ATTACK, Stat.SP_ATTACK): "Bashful",
    (Stat.SP_ATTACK, Stat.SP_DEFENSE): "Rash",
    (Stat.SP_ATTACK, Stat.SPEED): "Quiet",
    (Stat.SP_DEFENSE, Stat.ATTACK): "Calm",
    (Stat.SP_DEFENSE, Stat.DEFENSE): "Gentle",
    (Stat.SP_DEFENSE, Stat.SP_ATTACK): "Careful",
    (Stat.SP_DEFENSE, Stat.SP_DEFENSE): "Quirky",
    (Stat.SP_DEFENSE, Stat.SPEED): "Sassy",
    (Stat.SPEED, Stat.ATTACK): "Timid",
    (Stat.SPEED, Stat.DEFENSE): "Hasty",
    (Stat.SPEED, Stat.SP_ATTACK): "Jolly",
    (Stat.SPEED, Stat.SP_DEFENSE): "Naive",
    (Stat.SPEED, Stat.SPEED): "Serious"
}

NATURE_MAP_REVERSED: dict[str, tuple[Stat, Stat]] = {v.upper(): k for k, v in NATURE_MAP.items()}


class _NatureMeta(ABCMeta):
    Hardy: Nature
    Lonely: Nature
    Adamant: Nature
    Naughty: Nature
    Brave: Nature
    Bold: Nature
    Docile: Nature
    Impish: Nature
    Lax: Nature
    Relaxed: Nature
    Modest: Nature
    Mild: Nature
    Bashful: Nature
    Rash: Nature
    Quiet: Nature
    Calm: Nature
    Gentle: Nature
    Careful: Nature
    Quirky: Nature
    Sassy: Nature
    Timid: Nature
    Hasty: Nature
    Jolly: Nature
    Naive: Nature
    Serious: Nature

    def __getattribute__(self, item):
        if isinstance(item, str) and item.upper() in NATURE_MAP_REVERSED:
            return Nature(*NATURE_MAP_REVERSED[item.upper()])
        return super().__getattribute__(item)


class Nature(JSONConvertible, metaclass=_NatureMeta):

    def __init__(self, plus_stat: Stat, minus_stat: Stat):
        for s in (plus_stat, minus_stat):
            if s not in NUMBER_STATS or s == Stat.HP:
                raise StatError(f"Invalid stat for nature: '{s}'")
        self._plus_stat = plus_stat
        self._minus_stat = minus_stat

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Nature) and self._plus_stat == o._plus_stat and self._minus_stat == o._minus_stat

    def __hash__(self) -> int:
        return hash((self._plus_stat, self._minus_stat))

    def __str__(self) -> str:
        return f"{self.name}: +{self._plus_stat}, -{self._minus_stat}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        return NATURE_MAP[(self._plus_stat, self._minus_stat)]

    def get_modifier(self, stat: Stat) -> float:
        if self.is_boosting(stat):
            return 1.1
        elif self.is_hindering(stat):
            return 0.9
        else:
            return 1

    def is_boosting(self, stat: Stat) -> bool:
        return self._plus_stat == stat and self._minus_stat != stat

    def is_hindering(self, stat: Stat) -> bool:
        return self._minus_stat == stat and self._plus_stat != stat

    def get_mod_as_string(self, stat: Stat) -> str:
        if self.is_boosting(stat):
            return f"Boosting"
        elif self.is_hindering(stat):
            return f"Hindering"
        else:
            return f"Neutral"

    @classmethod
    def build_boosting(cls, stat: Stat) -> Nature:
        if stat == Stat.HP:
            return cls.build_neutral()
        return Nature(stat, Stat.ATTACK if stat != Stat.ATTACK else Stat.SP_ATTACK)

    @classmethod
    def build_hindering(cls, stat: Stat) -> Nature:
        if stat == Stat.HP:
            return cls.build_neutral()
        return Nature(Stat.ATTACK if stat != Stat.ATTACK else Stat.SP_ATTACK, stat)

    @classmethod
    def build_neutral(cls) -> Nature:
        return Nature(Stat.ATTACK, Stat.ATTACK)

    @classmethod
    def from_json(cls, obj: dict, **kwargs) -> Nature:
        return Nature(plus_stat=Stat(obj["plus"]),
                      minus_stat=Stat(obj["minus"]))

    def to_json(self) -> dict:
        return {
            "plus": self._plus_stat.name,
            "minus": self._minus_stat.name,
            "name": self.name
        }


#


class Stats(JSONModel):
    base: BaseStats
    evs: dict[Stat, int]
    ivs: dict[Stat, int]
    level: int
    nature: Nature
    modifiers: dict[Stat, int] = {}

    @classmethod
    def of(cls, base: BaseStats,
           evs: Iterable[EV],
           ivs: Iterable[IV],
           nature: Nature,
           level: int,
           modifiers: Iterable[StatModifier] | None = None):
        return Stats(base=base,
                     evs={**{stat: 0 for stat in NUMBER_STATS},
                          **{ev.stat: ev.value for ev in evs}},
                     ivs={**{stat: IV_MAX for stat in NUMBER_STATS},
                          **{iv.stat: iv.value for iv in ivs}},
                     nature=nature,
                     level=level,
                     modifiers={m.stat: m.modifier for m in (modifiers or [])})

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Stats) and \
            self.base == o.base and \
            self.evs == o.evs and \
            self.ivs == o.ivs and \
            self.level == o.level and \
            self.nature == o.nature and \
            self.modifiers == o.modifiers

    def __hash__(self) -> int:
        return hash((self.base,
                     tuple((s, self.evs[s]) for s in NUMBER_STATS),
                     tuple((s, self.ivs[s]) for s in NUMBER_STATS),
                     self.level,
                     self.nature,
                     tuple((s, self.modifiers.get(s, None)) for s in Stat)))

    def __str__(self) -> str:
        return f"{self.base} | " \
               f"EVS = {', '.join('%s: %s' % (s, v) for s, v in self.evs.items() if v != 0)} | " \
               f"IVS {', '.join('%s: %s' % (s, v) for s, v in self.ivs.items() if v != IV_MAX)} | " \
               f"Level = {self.level} | " \
               f"Nature = {self.nature} | " \
               f"{', '.join('%s: %s%s' % (s, '+' if m >= 0 else '', m) for s, m in self.modifiers.items())}"

    def __repr__(self) -> str:
        return str(self)

    def get_iv(self, stat: Stat) -> int:
        StatError.check_number_stat(stat)
        return self.ivs[stat]

    def set_iv(self, iv: IV):
        self.ivs[iv.stat] = iv.value

    def get_ev(self, stat: Stat) -> int:
        StatError.check_number_stat(stat)
        return self.evs[stat]

    def set_ev(self, ev: EV):
        self.ivs[ev.stat] = ev.value

    def get_modifier(self, stat: Stat, minimum: int | None = None, maximum: int | None = None) -> StatModifier:
        m = self.modifiers.get(stat, 0)
        if minimum is not None and m < minimum:
            return StatModifier(stat, minimum)
        elif maximum is not None and m > maximum:
            return StatModifier(stat, maximum)
        return StatModifier(stat, m)

    def add_modifiers(self, *stat_mods: StatModifier):
        for stat_mod in stat_mods:
            self.modifiers[stat_mod.stat] = \
                StatModifier(stat_mod.stat,
                             (self.modifiers[stat_mod.stat]
                              if stat_mod.stat in self.modifiers else 0) + stat_mod.modifier,
                             adjust_to_cap=True).modifier
