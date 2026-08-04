from __future__ import annotations

from SprelfPkmn.Objects import *

from enum import IntFlag, Enum
from typing import Iterable
from abc import ABC

from SprelfJSON import JSONModel, AbstractJSONModel
from SprelfPkmn.Objects.BoardState import Weather, BoardEffectType, Terrain

TWO_THIRDS = 2732 / 4096
ONE_POINT_THREE_THREE = 5448 / 4096
ONE_POINT_ONE = 4505 / 4096
ONE_POINT_TWO = 4915 / 4096
ONE_POINT_THREE = 5324 / 4096


#


class MoveProperties(IntFlag):
    NONE = 0
    CONTACT = 1
    SOUND = 2
    SLASHING = 4
    PUNCHING = 8
    BITING = 16
    BULLET = 32
    WIND = 64
    POWDER = 128
    ABSORBING = 256
    PULSING = 512
    MULTI_TARGET = 1024


class DamageType(Enum):
    PHYSICAL = 1
    SPECIAL = 2


class Move(JSONModel, ABC):
    """
    Describes a single move learnable by a Pokémon
    """
    name: str
    type: Type
    properties: MoveProperties = MoveProperties.NONE
    __name_field__ = "category"
    __name_field_required__ = True
    accuracy: int | None = 100
    max_pp: int | None = None
    description: str = ""
    priority: int = 0


class DamagingMove(Move):
    base_power: int
    damage_type: DamageType
    offense_stat: Stat
    defense_stat: Stat

    def __init__(self, name: str, type: Type,
                 base_power: int,
                 offense_stat: Stat,
                 defense_stat: Stat | None = None,
                 damage_type: DamageType | None = None,
                 accuracy: int | None = None,
                 description: str = "", max_pp: int | None = None,
                 properties: MoveProperties = MoveProperties.NONE):
        if defense_stat is None:
            defense_stat = Stat.DEFENSE if offense_stat == Stat.ATTACK else Stat.SP_DEFENSE
        if damage_type is None:
            damage_type = DamageType.PHYSICAL if offense_stat in (Stat.ATTACK, Stat.DEFENSE) else DamageType.SPECIAL
        super().__init__(name=name, type=type, base_power=base_power, offense_stat=offense_stat,
                         defense_stat=defense_stat, accuracy=accuracy, description=description,
                         damage_type=damage_type,
                         max_pp=max_pp, properties=properties)

    def __str__(self) -> str:
        return f"[{type(self).__name__}] {self.name} : {self.type.name.capitalize()} ({self.base_power})"

    def get_damage_conditions(self, attacker: Pokemon,
                              defender: Pokemon,
                              board_state: BoardState,
                              critical: bool = False) -> Iterable[DamageCondition]:
        yield from WeatherModifiers.damage_conditions(self,
                                                      attacker=attacker,
                                                      defender=defender,
                                                      board_state=board_state)
        yield from AbilityModifiers.damage_conditions(self,
                                                      attacker=attacker,
                                                      defender=defender,
                                                      board_state=board_state,
                                                      critical=critical)
        yield from BoardStateModifiers.damage_conditions(move=self,
                                                         attacker=attacker,
                                                         defender=defender,
                                                         board_state=board_state,
                                                         critical=critical)
        yield from ItemModifiers.damage_conditions(move=self,
                                                   attacker=attacker,
                                                   defender=defender,
                                                   board_state=board_state,
                                                   critical=critical)

    def get_stat_conditions(self, attacker: Pokemon,
                            defender: Pokemon,
                            board_state: BoardState) -> Iterable[StatCondition]:
        yield from WeatherModifiers.stat_conditions(move=self,
                                                    attacker=attacker,
                                                    defender=defender,
                                                    board_state=board_state)
        yield from ItemModifiers.stat_conditions(move=self,
                                                 attacker=attacker,
                                                 defender=defender,
                                                 board_state=board_state)

    def get_base_power_modifiers(self, attacker: Pokemon,
                                 defender: Pokemon,
                                 board_state: BoardState) -> Iterable[BasePowerCondition]:
        yield from AbilityModifiers.base_power_conditions(move=self,
                                                          attacker=attacker,
                                                          defender=defender,
                                                          board_state=board_state)
        yield from BoardStateModifiers.base_power_conditions(move=self,
                                                             attacker=attacker,
                                                             defender=defender,
                                                             board_state=board_state)
        yield from ItemModifiers.base_power_conditions(move=self,
                                                       attacker=attacker,
                                                       defender=defender,
                                                       board_state=board_state)

    def get_stab_modifiers(self, attacker: Pokemon,
                           defender: Pokemon,
                           board_state: BoardState) -> Iterable[STABCondition]:
        if self.type in attacker.data.typing:
            if attacker.ability.name == "Adaptability":
                yield STABCondition(source=attacker.ability.name, multiplier=2)


