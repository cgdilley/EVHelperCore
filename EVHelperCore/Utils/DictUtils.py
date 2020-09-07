
from typing import Hashable, List, Any, TypeVar, Dict, Optional, Type, Set, Iterable, \
    Callable
from EVHelperCore.Interfaces import IJsonExchangeable

T = TypeVar('T')
TIJsonExchangeable = TypeVar('TIJsonExchangeable', bound=IJsonExchangeable)
H = TypeVar('H', bound=Hashable)


def add_or_append(d: Dict[H, List[T]], key: H, val: T):
    if key in d:
        d[key].append(val)
    else:
        d[key] = [val]


def pop_field(d: Dict[H, T], key: H, default: Optional[T] = None) -> Optional[T]:
    if key in d:
        v = d[key]
        del d[key]
        return v
    else:
        return default if default is not None else None


def get_or_default(d: Dict[H, T], key: H, default: Optional[T] = None) -> Optional[T]:
    if key in d:
        return d[key]
    return default if default is not None else None


def from_json_or_default(t: Type[TIJsonExchangeable],
                         d: Dict[H, TIJsonExchangeable],
                         key: H,
                         default: Optional[T] = None) -> Optional:
    if key in d:
        return t.from_json(d[key])
    return default if default is not None else None


def trim_none(d: Dict[H, Optional[T]]) -> Dict[H, T]:
    return {
        k: v for k, v in d.items() if v is not None
    }


def unique_by(s: Iterable[T], key: Callable[[T], H]) -> Iterable[T]:
    unique = set()
    for item in s:
        k = key(item)
        if k not in unique:
            unique.add(k)
            yield item
