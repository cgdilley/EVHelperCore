from __future__ import annotations

from enum import Enum
from typing import Optional

from SprelfJSON import JSONModel


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
    HISUI = "HISUI"
    PALDEA = "PALDEA"

    @staticmethod
    def parse_descriptor(s: str) -> Region:
        return {
            "Galarian": Region.GALAR,
            "Alolan": Region.ALOLA,
            "Hisuian": Region.HISUI,
            "Paldean": Region.PALDEA
        }[s]

    @staticmethod
    def is_region_descriptor(s: str) -> bool:
        return s in ("Galarian", "Alolan", "Hisuian", "Paldean")

    def region_descriptor(self) -> Optional[str]:
        c = {
            Region.ALOLA: "Alolan",
            Region.GALAR: "Galarian",
            Region.HISUI: "Hisuian",
            Region.PALDEA: "Paldean"
        }
        return c[self] if self in c else None


class MegaType(Enum):
    NONE = "NONE"
    NORMAL = "NORMAL"
    X = "X"
    Y = "Y"


class Variant(JSONModel):
    """
    Describes the particular variant of a Pokémon.  There are four categories of variants:

    1. Region: A regional variant (eg. Alolan Ninetales)
    2. Gender: A variant determined by the gender (eg. Indeedee female/male)
    3. Mega: A mega form, with distinctions made for Mega X and Mega Y variants (eg. Mega Mewtwo X, Mega Mewtwo Y)
    4. Form: All other species-specific variants (eg. Rotom-Heat)

    If representing a Pokémon that is not a variant but rather the base version of that Pokémon, then all of these
    categories will have their default values (eg. Region.NONE).  See is_base_variant()
    """
    region: Region = Region.NONE
    gender: Gender = Gender.IRRELEVANT
    mega_type: MegaType = MegaType.NONE
    form: Optional[str] = None



    def __eq__(self, other: Variant) -> bool:
        return other is not None and \
               self.region == other.region and \
               self.gender == other.gender and \
               self.mega_type == other.mega_type and \
               self.form == other.form

    def __hash__(self) -> int:
        return hash((self.region,
                     self.gender,
                     self.mega_type,
                     self.form))

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

    #

    def is_mega(self) -> bool:
        return self.mega_type != MegaType.NONE

    #

    def is_gender(self) -> bool:
        return self.gender != Gender.IRRELEVANT

    #

    def is_form(self) -> bool:
        return self.form is not None

    #

    def is_base_variant(self) -> bool:
        return not self.is_form() and not self.is_mega() and not self.is_gender() and not self.is_regional()

    #

    @classmethod
    def merge(cls, *variants: Variant) -> Variant:
        result = Variant()
        for v in variants:
            if v.is_form():
                result._form = v.form
            if v.is_mega():
                result._mega = v.mega_type
            if v.is_gender():
                result._gender = v.gender
            if v.is_regional():
                result._region = v.region
        return result
