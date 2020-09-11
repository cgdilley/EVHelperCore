from __future__ import annotations

from EVHelperCore.Interfaces import IJsonExchangeable, IJsonable
from EVHelperCore.Utils.DictUtils import get_or_default, unique_by

from enum import Enum
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Collection, Iterable, Union
from tree_format import format_tree
import itertools


#


class Evolution(IJsonExchangeable):
    """
    Represents a particular evolution from one Pokémon to another Pokémon by
    a particular means.
    """

    def __init__(self, from_id: str, to_id: str, evolution_type: EvolutionType):
        """
        :param from_id: The ID of the evolving Pokémon
        :param to_id: The ID of the Pokémon being evolved into
        :param evolution_type: The type of the evolution
        """
        self.from_id = from_id
        self.to_id = to_id
        self.evolution_type = evolution_type

    def __str__(self) -> str:
        return f"{self.from_id} -> ({str(self.evolution_type)}) -> {self.to_id}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Evolution) and \
               self.from_id == o.from_id and \
               self.to_id == o.to_id and \
               self.evolution_type == o.evolution_type

    def __hash__(self) -> int:
        return hash((self.from_id, self.to_id, self.evolution_type))

    @classmethod
    def from_json(cls, obj: dict) -> Evolution:
        return Evolution(obj["from"], obj["to"], EvolutionType.from_json(obj["evo"]))

    def to_json(self) -> dict:
        return {
            "from": self.from_id,
            "to": self.to_id,
            "evo": self.evolution_type.to_json()
        }


#


class EvolutionLine(IJsonExchangeable):
    """
    A node in a tree-type structure that represents the evolutionary line of a particular Pokémon.
    The value of the node is the string ID of the represented Pokémon.
    Each possible evolution is represented by a branch leading to a new evolution line (node).
    """

    def __init__(self, pokemon_id: str, *evolutions: Tuple[Evolution, EvolutionLine]):
        self.pokemon_id = pokemon_id
        self.evolutions: Collection[Tuple[Evolution, EvolutionLine]] = evolutions

    def __str__(self) -> str:
        return f"{self.pokemon_id} -> ({len(self.evolutions)} evolution(s))"

    def __repr__(self) -> str:
        return str(self)

    def render_tree(self) -> str:
        return format_tree(self, lambda e: e.pokemon_id, lambda e: (evo_line for evo, evo_line in e.evolutions))

    def get_next_evolutions(self) -> Iterable[EvolutionLine]:
        """
        Generates all evolution lines that this evolution line immediately leads to.
        """
        return (evo_line for evo, evo_line in self.evolutions)

    def get_next_evolution_ids(self) -> Iterable[str]:
        """
        Generates the IDs of all Pokémon that follow directly in this evolution line.
        """
        return (evo_line.pokemon_id for evo_line in self.get_next_evolutions())

    def get_final_evolution_ids(self) -> Iterable[str]:
        """
        Generates the IDs of all Pokémon that lie at the end of this evolution line and
        all evolution lines led to by this evolution line.
        """
        if len(self.evolutions) == 0:
            return self.pokemon_id,
        return (final for evo_line in self.get_next_evolutions() for final in evo_line.get_final_evolution_ids())

    def get_all_pokemon_ids_in_line(self) -> Iterable[str]:
        """
        Generates the IDs of all Pokémon involved in this evolution line and all
        evolution lines led to by this evolution line.
        """
        return itertools.chain((self.pokemon_id,), (p_id for evo_line in self.get_next_evolutions()
                                                    for p_id in evo_line.get_all_pokemon_ids_in_line()))

    @classmethod
    def from_json(cls, obj: dict) -> EvolutionLine:
        return EvolutionLine(obj["pokemon_id"],
                             *(
                                 (Evolution(from_id=obj["pokemon_id"],
                                            to_id=evo_obj["result"]["pokemon_id"],
                                            evolution_type=EvolutionType.from_json(evo_obj["evo"])),
                                  EvolutionLine.from_json(evo_obj["result"]))
                                 for evo_obj in get_or_default(obj, "evolutions", [])
                             ))

    def to_json(self) -> dict:
        j = {"pokemon_id": self.pokemon_id}
        if len(self.evolutions) > 0:
            j["evolutions"] = [{
                "evo": evo_type.evolution_type.to_json(),
                "result": evo_line.to_json()
            } for evo_type, evo_line in self.evolutions]
        return j

    @staticmethod
    def merge(*evolution_lines: EvolutionLine) -> Iterable[EvolutionLine]:
        """
        Merges the given evolution lines into unique evolution lines.

        :param evolution_lines: The evolution lines to merge.
        :return: A lazy generator for the unique, merged evolution lines
        """

        def _merge_internal(*_evo_lines: Tuple[Evolution, EvolutionLine]) \
                -> Iterable[Tuple[Evolution, EvolutionLine]]:
            for _evo, _evo_line in unique_by(_evo_lines, key=lambda t: (t[0], t[1].pokemon_id)):
                yield _evo, EvolutionLine(_evo_line.pokemon_id, *_merge_internal(*_evo_line.evolutions))
            # return (
            #     (evo, EvolutionLine(evo_line.pokemon_id, *_merge_internal(evo_line.evolutions)))
            #     for evo, evo_line in unique_by(_evo_lines, key=lambda t: (t[0], t[1].pokemon_id)))

        for evo_line in unique_by(evolution_lines, key=lambda e: e.pokemon_id):
            internal = _merge_internal(*((e, el) for _e in evolution_lines for e, el in _e.evolutions
                                         if _e.pokemon_id == evo_line.pokemon_id))
            yield EvolutionLine(evo_line.pokemon_id, *internal)
        # return \
        #     (EvolutionLine(
        #         evo.pokemon_id,
        #         *(_merge_internal(*((e, el) for _e in evolution_lines for e, el in _e.evolutions))))
        #         for evo in unique_by(evolution_lines, key=lambda e: e.pokemon_id))


