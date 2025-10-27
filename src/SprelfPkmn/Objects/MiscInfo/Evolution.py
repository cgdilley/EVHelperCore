from __future__ import annotations

from SprelfPkmn.Utils.DictUtils import unique_by

from abc import ABC, abstractmethod
from typing import Iterable
from tree_format import format_tree
import itertools

from SprelfJSON import JSONModel, JSONModelError


#



class EvolutionType(JSONModel, ABC):
    """
    Represents a particular means of evolution.
    """
    __name_field__ = "type"

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
    def model_identity(cls) -> str:
        return cls.evo_type()

    @classmethod
    def from_json(cls, obj: dict, **kwargs) -> EvolutionType:
        try:
            return super().from_json(obj, **kwargs)
        except JSONModelError:
            return UnknownEvolutionType()


#


class Evolution(JSONModel):
    """
    Represents a particular evolution from one Pokémon to another Pokémon by
    a particular means.
    """
    frm: str
    to: str
    evo: EvolutionType

    def __str__(self) -> str:
        return f"{self.frm} -> ({str(self.evo)}) -> {self.to}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Evolution) and \
            self.frm == o.frm and \
            self.to == o.to and \
            self.evo == o.evo

    def __hash__(self) -> int:
        return hash((self.frm, self.to, self.evo))


#


class EvolutionLine(JSONModel):
    """
    A node in a tree-type structure that represents the evolutionary line of a particular Pokémon.
    The value of the node is the string ID of the represented Pokémon.
    Each possible evolution is represented by a branch leading to a new evolution line (node).
    """
    pokemon_id: str
    evolutions: list[tuple[Evolution, EvolutionLine]] = []

    @classmethod
    def of(cls, pokemon_id: str, *evolutions: tuple[Evolution, EvolutionLine]):
        return cls(pokemon_id=pokemon_id, evolutions=list(evolutions))

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
    def from_json(cls, obj: dict, **kwargs) -> EvolutionLine:
        return EvolutionLine.of(obj["pokemon_id"],
                             *(
                                 (Evolution(frm=obj["pokemon_id"],
                                            to=evo_obj["result"]["pokemon_id"],
                                            evo=EvolutionType.from_json(evo_obj["evo"])),
                                  EvolutionLine.from_json(evo_obj["result"]))
                                 for evo_obj in obj.get("evolutions", [])
                             ))

    def to_json(self) -> dict:
        j = {"pokemon_id": self.pokemon_id}
        if len(self.evolutions) > 0:
            j["evolutions"] = [{
                "evo": evo_type.evo.to_json(),
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

        def _merge_internal(*_evo_lines: tuple[Evolution, EvolutionLine]) \
                -> Iterable[tuple[Evolution, EvolutionLine]]:
            for _evo, _evo_line in unique_by(_evo_lines, key=lambda t: (t[0], t[1].pokemon_id)):
                yield _evo, EvolutionLine(pokemon_id=_evo_line.pokemon_id,
                                          evolutions=list(_merge_internal(*_evo_line.evolutions)))
            # return (
            #     (evo, EvolutionLine(evo_line.pokemon_id, *_merge_internal(evo_line.evolutions)))
            #     for evo, evo_line in unique_by(_evo_lines, key=lambda t: (t[0], t[1].pokemon_id)))

        for evo_line in unique_by(evolution_lines, key=lambda e: e.pokemon_id):
            internal = _merge_internal(*((e, el) for _e in evolution_lines for e, el in _e.evolutions
                                         if _e.pokemon_id == evo_line.pokemon_id))
            yield EvolutionLine(pokemon_id=evo_line.pokemon_id,
                                evolutions=list(internal))
        # return \
        #     (EvolutionLine(
        #         evo.pokemon_id,
        #         *(_merge_internal(*((e, el) for _e in evolution_lines for e, el in _e.evolutions))))
        #         for evo in unique_by(evolution_lines, key=lambda e: e.pokemon_id))


#


class LevelUpEvolutionType(EvolutionType):
    """
    An evolution triggered by leveling to a particular level
    """
    level: int
    location: str | None = None

    def __str__(self) -> str:
        if self.location:
            return f"Level up at level {self.level} in {self.location}"
        return f"Level up at level {self.level}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, o: LevelUpEvolutionType) -> int:
        return isinstance(o, LevelUpEvolutionType) and \
            self.level == o.level and \
            self.location == o.location

    def __hash__(self) -> int:
        return hash((self.evo_type(), self.level, self.location))

    @classmethod
    def evo_type(cls) -> str:
        return "level_up"


#


class ItemEvolutionType(EvolutionType):
    """
    An evolution triggered by using a particular item
    """
    item: str

    def __str__(self) -> str:
        return f"Evolve by using {self.item}"

    def __eq__(self, o: EvolutionType) -> int:
        return isinstance(o, ItemEvolutionType) and self.item == o.item

    def __hash__(self) -> int:
        return hash((self.evo_type(), self.item))

    @classmethod
    def evo_type(cls) -> str:
        return "item"


#


class MoveKnowledgeEvolutionType(EvolutionType):
    """
    An evolution triggered by leveling up while knowing a particular move
    """
    move: str

    def __str__(self) -> str:
        return f"Level up after learning {self.move}"

    def __eq__(self, o: EvolutionType) -> int:
        return isinstance(o, MoveKnowledgeEvolutionType) and self.move == o.move

    def __hash__(self) -> int:
        return hash((self.evo_type(), self.move))

    @classmethod
    def evo_type(cls) -> str:
        return "move_known"


class TradingEvolutionType(EvolutionType):
    holding: str | None

    def __str__(self) -> str:
        if self.holding:
            return f"Trade while holding {self.holding}"
        return "Trade"

    def __eq__(self, o: EvolutionType) -> int:
        return isinstance(o, TradingEvolutionType) and o.holding == self.holding

    def __hash__(self) -> int:
        return hash((self.evo_type(), self.holding))

    @classmethod
    def evo_type(cls) -> str:
        return "trade"


class FriendshipEvolutionType(EvolutionType):

    def __str__(self) -> str:
        return "Friendship"

    def __eq__(self, o: EvolutionType) -> int:
        return isinstance(o, FriendshipEvolutionType)

    def __hash__(self) -> int:
        return hash(self.evo_type())

    @classmethod
    def evo_type(cls) -> str:
        return "friendship"


class UnknownEvolutionType(EvolutionType):

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
