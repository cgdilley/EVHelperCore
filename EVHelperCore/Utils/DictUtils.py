
from typing import Hashable, List, Any, TypeVar, Dict, Optional, Type, Set, Iterable, \
    Callable
from EVHelperCore.Interfaces import IJsonExchangeable

T = TypeVar('T')
TIJsonExchangeable = TypeVar('TIJsonExchangeable', bound=IJsonExchangeable)
H = TypeVar('H', bound=Hashable)


def add_or_append(d: Dict[H, List[T]], key: H, val: T):
    """
    Appends the given value to the list found at the given key in the given dictionary.  If the key does not yet
    exist, it is created, containing a list with just the given value.

    :param d: The dictionary mapping keys to lists of values
    :param key: The key where the list to append to is fond
    :param val: The value to append
    """
    if key in d:
        d[key].append(val)
    else:
        d[key] = [val]


#


def pop_field(d: Dict[H, T], key: H, default: Optional[T] = None) -> Optional[T]:
    """
    Returns the value from the given key from the given dictionary, if it exists, and then removes
    that key from the dictionary.  If the key does not exist, the given default value is returned instead.

    :param d: The dictionary to pop the field from
    :param key: The key of the field to pop
    :param default: Optional.  The value to return if the given key is not found in the given dictionary.
    Defaults to None.
    :return: The popped value if the given key was found, or the given default value.
    """
    if key in d:
        v = d[key]
        del d[key]
        return v
    else:
        return default if default is not None else None


#


def get_or_default(d: Dict[H, T], key: H, default: Optional[T] = None) -> Optional[T]:
    """
    Retrieves the value at the given key in the given dictionary, if it exists.  If the given key is
    not found, returns the given default value instead rather than raising an error.

    :param d: The dictionary to get the value from.
    :param key: The key to retrieve the value for.
    :param default: Optional.  The default value to return if the given key is not found in the given
    dictionary.  Defaults to None.
    :return: The retrieved value.
    """
    if key in d:
        return d[key]
    return default if default is not None else None


#


def from_json_or_default(t: Type[TIJsonExchangeable],
                         d: Dict[H, dict],
                         key: H,
                         default: Optional[TIJsonExchangeable] = None) -> Optional[TIJsonExchangeable]:
    """
    For a dictionary mapping keys to JSON objects representing a IJsonExchangeable object, extract
    the JSON from the given key and convert it into the specified IJsonExchangeable type using that type's
    .from_json() method.  If the given key is not found in the given dictionary, returns the
    given default value instead.

    :param t: The IJsonExchangeable type to parse the JSON as.
    :param d: The dictionary mapping keys to IJsonExchangeable JSON representations
    :param key: The key to extract the JSON from
    :param default: Optional.  The default value to return if the given key is not found in the given dictionary.
    Defaults to None.
    :return: The retrieved value, converted from JSON to the specified IJsonExchangeable type, or the given
    default value if the given key was not found in the given dictionary.
    """
    if key in d:
        return t.from_json(d[key])
    return default if default is not None else None


#


def trim_none(d: Dict[H, Optional[T]]) -> Dict[H, T]:
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
