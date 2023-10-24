
from enum import Enum
from typing import Union, Optional, Iterable


class DamageModifierType(Enum):
    NONE = 0
    OFFENSE_MULTIPLIER = 1
    DEFENSE_MULTIPLIER = 2
    BASE_DAMAGE = 3
    MULTI_TARGET = 4
    WEATHER = 5
    CRITICAL = 6
    STATUS = 7
    OTHER = 8


class DamageModifier:

    def __init__(self, typ: DamageModifierType, value: Union[int, float]):
        self.type = typ
        self.value = value


