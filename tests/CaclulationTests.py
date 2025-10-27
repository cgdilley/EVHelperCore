from unittest import TestCase

from EVHelperCore.Calculations.Stats import *
from EVHelperCore.Calculations.StatTemplates import get_combinations_for_value
from EVHelperCore.Calculations.Damage import *

import itertools


class TestCalculations(TestCase):

    def test_stat_calc(self):
        # Example from https://bulbapedia.bulbagarden.net/wiki/Statistic#Determination_of_stats
        garchomp = Stats.of(base=BaseStats(attack=130, defense=95, special_attack=80,
                                           special_defense=85, speed=102, hp=108),
                            evs=[EV(Stat.HP, 74, round_off=True),
                                 EV(Stat.ATTACK, 190, round_off=True),
                                 EV(Stat.DEFENSE, 91, round_off=True),
                                 EV(Stat.SP_ATTACK, 48, round_off=True),
                                 EV(Stat.SP_DEFENSE, 84, round_off=True),
                                 EV(Stat.SPEED, 23, round_off=True)],
                            ivs=[IV(Stat.HP, 24),
                                 IV(Stat.ATTACK, 12),
                                 IV(Stat.DEFENSE, 30),
                                 IV(Stat.SP_ATTACK, 16),
                                 IV(Stat.SP_DEFENSE, 23),
                                 IV(Stat.SPEED, 5)],
                            nature=Nature.Adamant,
                            level=78,
                            modifiers=[])

        real_stats = [(Stat.HP, 289), (Stat.ATTACK, 278), (Stat.DEFENSE, 193),
                      (Stat.SP_ATTACK, 135), (Stat.SP_DEFENSE, 171), (Stat.SPEED, 171)]

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
                                             value=value))
            self.assertIn(garchomp.get_iv(stat),
                          get_ivs_from_value(stat=stat,
                                             base=garchomp.base.get_stat(stat),
                                             ev=garchomp.get_ev(stat),
                                             level=garchomp.level,
                                             nature=garchomp.nature,
                                             value=value))

        #

        comfey_stat_ranges = [(Stat.HP, 51, 111, 158), (Stat.ATTACK, 52, 51, 114),
                              (Stat.DEFENSE, 90, 85, 156), (Stat.SP_ATTACK, 82, 78, 147),
                              (Stat.SP_DEFENSE, 110, 103, 178), (Stat.SPEED, 100, 94, 167)]

        for stat, base, mn, mx in comfey_stat_ranges:
            self.assertTupleEqual((mn, mx), get_stat_range(stat, base, 50))

    #

    #

    def test_stat_templates(self):

        template = StatTemplate(stat=Stat.ATTACK, ev=0, iv=IV_MAX, level=50)
        results = get_combinations_for_value(template, 150)
        self.assertSetEqual({130, 117, 147}, {b for r in results for b in r.base})
        self.assertTrue(all(r.is_complete() for r in results))

        template = StatTemplate(stat=Stat.ATTACK, ev=(0, EV_MAX), iv=IV_MAX, level=50)
        results = get_combinations_for_value(template, 150)
        self.assertSetEqual({(98, 252, "Neutral"), (115, 252, "Hindering"), (130, 0, "Neutral"),
                             (117, 0, "Boosting"), (85, 252, "Boosting"), (147, 0, "Hindering")},
                            {b for r in results for b in
                             itertools.product(r.base, r.ev, (n.get_mod_as_string(Stat.ATTACK) for n in r.nature))})
        self.assertTrue(all(r.is_complete() for r in results))

        template = StatTemplate(stat=Stat.ATTACK, base=130, ev=0, iv=IV_MAX, level=50,
                                nature=[Nature.build_neutral(), Nature.build_boosting(Stat.ATTACK)])
        results = get_combinations_for_value(template, 150)
        self.assertSetEqual({"Neutral"}, {n.get_mod_as_string(Stat.ATTACK) for r in results for n in r.nature})
        self.assertTrue(all(r.is_complete() for r in results))

        template = StatTemplate(stat=Stat.ATTACK, base=100, iv=IV_MAX, level=50)
        results = get_combinations_for_value(template, 150)
        self.assertSetEqual({132, 136, 236, 240}, {e for r in results for e in r.ev})
        self.assertTrue(all(r.is_complete() for r in results))

        template = StatTemplate(stat=Stat.HP, ev=EV_MAX, iv=IV_MAX)
        results = get_combinations_for_value(template, 350)
        self.assertSetEqual({(73, 100), (243, 50)}, {(b, lev) for r in results for b in r.base for lev in r.level})
        self.assertTrue(all(r.is_complete() for r in results))

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
                           ability=Ability(name="Rough skin"),
                           item="",
                           stats=Stats.of(base=base_stats,
                                          evs=[EV(stat, 0) for stat in NUMBER_STATS],
                                          ivs=[IV(stat, 31) for stat in NUMBER_STATS],
                                          nature=Nature.Adamant,
                                          level=50,
                                          modifiers=[]))
        defender = Pokemon(data=garchomp,
                           moveset=MoveSet(),
                           ability=Ability(name="Rough skin"),
                           item="",
                           stats=Stats.of(base=base_stats,
                                          evs=[EV(stat, 0) for stat in NUMBER_STATS],
                                          ivs=[IV(stat, 31) for stat in NUMBER_STATS],
                                          nature=Nature.Adamant,
                                          level=50,
                                          modifiers=[]))

        move = DamagingMove(name="Earthquake", type=Type.GROUND, base_power=100, offense_stat=Stat.ATTACK)
        self.assertListEqual([82, 82, 84, 85, 85, 87, 88, 88, 90, 91, 91, 93, 94, 94, 96, 97],
                             list(calculate_damage(attacker, defender, move)))

        move = DamagingMove(name="Dragon Claw", type=Type.DRAGON, base_power=80, offense_stat=Stat.ATTACK)
        self.assertListEqual([132, 132, 134, 134, 138, 138, 140, 140, 144, 144, 146, 146, 150, 150, 152, 156],
                             list(calculate_damage(attacker, defender, move)))

        move = DamagingMove(name="Poison Jab", type=Type.POISON, base_power=80, offense_stat=Stat.ATTACK)
        self.assertListEqual([22, 22, 22, 22, 23, 23, 23, 23, 24, 24, 24, 24, 25, 25, 25, 26],
                             list(calculate_damage(attacker, defender, move)))

        move = DamagingMove(name="Thunder Punch", type=Type.ELECTRIC, base_power=75, offense_stat=Stat.ATTACK)
        self.assertListEqual([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             list(calculate_damage(attacker, defender, move)))

        move = DamagingMove(name="Ice Beam", type=Type.ICE, base_power=90, offense_stat=Stat.SP_ATTACK)
        self.assertListEqual([116, 120, 120, 120, 124, 124, 124, 128, 128, 128, 132, 132, 132, 136, 136, 140],
                             list(calculate_damage(attacker, defender, move)))

        move = DamagingMove(name="Body Press", type=Type.FIGHTING, base_power=80, offense_stat=Stat.DEFENSE,
                            defense_stat=Stat.DEFENSE)
        self.assertListEqual([31, 31, 32, 32, 32, 33, 33, 34, 34, 34, 35, 35, 35, 36, 36, 37],
                             list(calculate_damage(attacker, defender, move)))

        attacker.stats.add_modifiers(StatModifier(Stat.ATTACK, 2))
        move = DamagingMove(name="Earthquake", type=Type.GROUND, base_power=100, offense_stat=Stat.ATTACK,
                            defense_stat=Stat.DEFENSE)
        self.assertListEqual([162, 165, 166, 168, 169, 172, 174, 175, 178, 180, 181, 183, 186, 187, 189, 192],
                             list(calculate_damage(attacker, defender, move)))

        defender.stats.add_modifiers(StatModifier(Stat.DEFENSE, 4))
        self.assertListEqual([55, 55, 57, 57, 58, 58, 60, 60, 60, 61, 61, 63, 63, 64, 64, 66],
                             list(calculate_damage(attacker, defender, move)))
        # self.assertListEqual([],
        #                      list(calculate_damage(attacker, defender, move, critical=True)))
