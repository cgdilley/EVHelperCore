from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class IJsonable(ABC):

    @abstractmethod
    def to_json(self) -> dict: ...

    @classmethod
    def to_json_or_default(cls, o: Optional[IJsonable], default: Optional[dict] = None) -> dict:
        return o.to_json() if o is not None else default


class IJsonExchangeable(IJsonable, ABC):

    @classmethod
    @abstractmethod
    def from_json(cls, obj: dict) -> IJsonExchangeable: ...
