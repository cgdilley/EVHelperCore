from __future__ import annotations

from SprelfPkmn.Objects import Move, Type, DamageClass, Stat, MoveProperties
from SprelfPkmn.Implementations.Moves.DamagingMove import DamagingMove
from SprelfPkmn.Implementations.Moves.StatusMove import StatusMove
from typing import Iterator, Iterable, Collection
import json


#


class MoveQueryable(Iterable[Move]):

    def __init__(self, moves: Iterable[Move]):
        self._items: Iterable[Move] = moves

    def __iter__(self) -> Iterator[Move]:
        return iter(self._items)

    def to_list(self) -> list[Move]:
        self._items = list(self._items)
        return self._items

    def type(self, t: Type) -> MoveQueryable:
        return MoveQueryable(move for move in self._items if move.type == t)

    def base_power(self, *bp: int) -> MoveQueryable:
        return MoveQueryable(move for move in self._items if isinstance(move, DamagingMove) and move.base_power in bp)

    def damaging(self) -> MoveQueryable:
        return MoveQueryable(move for move in self._items if isinstance(move, DamagingMove))

    def status(self) -> MoveQueryable:
        return MoveQueryable(move for move in self._items if isinstance(move, StatusMove))

    def damage_class(self, dc: DamageClass) -> MoveQueryable:
        return MoveQueryable(move for move in self._items if isinstance(move, DamagingMove)
                             and move.damage_class == dc)

    def offense_stat(self, os: Stat) -> MoveQueryable:
        return MoveQueryable(move for move in self._items if isinstance(move, DamagingMove)
                             and move.offense_stat == os)

    def defense_stat(self, ds: Stat) -> MoveQueryable:
        return MoveQueryable(move for move in self._items if isinstance(move, DamagingMove)
                             and move.defense_stat == ds)

    def properties(self, p: MoveProperties) -> MoveQueryable:
        return MoveQueryable(move for move in self._items if (move.properties & p) == p)

    def priority(self, *p: int) -> MoveQueryable:
        return MoveQueryable(move for move in self._items if move.priority in p)

    def accuracy(self, *a: int) -> MoveQueryable:
        return MoveQueryable(move for move in self._items if move.accuracy in a)

    def max_pp(self, *pp: int) -> MoveQueryable:
        return MoveQueryable(move for move in self._items if move.max_pp in pp)


#


#


class MoveDataMap(MoveQueryable):

    def __init__(self, moves: Iterable[Move]):
        super().__init__(moves)

        self._item_list = []
        self.name_map: dict[str, Move] = {}
        self.category_map: dict[type[Move], list[Move]] = {}
        self.type_map: dict[Type, list[Move]] = {}
        self.base_power_map: dict[int, list[Move]] = {}
        self.offense_stat_map: dict[Stat, list[Move]] = {}
        self.defense_stat_map: dict[Stat, list[Move]] = {}
        self.damage_class_map: dict[DamageClass, list[Move]] = {}
        self.property_map: dict[MoveProperties, list[Move]] = {}
        self.add_moves(self._items)
        self._items = self._item_list

    def to_list(self) -> list[Move]:
        return self._item_list

    def add_move(self, m: Move):
        self._item_list.append(m)
        self._index_move(m)

    def add_moves(self, moves: Iterable[Move]):
        for m in moves:
            self.add_move(m)

    def _index_move(self, m: Move):
        self.name_map[m.name] = m
        self.type_map.setdefault(m.type, []).append(m)
        if isinstance(m, DamagingMove):
            self.category_map.setdefault(DamagingMove, []).append(m)
            self.base_power_map.setdefault(m.base_power, []).append(m)
            self.offense_stat_map.setdefault(m.offense_stat, []).append(m)
            self.defense_stat_map.setdefault(m.defense_stat, []).append(m)
            self.damage_class_map.setdefault(m.damage_class, []).append(m)
        elif isinstance(m, StatusMove):
            self.category_map.setdefault(StatusMove, []).append(m)

        for flag in m.properties:
            self.property_map.setdefault(flag, []).append(m)

    def name(self, name: str) -> Move | None:
        return self.name_map.get(name)

    def type(self, t: Type) -> MoveQueryable:
        return MoveQueryable(self.type_map.get(t, ()))

    def base_power(self, *bp: int) -> MoveQueryable:
        return MoveQueryable((x for val in bp for x in self.base_power_map.get(val, ())))

    def damaging(self) -> MoveQueryable:
        return MoveQueryable(self.category_map.get(DamagingMove, ()))

    def status(self) -> MoveQueryable:
        return MoveQueryable(self.category_map.get(StatusMove, ()))

    def damage_class(self, dc: DamageClass) -> MoveQueryable:
        return MoveQueryable(self.damage_class_map.get(dc, ()))

    def offense_stat(self, os: Stat) -> MoveQueryable:
        return MoveQueryable(self.offense_stat_map.get(os, ()))

    def defense_stat(self, ds: Stat) -> MoveQueryable:
        return MoveQueryable(self.defense_stat_map.get(ds, ()))

    def properties(self, p: MoveProperties) -> MoveQueryable:
        individual = list(iter(p))
        if len(individual) == 0:
            return self
        return MoveQueryable(m for m in self.property_map.get(individual[0], ()) if all(m.properties & p) == p)

    @classmethod
    def from_file(cls, path: str) -> MoveDataMap:
        with open(path, "r", encoding="utf-8") as f:
            return MoveDataMap(Move.from_json(json.loads(line)) for line in f)


