
from typing import Hashable, TypeVar, Iterable, Callable

from SprelfJSON import JSONConvertible

T = TypeVar('T')
TJSONConvertible = TypeVar('TJSONConvertible', bound=JSONConvertible)
H = TypeVar('H', bound=Hashable)


#


def from_json_or_default(t: type[TJSONConvertible],
                         d: dict[H, dict],
                         key: H,
                         default: TJSONConvertible | None = None) -> TJSONConvertible | None:
    """
    For a dictionary mapping keys to JSON objects representing a JSONConvertible object, extract
    the JSON from the given key and convert it into the specified JSONConvertible type using that type's
    .from_json() method.  If the given key is not found in the given dictionary, returns the
    given default value instead.

    :param t: The JSONConvertible type to parse the JSON as.
    :param d: The dictionary mapping keys to JSONConvertible JSON representations
    :param key: The key to extract the JSON from
    :param default: Optional.  The default value to return if the given key is not found in the given dictionary.
    Defaults to None.
    :return: The retrieved value, converted from JSON to the specified JSONConvertible type, or the given
    default value if the given key was not found in the given dictionary.
    """
    if key in d:
        return t.from_json(d[key])
    return default if default is not None else None


#


def trim_none(d: dict[H, T | None]) -> dict[H, T]:
    """
    Generates a copy of the given dictionary that excludes all fields for which the value is None.

    :param d: The dictionary to remove None values from.
    :return: The copied dictionary sans None values.
    """
    return {
        k: v for k, v in d.items() if v is not None
    }


#


def unique_by(s: Iterable[T], key: Callable[[T], H]) -> Iterable[T]:
    """
    Creates an iterable object that iterates through all unique values in the given iterable object, using the
    given function to derive a value from each object that uniqueness is based on.

    :param s: The iterable object to iterate through the unique values of.
    :param key: A function that takes one of the iterated objects as an argument and returns a hashable value
    that will be used to determine whether that object is unique or not.
    :return: An lazy generator for the unique values of the given iterable object.
    """
    unique = set()
    for item in s:
        k = key(item)
        if k not in unique:
            unique.add(k)
            yield item