#


class StatusMove(Move):

    def __str__(self) -> str:
        return f"[{type(self).__name__}] {self.name} : {self.type.name.capitalize()}"


class MoveList(JSONModel):
    """
    Describes a collection of moves that are learnable by a Pokémon
    """
    moves: list[Move] = []


class MoveSet(JSONModel):
    """
    Describes the set of 4 moves that a single Pokémon knows
    """
    moves: list[Move] = []


#


#


# +

class CalculationCondition(AbstractJSONModel, ABC):
    ...


class DamageCondition(CalculationCondition, ABC):
    multiplier: float
    for_attacker: bool = True


class STABCondition(CalculationCondition, ABC):
    source: str
    multiplier: float


class StatCondition(CalculationCondition, ABC):
    for_attacker: bool
    stat: Stat
    multiplier: float


class BasePowerCondition(CalculationCondition, ABC):
    multiplier: float


class AbilityCondition(CalculationCondition, ABC):
    ability: Ability


class ItemCondition(CalculationCondition, ABC):
    item: Item


class AbilityBasePowerCondition(BasePowerCondition, AbilityCondition):
    ...


class TerrainBasePowerCondition(BasePowerCondition):
    terrain: Terrain


class ItemBasePowerCondition(BasePowerCondition, ItemCondition):
    ...


class ItemStatCondition(StatCondition, ItemCondition):
    ...


class ItemDamageCondition(DamageCondition, ItemCondition):
    ...


class TypeChangeCondition(CalculationCondition):
    source: str
    new_type: Type


class WeatherCondition(CalculationCondition, ABC):
    weather: Weather


class WeatherDamageCondition(DamageCondition, WeatherCondition):
    ...


class WeatherStatModifier(StatCondition, WeatherCondition):
    ...


class ScreensDamageCondition(DamageCondition):
    effect: BoardEffectType


class AssistanceDamageCondition(DamageCondition):
    source: str


class AbilityDamageCondition(DamageCondition, AbilityCondition):
    ...


class AbilityStatCondition(StatCondition, AbilityCondition):
    ...


#


class WeatherModifiers:

    @classmethod
    def damage_conditions(cls,
                          move: DamagingMove,
                          attacker: Pokemon,
                          defender: Pokemon,
                          board_state: BoardState) -> Iterable[WeatherDamageCondition]:
        if move.type == Type.FIRE:
            if board_state.weather in (Weather.SUN, Weather.HARSH_SUN):
                yield WeatherDamageCondition(weather=board_state.weather, multiplier=1.5)
            elif board_state.weather == Weather.RAIN:
                yield WeatherDamageCondition(weather=board_state.weather, multiplier=0.5)
            elif board_state.weather == Weather.HEAVY_RAIN:
                yield WeatherDamageCondition(weather=board_state.weather, multiplier=0)
        elif move.type == Type.WATER:
            if board_state.weather in (Weather.RAIN, Weather.HEAVY_RAIN):
                yield WeatherDamageCondition(weather=board_state.weather, multiplier=1.5)
            elif board_state.weather == Weather.SUN:
                yield WeatherDamageCondition(weather=board_state.weather, multiplier=0.5)
            elif board_state.weather == Weather.HARSH_SUN:
                yield WeatherDamageCondition(weather=board_state.weather, multiplier=0)

    @classmethod
    def stat_conditions(cls,
                        move: DamagingMove,
                        attacker: Pokemon,
                        defender: Pokemon,
                        board_state: BoardState) -> Iterable[WeatherStatModifier]:
        if board_state.weather == Weather.SNOW and Type.ICE in defender.data.typing:
            yield WeatherStatModifier(weather=board_state.weather,
                                      stat=Stat.DEFENSE,
                                      multiplier=1.5,
                                      for_attacker=False)
        if board_state.weather == Weather.SAND and Type.ROCK in defender.data.typing:
            yield WeatherStatModifier(weather=board_state.weather,
                                      stat=Stat.SP_DEFENSE,
                                      multiplier=1.5,
                                      for_attacker=False)


