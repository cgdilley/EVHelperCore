from __future__ import annotations

from SprelfPkmn.Objects import *

from enum import IntFlag, Enum
from typing import Iterable
from abc import ABC

from SprelfJSON import JSONModel, AbstractJSONModel
from SprelfPkmn.Objects.BoardState import Weather, BoardEffectType, Terrain
from .CalculationCondition import DamageCondition, BasePowerCondition, STABCondition, StatCondition, \
    AbilityStatCondition, AbilityBasePowerCondition, AbilityCondition, AbilityDamageCondition, \
    ItemBasePowerCondition, ItemDamageCondition, ItemStatCondition, ItemCondition, \
    ScreensDamageCondition, WeatherDamageCondition, WeatherCondition, WeatherStatCondition, \
    BoardEffectBasePowerCondition, BoardEffectDamageCondition, TerrainBasePowerCondition


TWO_THIRDS = 2732 / 4096
FOUR_THIRDS = 5448 / 4096
ONE_POINT_ONE = 4505 / 4096
ONE_POINT_TWO = 4915 / 4096
ONE_POINT_THREE = 5324 / 4096


#


class MoveProperties(IntFlag):
    NONE = 0
    CONTACT = 2**0
    SOUND = 2**1
    SLASHING = 2**2
    PUNCHING = 2**3
    BITING = 2**4
    BULLET = 2**5
    WIND = 2**6
    POWDER = 2**7
    ABSORBING = 2**8
    PULSING = 2**9
    MULTI_TARGET = 2**10
    HAS_SECONDARIES = 2**11
    RECOIL = 2**12
    CRASHING = 2**13
    IGNORES_BOOSTS = 2**14


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

#


class WeatherModifiers:

    @classmethod
    def damage_conditions(cls,
                          move: DamagingMove,
                          attacker: Pokemon,
                          defender: Pokemon,
                          board_state: BoardState) -> Iterable[WeatherDamageCondition]:
        if len(board_state.weather_negations) == 0:
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
                        board_state: BoardState) -> Iterable[WeatherStatCondition]:
        if len(board_state.weather_negations) == 0:
            if board_state.weather == Weather.SNOW and Type.ICE in defender.data.typing:
                yield WeatherStatCondition(weather=board_state.weather,
                                          stat=Stat.DEFENSE,
                                          multiplier=1.5,
                                          for_attacker=False)
            if board_state.weather == Weather.SAND and Type.ROCK in defender.data.typing:
                yield WeatherStatCondition(weather=board_state.weather,
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

        typing_multiplier = Type.get_damage_multiplier(move.type, defender.data.typing)
        if defender.ability.name in ("Filter", "Solid Rock", "Prism Armor") and typing_multiplier > 1:
            yield AbilityDamageCondition(ability=defender.ability, multiplier=0.75)
        if attacker.ability.name == "Tinted Lens" and typing_multiplier < 1:
            yield AbilityDamageCondition(ability=attacker.ability, multiplier=2)
        if attacker.ability.name == "Neuroforce" and typing_multiplier > 1:
            yield AbilityDamageCondition(ability=attacker.ability, multiplier=1.25)

        if attacker.ability.name != "Mold Breaker":
            if defender.ability.name == "Bulletproof" and MoveProperties.BULLET in move.properties:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0,
                                             for_attacker=False)
            if defender.ability.name == "Soundproof" and MoveProperties.SOUND in move.properties:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0,
                                             for_attacker=False)
            if defender.ability.name in ("Flash Fire", "Well-baked Body") and move.type == Type.FIRE:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0,
                                             for_attacker=False)
            if defender.ability.name == "Volt Absorb" and move.type == Type.ELECTRIC:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0,
                                             for_attacker=False)
            if defender.ability.name in ("Storm Drain", "Water Absorb", "Dry Skin") and move.type == Type.WATER:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0,
                                             for_attacker=False)
            if defender.ability.name == "Levitate" and move.type == Type.GROUND:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0,
                                             for_attacker=False)
        if defender.ability.name == "Fluffy":
            if MoveProperties.CONTACT in move.properties:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=0.5)
            if move.type == Type.FIRE:
                yield AbilityDamageCondition(ability=defender.ability, multiplier=2)
        if defender.ability.name == "Punk Rock" and MoveProperties.SOUND in move.properties:
            yield AbilityDamageCondition(ability=defender.ability, multiplier=0.5)
        if defender.ability.name == "Ice Scales" and move.damage_type == DamageType.SPECIAL:
            yield AbilityDamageCondition(ability=defender.ability, multiplier=0.5)
        # TODO: Multiscale / Shadow Shield

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
        if attacker.ability.name == "Tough Claws" and MoveProperties.CONTACT in move.properties:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=ONE_POINT_THREE)
        if attacker.ability.name == "Punk Rock" and MoveProperties.SOUND in move.properties:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=ONE_POINT_THREE)
        if attacker.ability.name == "Sheer Force" and MoveProperties.HAS_SECONDARIES in move.properties:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=ONE_POINT_THREE)
        if attacker.ability.name == "Reckless" and \
                (MoveProperties.RECOIL in move.properties or MoveProperties.CRASHING in move.properties):
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=ONE_POINT_TWO)

        if attacker.ability.name == "Steelworker" and move.type == Type.STEEL:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=1.5)
        if attacker.ability.name in ("Aerilate", "Refrigerate", "Pixilate", "Dragonize", "Galvanize") \
            and move.type == Type.NORMAL:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=ONE_POINT_TWO)
        if attacker.ability.name == "Normalize":
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=ONE_POINT_TWO)
        if attacker.ability.name == "Technician" and move.base_power <= 60:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=1.5)
        if attacker.ability.name == "Sand Force" and board_state.weather == Weather.SAND and \
            move.type in ("Ground", "Rock", "Steel") and len(board_state.weather_negations) == 0:
            yield AbilityBasePowerCondition(ability=attacker.ability, multiplier=ONE_POINT_THREE)
        # TODO: Steely Spirit
        # TODO: Toxic Boost / Flare Boost
        # TODO: Power Spot / Battery / Whatever Cherrim's ability is
        # TODO: Analytic
        # TODO: Rivalry
        # TODO: Supreme Overlord
        #



