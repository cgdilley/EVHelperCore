from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable
from EVHelperCore.Exceptions import LocalizationError

from EVHelperCore.Utils.DictUtils import pop_field

from typing import Dict, Optional
from abc import ABC, abstractmethod

DEFAULT_LANGUAGE = "en"


#


class _NameBase(IJsonExchangeable, ABC):
    """
    Base class for Name objects, representing a "default" name (usually English) and localized versions of that name.
    """

    def __init__(self, default_name: str,
                 localized_names: Dict[str, str]):
        self._default_name: str = default_name
        self._localized_names: Dict[str, str] = localized_names

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self):
        return self.localized_name()

    def localized_name(self, language: str = None):
        try:
            return self._default_name if language is None or language == DEFAULT_LANGUAGE \
                else self._localized_names[language]
        except KeyError:
            raise LocalizationError.for_lang(language)

    def to_json(self) -> dict:
        return {
            "default": self._default_name,
            "localized": self._localized_names
        }

    @staticmethod
    def _parse_json(obj: dict) -> dict:
        return {
            "default_name": obj["default"],
            "localized_names": obj["localized"],
            **{k: v for k, v in obj.items() if k not in ["default", "localized"]}
        }


#


class VariantName(_NameBase, ABC):
    """
    Base class for the name of the particular variant of a Pokémon that gets appended or prepended to
    a particular Pokémon's base name.
    Eg. Mega Blaziken -> base name = Blaziken, variant name = Mega
    """

    def __init__(self, default_name: str, localized_names: Dict[str, str],
                 spacer: str = " "):
        super(VariantName, self).__init__(default_name, localized_names)
        self.spacer = spacer

    @abstractmethod
    def apply_variant_name(self, root_name: str, language: str) -> str:
        ...

    @classmethod
    def from_json(cls, obj: dict) -> VariantName:
        t = pop_field(obj, "type", default=None)
        if t is None or t == "prefix":
            return PrefixVariantName.from_json(obj)
        elif t == "suffix":
            return SuffixVariantName.from_json(obj)
        elif t == "circumfix":
            return CircumfixVariantName.from_json(obj)
        else:
            raise Exception(f"Invalid variant name type '{t}'.")

    def to_json(self) -> dict:
        return super().to_json() if self.spacer == " " else {**super().to_json(), "spacer": self.spacer}


#


class PrefixVariantName(VariantName):
    """
    A variant name that gets attached to the start of the Pokémon's name
    """

    def apply_variant_name(self, root_name: str, language: str = None) -> str:
        return f"{self.localized_name(language)}{self.spacer}{root_name}"

    @classmethod
    def from_json(cls, obj: dict) -> PrefixVariantName:
        return PrefixVariantName(**cls._parse_json(obj))

    def to_json(self) -> dict:
        return {**super().to_json(), "type": "prefix"}


class SuffixVariantName(VariantName):
    """
    A variant name that gets attached to the end of the Pokémon's name
    """

    def __init__(self, default_name: str,
                 localized_names: Dict[str, str],
                 spacer: str = " ",
                 comma: bool = False):
        super(SuffixVariantName, self).__init__(default_name, localized_names, spacer)
        self.comma = "," if comma else ""

    def apply_variant_name(self, root_name: str, language: str) -> str:
        return f"{root_name}{self.comma}{self.spacer}{self.localized_name(language)}"

    @classmethod
    def from_json(cls, obj: dict) -> SuffixVariantName:
        return SuffixVariantName(**cls._parse_json(obj))

    def to_json(self) -> dict:
        j = {**super().to_json(), "type": "suffix"}
        if self.comma == ",":
            j["comma"] = True
        return j


#


class CircumfixVariantName(VariantName):
    """
    A variant name that gets attached before and after the Pokémon's name
    """

    def __init__(self, default_prefix: str,
                 default_suffix: str,
                 localized_prefix: Dict[str, str],
                 localized_suffix: Dict[str, str],
                 prefix_comma: bool = False,
                 suffix_comma: bool = False,
                 prefix_spacer: str = " ",
                 suffix_spacer: str = " "):
        self._default_prefix = default_prefix
        self._default_suffix = default_suffix
        self._localized_prefix = localized_prefix
        self._localized_suffix = localized_suffix
        self.prefix_comma = "," if prefix_comma else ""
        self.suffix_comma = "," if suffix_comma else ""
        self.prefix_spacer = prefix_spacer
        self.suffix_spacer = suffix_spacer
        super(CircumfixVariantName, self).__init__(
            default_name=f"{self._default_prefix} {self._default_suffix}",
            localized_names={lang: f"{prefix} {self._localized_suffix[lang]}"
                             for prefix, lang in self._localized_prefix.items() if lang in self._localized_suffix})

    def localized_prefix(self, language: str = None):
        try:
            return self._default_prefix if language is None or language == DEFAULT_LANGUAGE \
                else self._localized_prefix[language]
        except KeyError:
            raise LocalizationError.for_lang(language)

    def localized_suffix(self, language: str = None):
        try:
            return self._default_suffix if language is None or language == DEFAULT_LANGUAGE \
                else self._localized_suffix[language]
        except KeyError:
            raise LocalizationError.for_lang(language)

    #

    def apply_variant_name(self, root_name: str, language: str) -> str:
        return f"{self.localized_prefix(language)}{self.prefix_comma}{self.prefix_spacer}" \
               f"{root_name}{self.suffix_comma}{self.suffix_spacer}{self.localized_suffix(language)}"

    @classmethod
    def from_json(cls, obj: dict) -> CircumfixVariantName:
        return CircumfixVariantName(**obj)

    def to_json(self) -> dict:
        j = {"type": "circumfix",
             "default_prefix": self._default_prefix, "localized_prefix": self._localized_prefix,
             "default_suffix": self._default_suffix, "localized_suffix": self._localized_suffix}
        if self.prefix_comma == ",":
            j["prefix_comma"] = True
        if self.suffix_comma == ",":
            j["suffix_comma"] = True
        if self.prefix_spacer != " ":
            j["prefix_spacer"] = self.prefix_spacer
        if self.suffix_spacer != " ":
            j["suffix_spacer"] = self.suffix_spacer
        return j


#


class Name(_NameBase):
    """
    The textual name of a particular Pokémon, including that Pokémon's base name and any variant names for
    that Pokémon.
    Eg. Mega Blaziken -> base name = Blaziken, variant name = Mega
    """

    def __init__(self, default_name: str,
                 localized_names: Dict[str, str],
                 variant_name: Optional[VariantName] = None):
        super(Name, self).__init__(default_name=default_name, localized_names=localized_names)
        self.variant_name: Optional[VariantName] = variant_name

    @property
    def name(self):
        return self.full_name()

    def base_name(self, language: str = None):
        return self.localized_name(language)

    def full_name(self, language: str = None):
        name = self.localized_name(language)
        return self.variant_name.apply_variant_name(name, language) if self.variant_name else name

    @classmethod
    def from_json(cls, obj: dict) -> Name:
        parsed = cls._parse_json(obj)
        variant = VariantName.from_json(pop_field(parsed, "variant")) if "variant" in obj else None
        return Name(**{**parsed, "variant_name": variant})

    def to_json(self) -> dict:
        j = super().to_json()
        if self.variant_name:
            j["variant"] = self.variant_name.to_json()
        return j
