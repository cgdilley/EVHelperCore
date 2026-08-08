from __future__ import annotations

from SprelfPkmn.Objects import Move


#


class StatusMove(Move):

    def __str__(self) -> str:
        return f"[{type(self).__name__}] {self.name} : {self.type.name.capitalize()}"