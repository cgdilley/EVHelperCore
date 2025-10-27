from __future__ import annotations

from EVHelperCore.Objects.Name import Name
from EVHelperCore.Objects.Ability import Ability, AbilityList
from EVHelperCore.Objects.Type import Type, Typing
from EVHelperCore.Objects.Move import MoveList, MoveSet
from EVHelperCore.Objects.Stats import Stats, BaseStats, Stat, NUMBER_STATS
from EVHelperCore.Objects.Variant import Variant
from EVHelperCore.Objects.Dex import DexEntryCollection, Dex
from EVHelperCore.Objects.MiscInfo import MiscInfo

from typing import Iterable, Iterator

from SprelfJSON import JSONModel


class PokemonData(JSONModel):
    """
    Represents the baseline collection of attributes that defines a particular species and variant of a Pokémon.
    """
    """
    :param name: The textual name of the Pokémon, including the variant name
    :param variant: Information about the particular variant of the Pokémon (eg. regional, gender, etc.)
    :param typing: The typing of the Pokémon
    :param stats: The base stat totals for the Pokémon
    :param abilities: The abilities the Pokémon is able to have
    :param move_list: The moves that the Pokémon is able to learn
    :param dex_entries: The Pokédex entries that the Pokémon is represented by
    :param misc_info: Other assorted (optional) information about the Pokémon
    :param name_id: Optional.  The name ID of the Pokémon,
    if different than the one automatically generated based on name and variant.
    :param base_id: Optional.  The base name ID of the Pokémon, separate from any variant,
    if different than the one automatically generated based on the base name.
    """
    name: Name
    variant: Variant
    typing: Typing
    stats: BaseStats
    abilities: AbilityList
    move_list: MoveList
    dex_entries: DexEntryCollection
    misc_info: MiscInfo
    name_id: str | None = None,
    base_id: str | None = None

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return str(self)


#


class PokemonQueryable(Iterable[PokemonData]):

    def __init__(self, data: Iterable[PokemonData]):
        self._items: Iterable[PokemonData] = data

    def __iter__(self) -> Iterator[PokemonData]:
        return iter(self._items)

    def typing(self, t: Type) -> PokemonQueryable:
        return PokemonQueryable(x for x in self._items
                    if t in x.typing)

    def stat(self, s: Stat, val: int) -> PokemonQueryable:
        return PokemonQueryable(x for x in self._items
                if x.stats.get_stat(s) == val)

    def ability(self, ability: str) -> PokemonQueryable:
        return PokemonQueryable(x for x in self._items
                    if ability in x.abilities)

    def nat_dex_number(self, number: int) -> PokemonQueryable:
        return PokemonQueryable(x for x in self._items
                    if x.dex_entries.get_dex_num(Dex.NATIONAL) == number)

    def ev_yield(self, stat: Stat, value: int | None = None, strict: bool = False) \
            -> PokemonQueryable:
        values = (value,) if value else (1, 2, 3)
        return PokemonQueryable(x for x in self._items
                                if x.misc_info.ev_yield and
                                any(x.misc_info.ev_yield.get(stat) == val
                                       and (not strict or len(x.misc_info.ev_yield.yields) == 1)
                                       for val in values))

    def dex(self, dex: Dex) -> PokemonQueryable:
        return PokemonQueryable(x for x in self._items
                                if x.dex_entries.get_dex_num(dex) is not None)

    def is_mega(self, b: bool = True) -> PokemonQueryable:
        return PokemonQueryable(x for x in self._items
                                if x.variant.is_mega() == b)


class PokemonDataMap(PokemonQueryable):
    """
    An indexed collection of Pokémon data
    """

    def __init__(self, *data: PokemonData):
        super().__init__(data)
        self._items: list[PokemonData] = list(self._items)
        self.name_map: dict[str, list[PokemonData]] = dict()
        self.name_id_map: dict[str, PokemonData] = dict()
        self.typing_map: dict[Type, list[PokemonData]] = dict()
        self.stats_map: dict[Stat, dict[int, list[PokemonData]]] = \
            {s: dict() for s in NUMBER_STATS}
        self.ability_map: dict[str, list[PokemonData]] = dict()
        self.nat_dex_map: dict[int, list[PokemonData]] = dict()
        self.ev_yield_map: dict[Stat, dict[int, list[PokemonData]]] = \
            {s: dict() for s in NUMBER_STATS}
        self.dex_map: dict[Dex, list[PokemonData]] = dict()
        for d in self._items:
            self._index_item(d)

    def add_data(self, d: PokemonData):
        self._items.append(d)
        self._index_item(d)

    def add_all_data(self, data: Iterable[PokemonData]):
        for d in data:
            self.add_data(d)

    def _index_item(self, d: PokemonData):
        self.name_map.setdefault(d.name.base_name(), []).append(d)
        self.name_id_map[d.name_id] = d
        for t in d.typing:
            self.typing_map.setdefault(t, []).append(d)
        for stat, value in d.stats:
            self.stats_map[stat].setdefault(value, []).append(d)
        for ability in d.abilities:
            self.ability_map.setdefault(ability.name, []).append(d)
        for dex in d.dex_entries:
            self.dex_map.setdefault(dex.dex, []).append(d)
            if dex.dex == Dex.NATIONAL:
                self.nat_dex_map.setdefault(dex.number, []).append(d)
        if d.misc_info.ev_yield:
            for stat, val in d.misc_info.ev_yield.yields.items():
                self.ev_yield_map[stat].setdefault(val, []).append(d)

    def name(self, name: str) -> PokemonQueryable:
        return PokemonQueryable(self.name_map.get(name, []))

    def typing(self, t: Type) -> PokemonQueryable:
        return PokemonQueryable(self.typing_map.get(t, []))

    def stat(self, s: Stat, val: int) -> PokemonQueryable:
        return PokemonQueryable(self.stats_map[s].get(val, []))

    def ability(self, ability: str) -> PokemonQueryable:
        return PokemonQueryable(self.ability_map.get(ability, []))

    def nat_dex_number(self, number: int) -> PokemonQueryable:
        return PokemonQueryable(self.nat_dex_map.get(number, []))

    def name_id(self, name_id: str) -> PokemonData | None:
        return self.name_id_map.get(name_id, None)

    def ev_yield(self, stat: Stat, value: int | None = None, strict: bool = False) \
            -> PokemonQueryable:
        values = (value,) if value else (1, 2, 3)
        return PokemonQueryable(pd for val in values
                                if val in self.ev_yield_map[stat]
                                for pd in self.ev_yield_map[stat][val] if not strict or
                                len(pd.misc_info.ev_yield.yields) == 1)

    def dex(self, dex: Dex) -> PokemonQueryable:
        return PokemonQueryable(self.dex_map.get(dex, []))


#


class Pokemon(JSONModel):
    data: PokemonData
    moveset: MoveSet
    ability: Ability
    item: str
    stats: Stats
