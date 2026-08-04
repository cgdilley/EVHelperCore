from unittest import TestCase

from SprelfPkmn.Calculations.Stats import *
from SprelfPkmn.Calculations.StatTemplates import get_combinations_for_value
from SprelfPkmn.Calculations.Damage import *
from SprelfPkmn.Objects import *

import itertools


class TestCalculations(TestCase):

    def test_stat_calc(self):
        # Example from https://bulbapedia.bulbagarden.net/wiki/Statistic#Determination_of_stats
        garchomp = Stats.of(base=BaseStats(attack=130, defense=95, special_attack=80,
                                           special_defense=85, speed=102, hp=108),
                            evs=[EV(Stat.HP, number=10),
                                 EV(stat=Stat.ATTACK, number=24),
                                 EV(stat=Stat.DEFENSE, number=12),
                                 EV(stat=Stat.SP_ATTACK, number=6),
                                 EV(stat=Stat.SP_DEFENSE, number=11),
                                 EV(stat=Stat.SPEED, number=3)],
                            ivs=[IV(stat=Stat.HP, value=31),
                                 IV(stat=Stat.ATTACK, value=31),
                                 IV(stat=Stat.DEFENSE, value=31),
                                 IV(stat=Stat.SP_ATTACK, value=31),
                                 IV(stat=Stat.SP_DEFENSE, value=31),
                                 IV(stat=Stat.SPEED, value=31)],
                            nature=Nature.Adamant,
                            level=50,
                            modifiers=[])

        real_stats = [(Stat.HP, 193), (Stat.ATTACK, 191), (Stat.DEFENSE, 127),
                      (Stat.SP_ATTACK, 95), (Stat.SP_DEFENSE, 116), (Stat.SPEED, 125)]

        for stat, value in real_stats:
            self.assertEqual(value, get_stat_value_from_info(garchomp, stat))
            self.assertIn(garchomp.base.get_stat(stat),
                          get_base_stat_from_value(stat=stat,
                                                   ev=garchomp.get_ev(stat),
                                                   iv=garchomp.get_iv(stat),
                                                   level=garchomp.level,
                                                   nature=garchomp.nature,
                                                   value=value))
            self.assertIn(garchomp.get_ev(stat),
                          get_evs_from_value(stat=stat,
                                             base=garchomp.base.get_stat(stat),
                                             iv=garchomp.get_iv(stat),
                                             level=garchomp.level,
                                             nature=garchomp.nature,
                                             value=value,
                                             ev_type=StatPoint))
            self.assertIn(garchomp.get_iv(stat),
                          get_ivs_from_value(stat=stat,
                                             base=garchomp.base.get_stat(stat),
                                             ev=garchomp.get_ev(stat),
                                             level=garchomp.level,
                                             nature=garchomp.nature,
                                             value=value))

        #

        comfey_stat_ranges = [(Stat.HP, 51, 126, 158), (Stat.ATTACK, 52, 64, 114),
                              (Stat.DEFENSE, 90, 99, 156), (Stat.SP_ATTACK, 82, 91, 147),
                              (Stat.SP_DEFENSE, 110, 117, 178), (Stat.SPEED, 100, 108, 167)]

        for stat, base, mn, mx in comfey_stat_ranges:
            self.assertTupleEqual((mn, mx), get_stat_range(stat, base, 50))

    #

    #

    def test_stat_templates(self):

        template = StatTemplate(stat=Stat.ATTACK, ev=0, iv=IV_MAX, level=50)
        results = get_combinations_for_value(template, 150)
        self.assertSetEqual({130, 117, 147}, {b for r in results for b in (r.base or ())})
        self.assertTrue(all(r.is_complete() for r in results))

        template = StatTemplate(stat=Stat.ATTACK, ev=(0, StatPoint.limit()), iv=IV_MAX, level=50)
        results = get_combinations_for_value(template, 150)
        self.assertSetEqual({(98, 32, "Neutral"), (115, 32, "Hindering"), (130, 0, "Neutral"),
                             (117, 0, "Boosting"), (85, 32, "Boosting"), (147, 0, "Hindering")},
                            {b for r in results for b in
                             itertools.product(r.base,
                                               (ev.number for ev in r.ev),
                                               (n.get_mod_as_string(Stat.ATTACK) for n in r.nature))})
        self.assertTrue(all(r.is_complete() for r in results))

        template = StatTemplate(stat=Stat.ATTACK, base=130, ev=0, iv=IV_MAX, level=50,
                                nature=[Nature.build_neutral(), Nature.build_boosting(Stat.ATTACK)])
        results = get_combinations_for_value(template, 150)
        self.assertSetEqual({"Neutral"}, {n.get_mod_as_string(Stat.ATTACK) for r in results for n in r.nature})
        self.assertTrue(all(r.is_complete() for r in results))

        template = StatTemplate(stat=Stat.ATTACK, base=100, iv=IV_MAX, level=50)
        results = get_combinations_for_value(template, 150)
        self.assertSetEqual({17, 30}, {e.number for r in results for e in (r.ev or ())})
        self.assertTrue(all(r.is_complete() for r in results))

        # template = StatTemplate(stat=Stat.HP, ev=EV.ev_max(), iv=IV_MAX)
        # results = get_combinations_for_value(template, 350)
        # self.assertSetEqual({(73, 100), (243, 50)}, {(b, lev) for r in results for b in (r.base or ())
        #                                              for lev in (r.level or ())})
        # self.assertTrue(all(r.is_complete() for r in results))

        template = StatTemplate(stat=Stat.HP)
        results = get_combinations_for_value(template, 1000)
        self.assertEqual(0, len(list(results)))
        self.assertTrue(all(r.is_complete() for r in results))

    def test_damage(self):

        base_stats = BaseStats(attack=130, defense=95, special_attack=80, special_defense=85, speed=102, hp=108)
        garchomp = PokemonData(name=Name(default="Garchomp"), variant=Variant(),
                               typing=Typing.of(Type.DRAGON, Type.GROUND),
                               stats=base_stats, abilities=AbilityList(primary=Ability(name="Rough Skin")),
                               move_list=MoveList(),
                               dex_entries=DexEntryCollection.of(), misc_info=MiscInfo())
        attacker = Pokemon(data=garchomp,
                           moveset=MoveSet(),
                           ability=garchomp.abilities.primary,
                           item=None,
                           stats=Stats.of(base=base_stats,
                                          evs=[EV(stat, 0) for stat in NUMBER_STATS],
                                          ivs=[IV(stat, 31) for stat in NUMBER_STATS],
                                          nature=Nature.Adamant,
                                          level=50,
                                          modifiers=[]))
        defender = Pokemon(data=garchomp,
                           moveset=MoveSet(),
                           ability=garchomp.abilities.primary,
                           item=None,
                           stats=Stats.of(base=base_stats,
                                          evs=[EV(stat, 0) for stat in NUMBER_STATS],
                                          ivs=[IV(stat, 31) for stat in NUMBER_STATS],
                                          nature=Nature.Adamant,
                                          level=50,
                                          modifiers=[]))
        board_state = BoardState(entities=[])

        eq = DamagingMove(name="Earthquake", type=Type.GROUND, base_power=100, offense_stat=Stat.ATTACK,
                          properties=MoveProperties.MULTI_TARGET)
        stomping = DamagingMove(name="Stomping Tantrum", type=Type.GROUND, base_power=75, offense_stat=Stat.ATTACK)
        d_claw = DamagingMove(name="Dragon Claw", type=Type.DRAGON, base_power=80, offense_stat=Stat.ATTACK)
        poison_jab = DamagingMove(name="Poison Jab", type=Type.POISON, base_power=80, offense_stat=Stat.ATTACK)
        ice_beam = DamagingMove(name="Ice Beam", type=Type.ICE, base_power=90, offense_stat=Stat.SP_ATTACK)
        t_punch = DamagingMove(name="Thunder Punch", type=Type.ELECTRIC, base_power=75, offense_stat=Stat.ATTACK)
        f_punch = DamagingMove(name="Fire Punch", type=Type.FIRE, base_power=75, offense_stat=Stat.ATTACK)
        body_press = DamagingMove(name="Body Press", type=Type.FIGHTING, base_power=80, offense_stat=Stat.DEFENSE,
                                  defense_stat=Stat.DEFENSE)
        trailblaze = DamagingMove(name="Trailblaze", type=Type.GRASS, base_power=50, offense_stat=Stat.ATTACK)
        fish_rend = DamagingMove(name="Fishious Rend", type=Type.WATER, base_power=170, offense_stat=Stat.ATTACK,
                                 properties=MoveProperties.BITING)

        report = calculate_damage(attacker, defender, move=eq, board_state=board_state)
        self.assertListEqual([61, 63, 63, 64, 64, 66, 66, 67, 67, 69, 69, 70, 70, 72, 72, 73],
                             report.rolls)
        self.assertEqual("0+ Atk Garchomp Earthquake vs. 0 HP / 0 Def Garchomp: 61-73 (33.3 - 39.8%) -- guaranteed OHKO",
                         str(report))
        
        board_state.is_doubles = False
        report = calculate_damage(attacker, defender, move=eq, board_state=board_state)
        self.assertListEqual([82, 82, 84, 85, 85, 87, 88, 88, 90, 91, 91, 93, 94, 94, 96, 97],
                             report.rolls)
        # self.assertEqual("0+ Atk Garchomp Earthquake vs. 0 HP / 0 Def Garchomp: 82-97 (44.8 - 53%) -- 26.17% chance to 2HKO", str(report))
        board_state.is_doubles = True

        self.assertListEqual([61, 63, 63, 64, 64, 66, 66, 67, 67, 69, 69, 70, 70, 72, 72, 73],
                             list(get_damage_rolls(attacker, defender, move=stomping, board_state=board_state)))

        report = calculate_damage(attacker, defender, move=d_claw, board_state=board_state)
        self.assertListEqual([132, 132, 134, 134, 138, 138, 140, 140, 144, 144, 146, 146, 150, 150, 152, 156],
                             report.rolls)
        # self.assertEqual("", str(report))

        report = calculate_damage(attacker, defender, move=poison_jab, board_state=board_state)
        self.assertListEqual([22, 22, 22, 22, 23, 23, 23, 23, 24, 24, 24, 24, 25, 25, 25, 26],
                             report.rolls)
        # self.assertEqual("", str(report))

        report = calculate_damage(attacker, defender, move=t_punch, board_state=board_state)
        self.assertListEqual([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             report.rolls)
        # self.assertEqual("", str(report))

        # Test weather
        report = calculate_damage(attacker, defender, move=f_punch, board_state=board_state)
        self.assertListEqual([20, 21, 21, 21, 21, 22, 22, 22, 22, 23, 23, 23, 23, 24, 24, 24],
                             report.rolls)
        # self.assertEqual("", str(report))

        board_state.weather = Weather.SUN
        report = calculate_damage(attacker, defender, move=f_punch, board_state=board_state)
        self.assertListEqual([31, 31, 31, 32, 32, 32, 33, 33, 33, 34, 34, 35, 35, 35, 36, 36],
                             report.rolls)
        # self.assertEqual("", str(report))

        board_state.weather = Weather.RAIN
        report = calculate_damage(attacker, defender, move=f_punch, board_state=board_state)
        self.assertListEqual([10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 12],
                             report.rolls)
        # self.assertEqual("", str(report))
        board_state.weather = Weather.NONE

        # Test terrain
        report = calculate_damage(attacker, defender, move=trailblaze, board_state=board_state)
        self.assertListEqual([28, 28, 28, 29, 29, 29, 30, 30, 30, 31, 31, 31, 32, 32, 32, 33],
                             report.rolls)
        # self.assertEqual("", str(report))

        board_state.terrain = Terrain.GRASSY
        report = calculate_damage(attacker, defender, move=trailblaze, board_state=board_state)
        self.assertListEqual([36, 36, 37, 37, 38, 38, 39, 39, 39, 40, 40, 41, 41, 42, 42, 43],
                             report.rolls)
        # self.assertEqual("", str(report))
        board_state.terrain = Terrain.NONE

        # Test screens
        board_state.effects = [BoardEffect(type=BoardEffectType.REFLECT,
                                           targets=[Entity(typing=defender.data.typing,
                                                           ability=defender.ability,
                                                           stats=defender.stats,
                                                           team=1,
                                                           item=defender.item)])]
        report = calculate_damage(attacker, defender, move=stomping, board_state=board_state)
        self.assertListEqual([41, 42, 42, 43, 43, 44, 44, 45, 45, 46, 46, 47, 47, 48, 48, 49],
                             report.rolls)
        # self.assertEqual("", str(report))

        board_state.is_doubles = False
        report = calculate_damage(attacker, defender, move=stomping, board_state=board_state)
        self.assertListEqual([30, 31, 31, 32, 32, 33, 33, 33, 33, 34, 34, 35, 35, 36, 36, 36],
                             report.rolls)
        # self.assertEqual("", str(report))

        board_state.is_doubles = True
        board_state.effects = [BoardEffect(type=BoardEffectType.AURORA_VEIL,
                                           targets=[Entity(typing=defender.data.typing,
                                                           ability=defender.ability,
                                                           stats=defender.stats,
                                                           team=1,
                                                           item=defender.item)])]
        report = calculate_damage(attacker, defender, move=stomping, board_state=board_state)
        self.assertListEqual([41, 42, 42, 43, 43, 44, 44, 45, 45, 46, 46, 47, 47, 48, 48, 49],
                             report.rolls)
        # self.assertEqual("", str(report))
        board_state.effects = [BoardEffect(type=BoardEffectType.LIGHT_SCREEN,
                                           targets=[Entity(typing=defender.data.typing,
                                                           ability=defender.ability,
                                                           stats=defender.stats,
                                                           team=1,
                                                           item=defender.item)])]
        report = calculate_damage(attacker, defender, move=stomping, board_state=board_state)
        self.assertListEqual([61, 63, 63, 64, 64, 66, 66, 67, 67, 69, 69, 70, 70, 72, 72, 73],
                             report.rolls)
        # self.assertEqual("", str(report))

        report = calculate_damage(attacker, defender, move=ice_beam, board_state=board_state)
        self.assertListEqual([77, 80, 80, 80, 83, 83, 83, 85, 85, 85, 88, 88, 88, 91, 91, 93],
                             report.rolls)
        # self.assertEqual("0- SpA Garchomp Ice Beam vs. 0 HP / 0 SpD Garchomp through Light Screen: 77-93 (42 - 50.8%) -- 1.95% chance to 2HKO", str(report))

        board_state.effects = []
        report = calculate_damage(attacker, defender, move=ice_beam, board_state=board_state)
        self.assertListEqual([116, 120, 120, 120, 124, 124, 124, 128, 128, 128, 132, 132, 132, 136, 136, 140],
                             report.rolls)
        # self.assertEqual("0- SpA Garchomp Ice Beam vs. 0 HP / 0 SpD Garchomp: 116-140 (63.3 - 76.5%) -- guaranteed 2HKO", str(report))

        report = calculate_damage(attacker, defender, move=body_press, board_state=board_state)
        self.assertListEqual([31, 31, 32, 32, 32, 33, 33, 34, 34, 34, 35, 35, 35, 36, 36, 37],
                             report.rolls)
        # self.assertEqual("", str(report))

        # Test ability effects
        report = calculate_damage(attacker, defender, move=fish_rend, board_state=board_state)
        self.assertListEqual([92, 93, 94, 95, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 109],
                             report.rolls)
        # self.assertEqual("", str(report))

        attacker.ability = Ability(name="Strong Jaw")
        report = calculate_damage(attacker, defender, move=fish_rend, board_state=board_state)
        self.assertListEqual([137, 139, 140, 142, 144, 145, 147, 149, 150, 152, 153, 155, 157, 158, 160, 162],
                             report.rolls)
        # self.assertEqual("0+ Atk Strong Jaw Garchomp Crunch (170 BP) vs. 0 HP / 0 Def Garchomp: 137-162 (74.8 - 88.5%) -- guaranteed 2HKO", str(report))

        defender.ability = Ability(name="Water Absorb")
        report = calculate_damage(attacker, defender, move=fish_rend, board_state=board_state)
        self.assertListEqual([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             report.rolls)
        # self.assertEqual("", str(report))

        defender.ability = Ability(name="Levitate")
        report = calculate_damage(attacker, defender, move=stomping, board_state=board_state)
        self.assertListEqual([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             report.rolls)
        # self.assertEqual("", str(report))

        attacker.ability = attacker.data.abilities.primary
        defender.ability = defender.data.abilities.primary

        attacker.stats.add_modifiers(StatModifier(Stat.ATTACK, 2))
        report = calculate_damage(attacker, defender, move=stomping, board_state=board_state)
        self.assertListEqual([121, 123, 124, 126, 127, 129, 130, 132, 133, 135, 136, 138, 139, 141, 142, 144],
                             report.rolls)
        # self.assertEqual("", str(report))

        defender.stats.add_modifiers(StatModifier(Stat.DEFENSE, 4))
        report = calculate_damage(attacker, defender, move=stomping, board_state=board_state)
        self.assertListEqual([42, 42, 42, 43, 43, 43, 45, 45, 45, 46, 46, 46, 48, 48, 48, 49],
                             report.rolls)
        # self.assertEqual("+2 0+ Atk Garchomp Stomping Tantrum vs. +4 0 HP / 0 Def Garchomp: 42-49 (22.9 - 26.7%) -- 30.99% chance to 4HKO", str(report))

        report = calculate_damage(attacker, defender, move=stomping, board_state=board_state,
                                  critical=True)
        self.assertListEqual([183, 184, 187, 189, 192, 193, 196, 198, 199, 202, 204, 207, 208, 211, 213, 216],
                             report.rolls)
        # self.assertEqual("+2 0+ Atk Garchomp Stomping Tantrum vs. 0 HP / 0 Def Garchomp on a critical hit: 183-216 (100 - 118%) -- guaranteed OHKO", str(report))

        defender.stats.add_modifiers(StatModifier(Stat.DEFENSE, -5))  # To -1
        report = calculate_damage(attacker, defender, move=stomping, board_state=board_state)
        self.assertListEqual([184, 186, 189, 190, 193, 195, 196, 199, 201, 204, 205, 208, 210, 213, 214, 217],
                             report.rolls)
        # self.assertEqual("+2 0+ Atk Garchomp Stomping Tantrum vs. -1 0 HP / 0 Def Garchomp: 184-217 (100.5 - 118.5%) -- guaranteed OHKO", str(report))

        attacker.stats.add_modifiers(StatModifier(Stat.ATTACK, -4))  # To -2
        report = calculate_damage(attacker, defender, move=stomping, board_state=board_state)
        self.assertListEqual([46, 46, 48, 48, 48, 49, 49, 51, 51, 51, 52, 52, 52, 54, 54, 55],
                             report.rolls)
        # self.assertEqual("", str(report))

        report = calculate_damage(attacker, defender, move=stomping, board_state=board_state,
                                  critical=True)
        self.assertListEqual([138, 139, 141, 142, 145, 147, 148, 150, 151, 153, 154, 156, 157, 159, 160, 163],
                             report.rolls)
        # self.assertEqual("0+ Atk Garchomp Stomping Tantrum vs. -1 0 HP / 0 Def Garchomp on a critical hit: 138-163 (75.4 - 89%) -- guaranteed 2HKO", str(report))
