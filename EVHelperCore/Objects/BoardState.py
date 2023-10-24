from __future__ import annotations

from enum import Enum, IntFlag
from typing import Optional, Iterable

from EVHelperCore.Objects.Move import Move
from EVHelperCore.Objects.Type import Type, Typing, TypeEffectivenessRecord
from EVHelperCore.Objects.Ability import Ability
from EVHelperCore.Objects.Stats import Stats
from EVHelperCore.Objects.Item import Item
from EVHelperCore.Objects.DamageModifier import DamageModifierType, DamageModifier


class Entity:

    def __init__(self, typing: Typing, ability: Ability, stats: Stats, team: int, item: Optional[Item]):
        self.typing = typing
        self.ability = ability
        self.stats = stats
        self.team = team
        self.item = item


class Terrain(Enum):
    NONE = 0
    PSYCHIC = 1
    ELECTRIC = 2
    MISTY = 3
    GRASSY = 4


class Weather(Enum):
    NONE = 0
    SUN = 1
    RAIN = 2
    SAND = 3
    HAIL = 4
    SNOW = 5
    HARSH_SUN = 6
    HEAVY_RAIN = 7
    STRONG_WINDS = 8
    CLOUD_NINE = 9

class Room(IntFlag):
    NONE = 0
    TRICK = 1
    MAGIC = 2
    WONDER = 4


class BoardEffectType(Enum):
    NONE = 0
    GRAVITY = 1
    AURA_BREAK = 2
    FAIRY_AURA = 3
    DARK_AURA = 4
    BEADS_OF_RUIN = 5
    TABLETS_OF_RUIN = 6
    SWORD_OF_RUIN = 7
    VESSEL_OF_RUIN = 8
    STEALTH_ROCK = 9
    SPIKES_1 = 10
    SPIKES_2 = 11
    SPIKES_3 = 12
    REFLECT = 13
    LIGHT_SCREEN = 14
    AURORA_VEIL = 15
    HELPING_HAND = 16
    BATTERY = 17
    FRIEND_GUARD = 18
    TAILWIND = 19


class BoardEffect:

    def __init__(self, typ: BoardEffectType, *targets: Entity):
        self.type = typ
        self.targets = targets


class BoardState:

    def __init__(self, *entities: Entity,
                 effects: Optional[Iterable[BoardEffect]] = None,
                 terrain: Terrain = Terrain.NONE, weather: Weather = Weather.NONE, room: Room = Room.NONE):
        self.entities = entities
        self.terrain = terrain
        self.weather = weather
        self.room = room
        self.effects = effects

    def get_effects_for_entity(self, entity: Entity) -> Iterable[BoardEffect]:
        yield from (e for e in self.effects if entity in e.targets)

    def get_damage_modifiers(self, source: Entity, targets: Iterable[Entity], move: Move) -> Iterable[DamageModifier]:
        yield from []

