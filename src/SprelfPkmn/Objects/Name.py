from __future__ import annotations

from SprelfPkmn.Exceptions import LocalizationError

from abc import ABC, abstractmethod

from SprelfJSON import JSONModel

DEFAULT_LANGUAGE = "en"


#


class _NameBase(JSONModel, ABC):
    """
    Base class for Name objects, representing a "default" name (usually English) and localized versions of that name.
    """
    default: str
    localized: dict[str, str] = {}

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self):
        return self.localized_name()

    def localized_name(self, language: str = None):
        try:
            return self.default if language is None or language == DEFAULT_LANGUAGE \
                else self.localized[language]
        except KeyError:
            raise LocalizationError.for_lang(language)


#


class VariantName(_NameBase, ABC):
    """
    Base class for the name of the particular variant of a Pokémon that gets appended or prepended to
    a particular Pokémon's base name.
    Eg. Mega Blaziken -> base name = Blaziken, variant name = Mega
    """
    spacer: str = " "
    __name_field__ = "type"
    __name_field_required__ = True
    __include_name_in_json_output__ = True

    @abstractmethod
    def apply_variant_name(self, root_name: str, language: str) -> str:
        ...


#


class AffixVariantName(VariantName, ABC):
    comma: bool = False

    def get_comma(self) -> str:
        return "," if self.comma else ""



class PrefixVariantName(AffixVariantName):
    """
    A variant name that gets attached to the start of the Pokémon's name
    """

    def apply_variant_name(self, root_name: str, language: str = None) -> str:
        return f"{self.localized_name(language)}{self.spacer}{root_name}"

    @classmethod
    def model_identity(cls) -> str:
        return "prefix"


class SuffixVariantName(AffixVariantName):
    """
    A variant name that gets attached to the end of the Pokémon's name
    """
    comma: bool = False

    def apply_variant_name(self, root_name: str, language: str) -> str:
        return f"{root_name}{self.get_comma()}{self.spacer}{self.localized_name(language)}"

    @classmethod
    def model_identity(cls) -> str:
        return "suffix"

#


class CircumfixVariantName(VariantName):
    """
    A variant name that gets attached before and after the Pokémon's name
    """
    prefix: PrefixVariantName
    suffix: SuffixVariantName
    default: str = ""

    def apply_variant_name(self, root_name: str, language: str) -> str:
        return f"{self.prefix.localized_name(language)}{self.prefix.get_comma()}{self.prefix.spacer}" \
               f"{root_name}{self.suffix.get_comma()}{self.suffix.spacer}{self.suffix.localized_name(language)}"

    @classmethod
    def model_identity(cls) -> str:
        return "circumfix"



#


class Name(_NameBase):
    """
    The textual name of a particular Pokémon, including that Pokémon's base name and any variant names for
    that Pokémon.
    Eg. Mega Blaziken -> base name = Blaziken, variant name = Mega
    """
    variant: VariantName | None = None
    __include_name_in_json_output__ = False
    __name_field_required__ = False

    @property
    def name(self):
        return self.full_name()

    def base_name(self, language: str = None):
        return self.localized_name(language)

    def full_name(self, language: str = None):
        name = self.localized_name(language)
        return self.variant.apply_variant_name(name, language) if self.variant else name

