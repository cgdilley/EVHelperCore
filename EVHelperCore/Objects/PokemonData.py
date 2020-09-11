from __future__ import annotations

from EVHelperCore.Objects.Name import Name
from EVHelperCore.Objects.Ability import Ability, AbilityList
from EVHelperCore.Objects.Type import Type, Typing
from EVHelperCore.Objects.Move import Move, MoveList
from EVHelperCore.Objects.Stats import Stats, BaseStats, Stat, NUMBER_STATS
from EVHelperCore.Objects.Variant import Variant
from EVHelperCore.Objects.Dex import DexEntry, DexEntryCollection, Dex
from EVHelperCore.Objects.MiscInfo import MiscInfo

from EVHelperCore.Interfaces import IJsonExchangeable

from EVHelperCore.Utils.DictUtils import add_or_append
from EVHelperCore.Utils.FormatUtils import format_name_as_id

from typing import Iterable, Dict, List, Iterator, Optional


class PokemonData(IJsonExchangeable):
    """
    Represents the baseline collection of attributes that defines a particular species and variant of a Pokémon.
    """

    def __init__(self,
                 name: Name,
                 variant: Variant,
                 typing: Typing,
                 stats: BaseStats,
                 abilities: AbilityList,
                 move_list: MoveList,
                 dex_entries: DexEntryCollection,
                 misc_info: MiscInfo,
                 name_id: Optional[str] = None,
                 base_id: Optional[str] = None):
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
        self.name_id = format_name_as_id(name, variant) if name_id is None else name_id
        self.base_id = format_name_as_id(name, None) if base_id is None else base_id
        self.name = name
        self.variant = variant
        self.typing = typing
        self.stats = stats
        self.abilities = abilities
        self.move_list = move_list
        self.dex_entries = dex_entries
        self.misc_info = misc_info

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def from_json(cls, obj: dict) -> PokemonData:
        return PokemonData(name=Name.from_json(obj["name"]),
                           variant=Variant.from_json(obj["variant"]),
                           typing=Typing.from_json(obj["typing"]),
                           stats=BaseStats.from_json(obj["stats"]),
                           abilities=AbilityList.from_json(obj["abilities"]),
                           move_list=MoveList.from_json(obj["move_list"]),
                           dex_entries=DexEntryCollection.from_json(obj["dex_entries"]),
                           misc_info=MiscInfo.from_json(obj["misc_info"]),
                           name_id=obj["name_id"] if "name_id" in obj else None)

    def to_json(self) -> dict:
        return {
            "name_id": self.name_id,
            "name": self.name.to_json(),
            "variant": self.variant.to_json(),
            "typing": self.typing.to_json(),
            "stats": self.stats.to_json(),
            "abilities": self.abilities.to_json(),
            "move_list": self.move_list.to_json(),
            "dex_entries": self.dex_entries.to_json(),
            "misc_info": self.misc_info.to_json()
        }


#


class PokemonDataMap(Iterable[PokemonData]):
    """
    An indexed collection of Pokémon data
    """

    def __init__(self, *data: PokemonData):
        self._items: List[PokemonData] = []
        self.name_map: Dict[str, List[PokemonData]] = dict()
        self.name_id_map: Dict[str, PokemonData] = dict()
        self.typing_map: Dict[Type, List[PokemonData]] = dict()
        self.stats_map: Dict[Stat, Dict[int, List[PokemonData]]] = \
            {s: dict() for s in NUMBER_STATS}
        self.ability_map: Dict[str, List[PokemonData]] = dict()
        self.nat_dex_map: Dict[int, List[PokemonData]] = dict()
        self.ev_yield_map: Dict[Stat, Dict[int, List[PokemonData]]] = \
            {s: dict() for s in NUMBER_STATS}
        self.add_all_data(data)

    def __iter__(self) -> Iterator[PokemonData]:
        return iter(self._items)

    def add_data(self, d: PokemonData):
        self._items.append(d)
        add_or_append(self.name_map, d.name.base_name(), d)
        self.name_id_map[d.name_id] = d
        for t in d.typing:
            add_or_append(self.typing_map, t, d)
        for stat, value in d.stats:
            add_or_append(self.stats_map[stat], value, d)
        for ability in d.abilities:
            add_or_append(self.ability_map, ability.name, d)
        dex_num = d.dex_entries.get_dex_num(Dex.NATIONAL)
        if dex_num is not None:
            add_or_append(self.nat_dex_map, dex_num, d)
        if d.misc_info.ev_yield:
            for stat, val in d.misc_info.ev_yield.yields.items():
                add_or_append(self.ev_yield_map[stat], val, d)

    def add_all_data(self, data: Iterable[PokemonData]):
        for d in data:
            self.add_data(d)

    def name(self, name: str) -> Iterable[PokemonData]:
        return self.name_map[name] if name in self.name_map else []

    def typing(self, t: Type) -> Iterable[PokemonData]:
        return self.typing_map[t] if t in self.typing_map else []

    def stat(self, s: Stat, val: int) -> Iterable[PokemonData]:
        return self.stats_map[s][val] if val in self.stats_map[s] else []

    def ability(self, ability: str) -> Iterable[PokemonData]:
        return self.ability_map[ability] if ability in self.ability_map else []

    def nat_dex_number(self, number: int) -> Iterable[PokemonData]:
        return self.nat_dex_map[number] if number in self.nat_dex_map else []

    def name_id(self, name_id: str) -> Optional[PokemonData]:
        return self.name_id_map[name_id] if name_id in self.name_id_map else None

    def ev_yield(self, stat: Stat, value: Optional[int] = None, strict: bool = False) \
            -> Iterable[PokemonData]:
        values = (value,) if value else (1, 2, 3)
        for val in values:
            if val in self.ev_yield_map[stat]:
                yield from (pd for pd in self.ev_yield_map[stat][val] if not strict or
                            len(pd.misc_info.ev_yield.yields) == 1)
