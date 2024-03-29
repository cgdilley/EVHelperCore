from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable

from enum import Enum
from typing import Dict, Optional
import itertools


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


class DexEntry(IJsonExchangeable):
    """
    Represents a particular Pokédex and Pokédex number
    """

    def __init__(self, dex: Dex, number: int):
        self.dex = dex
        self.number = number

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

    @classmethod
    def from_json(cls, obj: dict) -> IJsonExchangeable:
        return DexEntry(dex=Dex[obj["dex"]],
                        number=obj["num"])

    def to_json(self) -> dict:
        return {
            "dex": self.dex.name,
            "num": self.number
        }


class DexEntryCollection(IJsonExchangeable):
    """
    Represents a collection of Pokédex entries that a particular Pokémon is
    represented by.
    """

    def __init__(self, *entries: DexEntry):
        self.entries: Dict[Dex, DexEntry] = {
            e.dex: e
            for e in entries
        }

    def __str__(self) -> str:
        return " | ".join(str(e) for e in self.entries.values())

    def __repr__(self) -> str:
        return str(self)

    def __contains__(self, dex: Dex) -> bool:
        return dex in self.entries

    def __getitem__(self, dex: Dex) -> Optional[DexEntry]:
        return self.entries[dex] if dex in self.entries else None

    def add_entry(self, entry: DexEntry):
        self.entries[entry.dex] = entry

    def get_dex_num(self, dex: Dex) -> Optional[int]:
        return self.entries[dex].number if dex in self.entries else None

    @classmethod
    def from_json(cls, obj: dict) -> DexEntryCollection:
        return DexEntryCollection(*(DexEntry.from_json(e) for e in obj["entries"]))

    def to_json(self) -> dict:
        return {
            "entries": [e.to_json() for e in self.entries.values()]
        }
