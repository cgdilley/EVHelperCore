from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class IJsonable(ABC):

    @abstractmethod
    def to_json(self) -> dict:
        """
        Converts this object into a JSON object representing its contents
        """
        pass

    @classmethod
    def to_json_or_default(cls, o: Optional[IJsonable], default: Optional[dict] = None) -> Optional[dict]:
        """
        Attempts to convert the given JSONable object into a JSON object.  If the given object is None,
        returns the default value instead.

        :param o: The object to convert to JSON
        :param default: Optional.  The default value to return if the given object is None.  Defaults to None
        :return: The given object converted to JSON, or the given default value
        """
        return o.to_json() if o is not None else default


class IJsonExchangeable(IJsonable, ABC):

    @classmethod
    @abstractmethod
    def from_json(cls, obj: dict) -> IJsonExchangeable:
        """
        Parses the given JSON object, creating a new object with properties assigned based on the contents
        of that JSON object.
        """
        pass
