from __future__ import annotations

from SprelfJSON import JSONModel

from .Regulations import Regulation, Regulations


class CompetitiveInfo(JSONModel):
    regulations: Regulations

    @classmethod
    def empty(cls) -> CompetitiveInfo:
        return CompetitiveInfo(regulations=Regulations(regulations=set()))
