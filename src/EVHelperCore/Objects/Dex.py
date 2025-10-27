from __future__ import annotations

from enum import Enum
from typing import Optional, Iterator, Iterable, Collection
import itertools

from SprelfJSON import JSONModel


#


class Dex(Enum):
    """
    A particular Pokédex assigning Pokédex numbers to different Pokémon
    """
    GEN_1 = "Red/Blue/Yellow"
    GEN_2 = "Gold/Silver/Crystal"
    GEN_3 = "Ruby/Sapphire/Emerald"
    GEN_3_RM = "FireRed/LeafGreen"
    GEN_4 = "Diamond/Pearl"
    GEN_4_E = "Platinum"
    GEN_4_RM = "HeartGold/SoulSilver"
    GEN_5 = "Black/White"
    GEN_5_E = "Black 2/White 2"
    GEN_6 = "X/Y  Central Kalos"
    GEN_6_2 = "X/Y  Coastal Kalos"
    GEN_6_3 = "X/Y  Mountain Kalos"
    GEN_6_RM = "Omega Ruby/Alpha Sapphire"
    GEN_7 = "Sun/Moon  Alola dex"
    GEN_7_E = "U.Sun/U.Moon  Alola dex"
    GEN_7_LG = "Let's Go Pikachu/Let's Go Eevee"
    GEN_8 = "Sword/Shield"
    GEN_8_DLC1 = "The Isle of Armor"
    GEN_8_DLC2 = "The Crown Tundra"
    GEN_8_RM = "Brilliant Diamond/Shining Pearl"
    GEN_8_LEG = "Legends: Arceus"
    GEN_9 = "Scarlet/Violet"
    GEN_9_DLC1 = "The Teal Mask"
    GEN_9_DLC2 = "The Indigo Disk"
    GEN_9_LEG = "Legends: Z-A"
    NATIONAL = "National"

    @staticmethod
    def parse(s: str) -> Dex:
        try:
            return Dex(s)
        except ValueError:
            split = s.split("/")
            for perm in itertools.permutations(split):
                try:
                    return Dex("/".join(perm))
                except ValueError:
                    pass
            raise


class DexEntry(JSONModel):
    """
    Represents a particular Pokédex and Pokédex number
    """
    dex: Dex
    number: int

    def __str__(self) -> str:
        return f"{self.dex}: {self.number}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, DexEntry) and \
               self.dex == o.dex and \
               self.number == o.number

    def __hash__(self) -> int:
        return hash((self.dex, self.number))


class DexEntryCollection(JSONModel, Iterable[DexEntry]):
    """
    Represents a collection of Pokédex entries that a particular Pokémon is
    represented by.
    """
    entries: list[DexEntry] = []

    def __init__(self, entries: Collection[DexEntry]):
        super().__init__(entries=entries)
        self._dex_map: dict[Dex, DexEntry] = {d.dex: d for d in self.entries}

    def __str__(self) -> str:
        return " | ".join(str(e) for e in self.entries)

    def __repr__(self) -> str:
        return str(self)

    def __contains__(self, dex: Dex) -> bool:
        return dex in self.entries

    def __getitem__(self, dex: Dex) -> DexEntry:
        return self._dex_map[dex]

    def get(self, dex: Dex, default: DexEntry = None) -> DexEntry:
        return self._dex_map.get(dex, default)

    def __iter__(self) -> Iterator[DexEntry]:
        return iter(self.entries)

    def add_entry(self, entry: DexEntry):
        self._dex_map[entry.dex] = entry
        self.entries = list(self._dex_map.values())

    def get_dex_num(self, dex: Dex) -> Optional[int]:
        return self._dex_map[dex].number if dex in self._dex_map else None

    @classmethod
    def of(cls, *entries: DexEntry) -> DexEntryCollection:
        return cls(entries)
