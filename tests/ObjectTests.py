from unittest import TestCase

from SprelfPkmn.Objects import *
from SprelfPkmn.Exceptions import *


class TestObjects(TestCase):

    def test_name(self):
        name_obj = Name(default="a", localized={"de": "b"},
                        variant=PrefixVariantName(default="c", localized={"de": "d"}))
        name_json = {
            "default": "a",
            "localized": {
                "de": "b"
            },
            "variant": {
                "type": "prefix",
                "default": "c",
                "localized": {
                    "de": "d"
                }
            }
        }

        name_obj2 = Name(default="e", localized={})
        name_json2 = {
            "default": "e"
        }

        self.assertDictEqual(name_json, name_obj.to_json())
        self.assertDictEqual(name_json, Name.from_json(name_obj.to_json()).to_json())
        self.assertDictEqual(name_json2, name_obj2.to_json())
        self.assertDictEqual(name_json2, Name.from_json(name_obj2.to_json()).to_json())

        self.assertEqual("c a", name_obj.name)
        self.assertEqual("c a", name_obj.full_name())
        self.assertEqual("d b", name_obj.full_name("de"))
        with self.assertRaises(LocalizationError):
            name_obj.full_name("fr")
        self.assertEqual("a", name_obj.localized_name())
        self.assertEqual("b", name_obj.localized_name("de"))
        with self.assertRaises(LocalizationError):
            name_obj.localized_name("fr")

        self.assertEqual("e", name_obj2.name)
        self.assertEqual("e", name_obj2.localized_name())
        self.assertEqual("e", name_obj2.full_name())
        with self.assertRaises(LocalizationError):
            name_obj2.localized_name("de")
        with self.assertRaises(LocalizationError):
            name_obj2.full_name("de")

        from_json = Name.from_json(name_json)
        self.assertIsInstance(from_json.variant, PrefixVariantName)
        self.assertEqual(name_obj.name, from_json.name)
        self.assertEqual(name_obj.full_name("de"), from_json.full_name("de"))
        self.assertEqual(name_obj.localized_name(), from_json.localized_name())
        self.assertEqual(name_obj.localized_name("de"), from_json.localized_name("de"))

        from_json2 = Name.from_json(name_json2)
        self.assertIsNone(from_json2.variant)
        self.assertEqual(name_obj2.name, from_json2.name)
        self.assertEqual(name_obj2.localized_name(), from_json2.localized_name())

    def test_variant(self):

        self.assertFalse(Variant(region=Region.NONE).is_regional())
        self.assertTrue(Variant(region=Region.KANTO).is_regional())

        self.assertFalse(Variant(mega_type=MegaType.NONE).is_mega())
        self.assertTrue(Variant(mega_type=MegaType.NORMAL).is_mega())

        self.assertFalse(Variant(gender=Gender.IRRELEVANT).is_gender())
        self.assertTrue(Variant(gender=Gender.MALE).is_gender())

        self.assertFalse(Variant(form=None).is_form())
        self.assertTrue(Variant(form="Incarnate").is_form())

        variant1 = Variant(region=Region.KANTO,
                           mega_type=MegaType.NORMAL,
                           gender=Gender.MALE,
                           form="Incarnate")
        variant_json1 = {
            "region": "KANTO",
            "mega_type": "NORMAL",
            "gender": "MALE",
            "form": "Incarnate"
        }

        self.assertDictEqual(variant_json1, variant1.to_json())
        self.assertDictEqual(variant_json1, Variant.from_json(variant1.to_json()).to_json())

        self.assertDictEqual(dict(), Variant().to_json())

    def test_typing(self):

        mono = Typing.of(Type.FIRE)
        dual = Typing.of(Type.FIRE, Type.WATER)

        self.assertTrue(mono.is_mono_type())
        self.assertFalse(mono.is_dual_type())
        self.assertFalse(dual.is_mono_type())
        self.assertTrue(dual.is_dual_type())

        mono_json = {
            "primary": "FIRE"
        }
        dual_json = {
            "primary": "FIRE",
            "secondary": "WATER"
        }

        self.assertDictEqual(mono_json, mono.to_json())
        self.assertDictEqual(mono_json, Typing.from_json(mono.to_json()).to_json())
        self.assertDictEqual(dual_json, dual.to_json())
        self.assertDictEqual(dual_json, Typing.from_json(dual.to_json()).to_json())

    def test_stats(self):

        # BASE STATS

        base = BaseStats(attack=1, defense=2, special_attack=3, special_defense=4, speed=5, hp=6)
        base_json = {
            "ATTACK": 1,
            "DEFENSE": 2,
            "SP_ATTACK": 3,
            "SP_DEFENSE": 4,
            "SPEED": 5,
            "HP": 6
        }

        self.assertDictEqual(base_json, base.to_json())
        self.assertDictEqual(base_json, BaseStats.from_json(base_json).to_json())

        for bs in (base, BaseStats.from_json(base_json)):
            self.assertEqual(1, bs.get_stat(Stat.ATTACK))
            self.assertEqual(2, bs.get_stat(Stat.DEFENSE))
            self.assertEqual(3, bs.get_stat(Stat.SP_ATTACK))
            self.assertEqual(4, bs.get_stat(Stat.SP_DEFENSE))
            self.assertEqual(5, bs.get_stat(Stat.SPEED))
            self.assertEqual(6, bs.get_stat(Stat.HP))

            with self.assertRaises(StatError):
                bs.get_stat(Stat.CRITICAL)

        # STAT MODIFIERS

        self.assertEqual(3, StatModifier(Stat.ATTACK, 3).modifier)
        self.assertEqual(6, StatModifier(Stat.ATTACK, 7, adjust_to_cap=True).modifier)
        self.assertEqual(-6, StatModifier(Stat.ATTACK, -7, adjust_to_cap=True).modifier)
        self.assertEqual(3, StatModifier(Stat.CRITICAL, 4, adjust_to_cap=True).modifier)
        self.assertEqual(0, StatModifier(Stat.CRITICAL, -1, adjust_to_cap=True).modifier)
        for stat, fail_value in [(Stat.ATTACK, 7), (Stat.ATTACK, -7),
                                 (Stat.CRITICAL, 4), (Stat.CRITICAL, -1),
                                 (Stat.HP, 0)]:
            with self.assertRaises(StatError):
                _ = StatModifier(stat, fail_value)

        # EVs

        self.assertEqual(252, EV(Stat.ATTACK, EV_MAX).value)
        self.assertEqual(248, EV(Stat.ATTACK, EV_MAX - 1, round_off=True).value)
        for stat, fail_value in [(Stat.ATTACK, 1), (Stat.ATTACK, -1), (Stat.ATTACK, -4),
                                 (Stat.ATTACK, 256), (Stat.CRITICAL, 0)]:
            with self.assertRaises(StatError):
                _ = EV(stat, fail_value)

        # IVs

        self.assertEqual(31, IV(Stat.ATTACK, IV_MAX).value)
        for stat, fail_value in [(Stat.ATTACK, -1), (Stat.ATTACK, 32), (Stat.CRITICAL, 0)]:
            with self.assertRaises(StatError):
                _ = IV(stat, fail_value)

        # NATURES

        nature = Nature.Adamant
        self.assertEqual(nature, Nature(Stat.ATTACK, Stat.SP_ATTACK))
        self.assertEqual("Adamant", nature.name)
        self.assertEqual(1.1, nature.get_modifier(Stat.ATTACK))
        self.assertEqual(0.9, nature.get_modifier(Stat.SP_ATTACK))
        self.assertEqual(1, nature.get_modifier(Stat.DEFENSE))
        self.assertEqual(1, Nature(Stat.ATTACK, Stat.ATTACK).get_modifier(Stat.ATTACK))

        with self.assertRaises(StatError):
            _ = Nature(Stat.ATTACK, Stat.CRITICAL)
        with self.assertRaises(StatError):
            _ = Nature(Stat.HP, Stat.ATTACK)

        # STATS

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
                            nature=Nature(Stat.ATTACK, Stat.SP_ATTACK),
                            level=78,
                            modifiers=[])

        garchomp_json = {
            "base": {
                "ATTACK": 130,
                "DEFENSE": 95,
                "SP_ATTACK": 80,
                "SP_DEFENSE": 85,
                "SPEED": 102,
                "HP": 108
            },
            "evs": {
                "ATTACK": 188,
                "DEFENSE": 88,
                "SP_ATTACK": 48,
                "SP_DEFENSE": 84,
                "SPEED": 20,
                "HP": 72
            },
            "ivs": {
                "ATTACK": 12,
                "DEFENSE": 30,
                "SP_ATTACK": 16,
                "SP_DEFENSE": 23,
                "SPEED": 5,
                "HP": 24
            },
            "nature": {
                "plus": "ATTACK",
                "minus": "SP_ATTACK",
                "name": "Adamant"
            },
            "level": 78
        }

        self.assertDictEqual(garchomp_json, garchomp.to_json())
        self.assertDictEqual(garchomp_json, Stats.from_json(garchomp_json).to_json())

    #

    def test_abilities(self):

        self.assertEqual("a", Ability(name="a").name)
        self.assertEqual(Ability(name="a"), Ability(name="a"))
        self.assertDictEqual({"name": "a"}, Ability(name="a").to_json())
        self.assertDictEqual({"name": "a"}, Ability.from_json({"name": "a"}).to_json())

        ability_list = AbilityList(primary=Ability(name="a"),
                                   secondary=Ability(name="b"),
                                   hidden=Ability(name="c"))
        ability_list_json = {"primary": {"name": "a"},
                             "secondary": {"name": "b"},
                             "hidden": {"name": "c"}}

        self.assertListEqual(["a", "b", "c"], [a.name if a else None for a in ability_list])
        self.assertDictEqual(ability_list_json, ability_list.to_json())
        self.assertDictEqual(ability_list_json, AbilityList.from_json(ability_list_json).to_json())

        ability_list2 = AbilityList(primary=Ability(name="a"))
        ability_list_json2 = {"primary": {"name": "a"}}

        self.assertListEqual(["a"], [a.name if a else None for a in ability_list2])
        self.assertListEqual(["a", None, None], [a.name if a else None for a in ability_list2.as_tuple()])
        self.assertDictEqual(ability_list_json2, ability_list2.to_json())
        self.assertDictEqual(ability_list_json2, AbilityList.from_json(ability_list_json2).to_json())

    #

    def test_stat_template(self):

        st1 = StatTemplate(stat=Stat.HP, base=100, ev=0, iv=0, level=50, nature=Nature(Stat.ATTACK, Stat.ATTACK))
        st_json1 = {"stat": "HP", "base": [100], "ev": [0], "iv": [0], "level": [50],
                    "nature": [{"plus": "ATTACK", "minus": "ATTACK", "name": "Hardy"}]}
        self.assertTrue(st1.is_complete())
        self.assertDictEqual(st_json1, st1.to_json())
        self.assertDictEqual(st_json1, StatTemplate.from_json(st_json1).to_json())

        st2 = StatTemplate(stat=Stat.ATTACK, base=[100, 120])
        st_json2 = {"stat": "ATTACK", "base": [100, 120]}
        self.assertFalse(st2.is_complete())
        self.assertDictEqual(st_json2, st2.to_json())
        self.assertDictEqual(st_json2, StatTemplate.from_json(st_json2).to_json())

    def test_dex_entries(self):

        entry = DexEntry(dex=Dex.GEN_1, number=1)
        entry_json = {"dex": "GEN_1", "number": 1}

        self.assertDictEqual(entry_json, entry.to_json())
        self.assertDictEqual(entry_json, DexEntry.from_json(entry_json).to_json())

        coll = DexEntryCollection.of(entry)
        coll_json = {"entries": [entry_json]}

        self.assertDictEqual(coll_json, coll.to_json())
        self.assertDictEqual(coll_json, DexEntryCollection.from_json(coll_json).to_json())
        self.assertEqual(1, coll.get_dex_num(Dex.GEN_1))
        self.assertIsNone(coll.get_dex_num(Dex.GEN_8_DLC1))

    def test_misc_info(self):

        ev_yield = EVYield((Stat.ATTACK, 1))
        ev_yield_json = {"ATTACK": 1}
        self.assertDictEqual(ev_yield_json, ev_yield.to_json())
        self.assertDictEqual(ev_yield_json, EVYield.from_json(ev_yield_json).to_json())

        evo = Evolution(frm="RATTATA", to="RATICATE", evo=LevelUpEvolutionType(level=20))
        evo_json = {"frm": "RATTATA", "to": "RATICATE", "evo": {"type": "level_up", "level": 20}}
        self.assertDictEqual(evo_json, evo.to_json())
        self.assertDictEqual(evo_json, Evolution.from_json(evo_json).to_json())

        evo_line = EvolutionLine.of(
            "POLIWAG",
            (Evolution(frm="POLIWAG", to="POLIWHIRL", evo=LevelUpEvolutionType(level=25)),
             EvolutionLine.of(
                 "POLIWHIRL",
                 (Evolution(frm="POLIWHIRL", to="POLIWRATH", evo=UnknownEvolutionType()),
                  EvolutionLine.of("POLIWRATH")),
                 (Evolution(frm="POLIWHIRL", to="POLITOED", evo=UnknownEvolutionType()),
                  EvolutionLine.of("POLITOED")))))
        evo_line_json = {
            "pokemon_id": "POLIWAG",
            "evolutions": [
                {
                    "evo": {"type": "level_up", "level": 25},
                    "result": {
                        "pokemon_id": "POLIWHIRL",
                        "evolutions": [
                            {
                                "evo": {"type": "unknown"},
                                "result": {"pokemon_id": "POLIWRATH"}
                            },
                            {
                                "evo": {"type": "unknown"},
                                "result": {"pokemon_id": "POLITOED"}
                            }
                        ]
                    }
                }
            ]
        }
        self.assertDictEqual(evo_line_json, evo_line.to_json())
        self.assertDictEqual(evo_line_json, EvolutionLine.from_json(evo_line_json).to_json())
        self.assertListEqual(["POLIWHIRL"], list(evo_line.get_next_evolution_ids()))
        self.assertSetEqual({"POLIWRATH", "POLITOED"}, set(evo_line.get_final_evolution_ids()))
        self.assertSetEqual({"POLIWRATH", "POLITOED"},
                            set(list(evo_line.get_next_evolutions())[0].get_next_evolution_ids()))
        self.assertSetEqual({"POLIWAG", "POLIWHIRL", "POLIWRATH", "POLITOED"},
                            set(evo_line.get_all_pokemon_ids_in_line()))
        # print(evo_line.render_tree())

        #

        misc_info = MiscInfo(ev_yield=ev_yield, evolution_line=evo_line)
        misc_info_json = {"ev_yield": ev_yield_json, "evolution_line": evo_line_json}

        self.assertDictEqual(misc_info_json, misc_info.to_json())
        self.assertDictEqual(misc_info_json, MiscInfo.from_json(misc_info_json).to_json())