#


class EvolutionType(IJsonExchangeable, ABC):
    """
    Represents a particular means of evolution.
    """

    @abstractmethod
    def __str__(self) -> str:
        ...

    @abstractmethod
    def __eq__(self, o: EvolutionType) -> int:
        ...

    @abstractmethod
    def __hash__(self) -> int:
        ...

    @classmethod
    @abstractmethod
    def evo_type(cls) -> str:
        ...

    @classmethod
    @abstractmethod
    def from_json(cls, obj: dict) -> EvolutionType:
        for t in [LevelUpEvolutionType, UnknownEvolutionType, ItemEvolutionType]:
            if obj["type"] == t.evo_type():
                return t.from_json(obj)
        return UnknownEvolutionType()

    @abstractmethod
    def to_json(self) -> dict:
        return {"type": self.evo_type()}


#


class LevelUpEvolutionType(EvolutionType):
    """
    An evolution triggered by leveling to a particular level
    """

    def __init__(self, level: int):
        """
        :param level: The level that triggers evolution
        """
        self.level = level

    def __str__(self) -> str:
        return f"Level up at level {self.level}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, o: LevelUpEvolutionType) -> int:
        return isinstance(o, LevelUpEvolutionType) and \
               self.level == o.level

    def __hash__(self) -> int:
        return hash((self.evo_type(), self.level))

    @classmethod
    def evo_type(cls) -> str:
        return "level_up"

    @classmethod
    def from_json(cls, obj: dict) -> LevelUpEvolutionType:
        return LevelUpEvolutionType(obj["level"])

    def to_json(self) -> dict:
        return {
            **super().to_json(),
            "level": self.level
        }


#


class ItemEvolutionType(EvolutionType):
    """
    An evolution triggered by using a particular item
    """

    def __init__(self, item: str):
        """
        :param item: The item used to trigger evolution
        """
        self.item = item

    def __str__(self) -> str:
        return f"Level up by using {self.item}"

    def __eq__(self, o: EvolutionType) -> int:
        return isinstance(o, ItemEvolutionType) and self.item == o.item

    def __hash__(self) -> int:
        return hash((self.evo_type(), self.item))

    @classmethod
    def evo_type(cls) -> str:
        return "item"

    @classmethod
    def from_json(cls, obj: dict) -> EvolutionType:
        return ItemEvolutionType(obj["item"])

    def to_json(self) -> dict:
        return {
            **super().to_json(),
            "level": self.item
        }


#


class UnknownEvolutionType(EvolutionType):

    def __init__(self):
        pass

    def __str__(self) -> str:
        return f"Unknown evolution"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, o: UnknownEvolutionType) -> int:
        return isinstance(o, UnknownEvolutionType)

    def __hash__(self) -> int:
        return hash(self.evo_type())

    @classmethod
    def evo_type(cls) -> str:
        return "unknown"

    @classmethod
    def from_json(cls, obj: dict) -> UnknownEvolutionType:
        return UnknownEvolutionType()

    def to_json(self) -> dict:
        return super().to_json()