class BoardStateModifiers:
    @classmethod
    def damage_conditions(cls, move: DamagingMove,
                          attacker: Pokemon,
                          defender: Pokemon,
                          board_state: BoardState,
                          critical: bool) -> Iterable[DamageCondition]:

        if attacker.ability.name != "Infiltrator" and not critical:
            screens = [effect for effect in board_state.get_effects_for_entity(defender)
                       if effect.type in (BoardEffectType.LIGHT_SCREEN, BoardEffectType.REFLECT,
                                          BoardEffectType.AURORA_VEIL)]
            physical_screens = [s for s in screens if s.type != BoardEffectType.LIGHT_SCREEN]
            special_screens = [s for s in screens if s.type != BoardEffectType.REFLECT]
            if move.damage_type == DamageType.PHYSICAL and len(physical_screens) > 0:
                yield ScreensDamageCondition(effect=physical_screens[0].type,
                                             multiplier=TWO_THIRDS if board_state.is_doubles else 0.5)
            elif move.damage_type == DamageType.SPECIAL and len(special_screens) > 0:
                yield ScreensDamageCondition(effect=special_screens[0].type,
                                             multiplier=TWO_THIRDS if board_state.is_doubles else 0.5)

        if any(be.type == BoardEffectType.FRIEND_GUARD for be in board_state.get_effects_for_entity(defender)):
            yield BoardEffectDamageCondition(effect=BoardEffectType.FRIEND_GUARD, multiplier=0.75)

        #

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

        has_aura_break = any(effect.type == BoardEffectType.AURA_BREAK for effect in board_state.effects)
        if move.type == Type.FAIRY and any(effect.type == BoardEffectType.FAIRY_AURA for effect in board_state.effects):
            if has_aura_break:
                yield BoardEffectBasePowerCondition(effect=BoardEffectType.AURA_BREAK, multiplier=0.75)
            else:
                yield BoardEffectBasePowerCondition(effect=BoardEffectType.FAIRY_AURA, multiplier=FOUR_THIRDS)
        elif move.type == Type.DARK and any(effect.type == BoardEffectType.DARK_AURA for effect in board_state.effects):
            if has_aura_break:
                yield BoardEffectBasePowerCondition(effect=BoardEffectType.AURA_BREAK, multiplier=0.75)
            else:
                yield BoardEffectBasePowerCondition(effect=BoardEffectType.DARK_AURA, multiplier=FOUR_THIRDS)

        if any(be.type == BoardEffectType.HELPING_HAND for be in board_state.get_effects_for_entity(attacker)):
            yield BoardEffectBasePowerCondition(effect=BoardEffectType.HELPING_HAND, multiplier=1.5,
                                                for_attacker=True)

        # TODO: Mud Sport, Water Sport
        # TODO: Charge
        # TODO: Me First

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
            # TODO: Special legendary held items

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
            if attacker.item.name == "Choice Specs" and move.damage_type == DamageType.SPECIAL:
                yield ItemDamageCondition(item=attacker.item, multiplier=1.5, for_attacker=True)
            if attacker.item.name == "Expert Belt" and Type.get_damage_multiplier(move.type, defender.data.typing) > 1:
                yield ItemDamageCondition(item=attacker.item, multiplier=ONE_POINT_TWO, for_attacker=True)

        if defender.item:
            if defender.item.name == cls._type_resist_berry(move.type) \
                and not any(be.type == BoardEffectType.UNNERVE
                            for be in board_state.get_effects_for_entity(defender)) \
                and (move.type == Type.NORMAL
                    or Type.get_damage_multiplier(move.type, defender.data.typing) > 1):
                yield ItemDamageCondition(item=defender.item,
                                          multiplier=0.25 if defender.ability.name == "Ripen" else 0.5,
                                          for_attacker=False)
        # TODO: Metronome

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


    @classmethod
    def _type_resist_berry(cls, t: Type) -> str:
        match t:
            case t.FIRE:
                return "Occa Berry"
            case t.WATER:
                return "Passho Berry"
            case t.GRASS:
                return "Rindo Berry"
            case t.ELECTRIC:
                return "Wacan Berry"
            case t.GROUND:
                return "Shuca Berry"
            case t.ROCK:
                return "Charti Berry"
            case t.FLYING:
                return "Coba Berry"
            case t.FIGHTING:
                return "Chople Berry"
            case t.PSYCHIC:
                return "Payapa Berry"
            case t.GHOST:
                return "Kasib Berry"
            case t.DARK:
                return "Colbur Berry"
            case t.BUG:
                return "Tanga Berry"
            case t.POISON:
                return "Kebia Berry"
            case t.STEEL:
                return "Babiri Berry"
            case t.FAIRY:
                return "Roseli Berry"
            case t.DRAGON:
                return "Haban Berry"
            case t.ICE:
                return "Yache Berry"
            case t.NORMAL:
                return "Chilan Berry"
            case _:
                return ()
