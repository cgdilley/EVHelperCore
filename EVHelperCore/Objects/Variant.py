from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional


class Gender(Enum):
    IRRELEVANT = "IRRELEVANT"
    MALE = "MALE"
    FEMALE = "FEMALE"
    GENDERLESS = "GENDERLESS"


class Region(Enum):
    NONE = "NONE"
    KANTO = "KANTO"
    JOHTO = "JOHTO"
    HOENN = "HOENN"
    SINNOH = "SINNOH"
    UNOVA = "UNOVA"
    KALOS = "KALOS"
    ALOLA = "ALOLA"
    GALAR = "GALAR"

    @staticmethod
    def parse_descriptor(s: str) -> Region:
        return {
            "Galarian": Region.GALAR,
            "Alolan": Region.ALOLA
        }[s]

    @staticmethod
    def is_region_descriptor(s: str) -> bool:
        return s in ("Galarian", "Alolan")


class MegaType(Enum):
    NONE = "NONE"
    NORMAL = "NORMAL"
    X = "X"
    Y = "Y"


class Variant(IJsonExchangeable):

    def __init__(self,
                 region: Region = Region.NONE,
                 gender: Gender = Gender.IRRELEVANT,
                 mega_type: MegaType = MegaType.NONE,
                 form: Optional[str] = None):
        self._region = region
        self._gender = gender
        self._mega_type = mega_type
        self._form = form

    def __eq__(self, other: Variant) -> bool:
        return other is not None and \
               self._region == other._region and \
               self._gender == other._gender and \
               self._mega_type == other._mega_type and \
               self._form == other._form

    def __hash__(self) -> int:
        return hash((self._region,
                     self._gender,
                     self._mega_type,
                     self._form))

    def __str__(self) -> str:
        variations = [v for v in [
            str(self.region) if self.is_regional() else None,
            str(self.gender) if self.is_gender() else None,
            str(self.mega_type) if self.is_mega() else None,
            self.form if self.is_form() else None
        ] if v]
        return ", ".join(variations) if len(variations) > 0 else "None"

    def __repr__(self) -> str:
        return str(self)

    def is_regional(self) -> bool:
        return self.region != Region.NONE

    @property
    def region(self) -> Region:
        return self._region

    #

    def is_mega(self) -> bool:
        return self.mega_type != MegaType.NONE

    @property
    def mega_type(self) -> MegaType:
        return self._mega_type

    #

    def is_gender(self) -> bool:
        return self.gender != Gender.IRRELEVANT

    @property
    def gender(self) -> Gender:
        return self._gender

    #

    def is_form(self) -> bool:
        return self.form is not None

    @property
    def form(self) -> Optional[str]:
        return self._form

    @classmethod
    def from_json(cls, obj: dict) -> Variant:
        return Variant(region=Region(obj["region"]) if "region" in obj else Region.NONE,
                       mega_type=MegaType(obj["mega_type"]) if "mega_type" in obj else MegaType.NONE,
                       gender=Gender(obj["gender"]) if "gender" in obj else Gender.IRRELEVANT,
                       form=obj["form"] if "form" in obj else None)

    def to_json(self) -> dict:
        return {k: v for k, v in {
            "region": self.region.name if self.is_regional() else None,
            "mega_type": self.mega_type.name if self.is_mega() else None,
            "gender": self.gender.name if self.is_gender() else None,
            "form": self.form
        }.items() if v}

    #