class AbilityModifiers:

    @classmethod
    def damage_conditions(cls,
                          move: DamagingMove,
                          attacker: Pokemon,
                          defender: Pokemon,
                          board_state: BoardState,
                          critical: bool = False) -> Iterable[AbilityDamageCondition]:

        if critical and attacker.ability.name == "Sniper":
            yield AbilityDamageCondition(ability=attacker.ability, multiplier=1.5)

        if defender.ability.name in ("Filter", "Solid Rock", "Prism Armor") \
                and Type.get_damage_multiplier(move.type, defender.data.typing) > 1:
            yield AbilityDamageCondition(ability=defender.ability, multiplier=0.75)
        if attacker.ability.name == "Tinted Lens" and Type.get_damage_multiplier(move.type, defender.data.typing) < 1:
            yield AbilityDamageCondition(ability=attacker.ability, multiplier=2)

        if attacker.ability.name != "Mold Breaker":
            if defender.ability.name == "Bulletproof" and MoveProperties.BULLET in move.properties:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0)
            if defender.ability.name == "Soundproof" and MoveProperties.SOUND in move.properties:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0)
            if defender.ability.name in ("Flash Fire", "Well-baked Body",
                                         "Thermal Exchange") and move.type == Type.FIRE:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0)
            if defender.ability.name in ("Storm Drain", "Water Absorb", "Dry Skin") and move.type == Type.WATER:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0)
            if defender.ability.name == "Levitate" and move.type == Type.GROUND:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0)

    @classmethod
    def base_power_conditions(cls, move: DamagingMove,
                              attacker: Pokemon,
                              defender: Pokemon,
                              board_state: BoardState) -> Iterable[AbilityBasePowerCondition]:
        if attacker.ability.name == "Sharpness" and MoveProperties.SLASHING in move.properties:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=1.5)
        if attacker.ability.name == "Mega Launcher" and MoveProperties.PULSING in move.properties:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=1.5)
        if attacker.ability.name == "Iron Fist" and MoveProperties.PUNCHING in move.properties:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=ONE_POINT_TWO)
        if attacker.ability.name == "Strong Jaw" and MoveProperties.BITING in move.properties:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=1.5)
        if attacker.ability.name == "Steelworker" and move.type == Type.STEEL:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=1.5)


class BoardStateModifiers:
    @classmethod
    def damage_conditions(cls, move: DamagingMove,
                          attacker: Pokemon,
                          defender: Pokemon,
                          board_state: BoardState,
                          critical: bool) -> Iterable[DamageCondition]:

        if attacker.ability.name != "Infiltrator":
            screens = [effect for effect in board_state.effects
                       if effect.type in (BoardEffectType.LIGHT_SCREEN, BoardEffectType.REFLECT,
                                          BoardEffectType.AURORA_VEIL)
                       and all(entity.team == 1 for entity in effect.targets)]
            physical_screens = [s for s in screens if s.type != BoardEffectType.LIGHT_SCREEN]
            special_screens = [s for s in screens if s.type != BoardEffectType.REFLECT]
            if move.damage_type == DamageType.PHYSICAL and len(physical_screens) > 0:
                yield ScreensDamageCondition(effect=physical_screens[0].type,
                                             multiplier=TWO_THIRDS if board_state.is_doubles else 0.5)
            elif move.damage_type == DamageType.SPECIAL and len(special_screens) > 0:
                yield ScreensDamageCondition(effect=special_screens[0].type,
                                             multiplier=TWO_THIRDS if board_state.is_doubles else 0.5)

        if move.type == Type.FAIRY and any(effect.type == BoardEffectType.FAIRY_AURA for effect in board_state.effects):
            yield AssistanceDamageCondition(source="Fairy Aura", multiplier=ONE_POINT_THREE_THREE)
        elif move.type == Type.DARK and any(effect.type == BoardEffectType.DARK_AURA for effect in board_state.effects):
            yield AssistanceDamageCondition(source="Dark Aura", multiplier=ONE_POINT_THREE_THREE)

    @classmethod
    def base_power_conditions(cls, move: DamagingMove,
                              attacker: Pokemon,
                              defender: Pokemon,
                              board_state: BoardState) -> Iterable[BasePowerCondition]:
        if board_state.terrain == Terrain.MISTY and move.type == Type.DRAGON and cls._is_grounded(defender):
            yield TerrainBasePowerCondition(terrain=board_state.terrain, multiplier=0.5)
        elif board_state.terrain == Terrain.ELECTRIC and move.type == Type.ELECTRIC and cls._is_grounded(attacker):
            yield TerrainBasePowerCondition(terrain=board_state.terrain, multiplier=ONE_POINT_THREE)
        elif board_state.terrain == Terrain.GRASSY and move.type == Type.GRASS and cls._is_grounded(attacker):
            yield TerrainBasePowerCondition(terrain=board_state.terrain, multiplier=ONE_POINT_THREE)
        elif board_state.terrain == Terrain.PSYCHIC:
            if move.priority > 0:
                yield TerrainBasePowerCondition(terrain=board_state.terrain, multiplier=0)
            elif move.type == Type.PSYCHIC and cls._is_grounded(attacker):
                yield TerrainBasePowerCondition(terrain=board_state.terrain, multiplier=ONE_POINT_THREE)

    @classmethod
    def _is_grounded(cls, pok: Pokemon):
        return Type.FLYING not in pok.data.typing and pok.ability.name != "Levitate"


