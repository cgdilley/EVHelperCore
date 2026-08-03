from __future__ import annotations

from enum import Enum
from typing import Iterator

from SprelfJSON import JSONModel


class Regulation(Enum):
    M_A = "M-A"
    M_B = "M-B"


class Regulations(JSONModel):
    regulations: set[Regulation]

    def __contains__(self, item) -> bool:
        if isinstance(item, Regulation):
            return item in self.regulations
        if isinstance(item, str):
            try:
                return Regulation(item) in self.regulations
            except ValueError:
                try:
                    return Regulation[item] in self.regulations
                except ValueError:
                    pass
        return False

    def __len__(self) -> int:
        return len(self.regulations)

    def __iter__(self) -> Iterator[Regulation]:
        return iter(self.regulations)



