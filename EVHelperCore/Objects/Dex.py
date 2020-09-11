from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable

from enum import Enum
from typing import Dict, Optional


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
    NATIONAL = "National"


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