class ItemModifiers:

    @classmethod
    def base_power_conditions(cls, move: DamagingMove,
                              attacker: Pokemon,
                              defender: Pokemon,
                              board_state: BoardState) -> Iterable[ItemBasePowerCondition]:
        if attacker.item:
            if attacker.item.name == "Muscle Band" and move.damage_type == DamageType.PHYSICAL:
                yield ItemBasePowerCondition(item=attacker.item, multiplier=ONE_POINT_ONE)
            if attacker.item.name == "Wise Glasses" and move.damage_type == DamageType.SPECIAL:
                yield ItemBasePowerCondition(item=attacker.item, multiplier=ONE_POINT_ONE)
            if any(attacker.item.name == name for name in cls._type_item(move.type)):
                yield ItemBasePowerCondition(item=attacker.item, multiplier=ONE_POINT_TWO)
            if attacker.item.name == "Punching Glove" and MoveProperties.PUNCHING in move.properties:
                yield ItemBasePowerCondition(item=attacker.item, multiplier=ONE_POINT_ONE)

    @classmethod
    def stat_conditions(cls, move: DamagingMove,
                        attacker: Pokemon,
                        defender: Pokemon,
                        board_state: BoardState) -> Iterable[ItemStatCondition]:
        if defender.item and defender.item.name == "Assault Vest":
            yield ItemStatCondition(item=defender.item, multiplier=1.5, for_attacker=False,
                                    stat=Stat.SP_DEFENSE)

    @classmethod
    def damage_conditions(cls, move: DamagingMove,
                          attacker: Pokemon,
                          defender: Pokemon,
                          board_state: BoardState,
                          critical: bool) -> Iterable[ItemDamageCondition]:
        if attacker.item:
            if attacker.item.name == "Life Orb":
                yield ItemDamageCondition(item=attacker.item, multiplier=ONE_POINT_THREE, for_attacker=True)
            if attacker.item.name == "Choice Band" and move.damage_type == DamageType.PHYSICAL:
                yield ItemDamageCondition(item=attacker.item, multiplier=1.5, for_attacker=True)
            if attacker.item.name == "Choice Scarf" and move.damage_type == DamageType.SPECIAL:
                yield ItemDamageCondition(item=attacker.item, multiplier=1.5, for_attacker=True)
            if attacker.item.name == "Expert Belt" and Type.get_damage_multiplier(move.type, defender.data.typing) > 1:
                yield ItemDamageCondition(item=attacker.item, multiplier=ONE_POINT_TWO, for_attacker=True)

    @classmethod
    def _type_item(cls, t: Type) -> tuple[str, ...]:
        match t:
            case t.FIRE:
                return "Charcoal", "Flame Plate"
            case t.WATER:
                return "Mystic Water", "Wave Incense", "Sea Incense", "Splash Plate"
            case t.GRASS:
                return "Miracle Seed", "Meadow Plate", "Rose Incense"
            case t.ELECTRIC:
                return "Magnet", "Zap Plate"
            case t.GROUND:
                return "Soft Sand", "Earth Plate"
            case t.ROCK:
                return "Hard Stone", "Rock Incense", "Stone Plate"
            case t.FLYING:
                return "Sharp Beak", "Sky Plate"
            case t.FIGHTING:
                return "Black Belt", "Fist Plate"
            case t.PSYCHIC:
                return "Twisted Spoon", "Mind Plate", "Odd Incense"
            case t.GHOST:
                return "Spell Tag", "Spooky Plate"
            case t.DARK:
                return "Black Glasses", "Dread Plate"
            case t.BUG:
                return "Silver Powder", "Insect Plate"
            case t.POISON:
                return "Poison Barb", "Toxic Plate"
            case t.STEEL:
                return "Metal Coat", "Iron Plate"
            case t.FAIRY:
                return "Fairy Feather", "Pixie Plate"
            case t.DRAGON:
                return "Dragon Fang", "Draco Plate"
            case t.ICE:
                return "Never-Melt Ice", "Icicle Plate"
            case t.NORMAL:
                return "Silk Scarf", "Blank Plate"
            case _:
                return ()
