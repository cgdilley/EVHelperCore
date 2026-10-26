from __future__ import annotations

from SprelfPkmn.Objects import *
from SprelfPkmn.Utils import ShowdownUtils, FormatUtils
from SprelfPkmn.Implementations import MoveDataMap
from typing import Iterable
import re


def parse_pokepaste(paste: str, database: PokemonDataMap, moves: MoveDataMap) -> list[Pokemon]:
    lines = (_l.strip() for _l in paste.splitlines())
    return list(_parse_pokepaste_lines(lines, database, moves))



def _parse_pokepaste_lines(lines: Iterable[str],
                           database: PokemonDataMap,
                           moves: MoveDataMap) -> Iterable[Pokemon]:
    name_and_item = re.compile(r"^([^(@]+)( \(([\w\-' ]+)\))?( \([MF]\))?( @ (.+))?$")
    ability = re.compile(r"^Ability: (.+)$")
    stat_blocks = re.compile(r"^([IE]Vs): (((\d+) (\w{2,3}))( / ((\d+) (\w{2,3})))*)$")
    stat_individual = re.compile(r"(\d+) (\w{2,3})")
    nature = re.compile(r"^(.+) Nature$")
    move = re.compile(r"^ *- (.+)$")
    level = re.compile(r"^Level: (\d+)$")

    curr = dict()
    for line in lines:
        if not line.strip():
            if all(f in curr for f in Pokemon.__json_model__.keys()):
                yield Pokemon(**curr)
            curr = dict()
            continue

        if len(curr) == 0:
            if m := name_and_item.match(line):
                if m.group(3):
                    name = m.group(3)
                else:
                    name = m.group(1)
                name, variant = ShowdownUtils.parse_showdown_name(name)
                name_matches = database.name(name)
                for match in name_matches:
                    if match.variant == variant:
                        mon = match
                        break
                else:
                    continue
                curr["data"] = mon
                curr["ability"] = mon.abilities.primary
                curr["typing"] = mon.typing
                curr["stats"] = Stats.of(base=mon.stats, evs=(), ivs=(), level=50, nature=Nature.Serious)
                curr["item"] = Item(name=m.group(6)) if m.group(6) else None
                curr["gender"] = None
                if g := m.group(4):
                    if g == "M":
                        curr["gender"] = Gender.MALE
                    elif g == "F":
                        curr["gender"] = Gender.FEMALE
                curr["moveset"] = MoveSet()
        else:
            if m := ability.match(line):
                curr["ability"] = Ability(name=m.group(1))

            #

            elif m := stat_blocks.match(line):
                if not isinstance(stats := curr.get("stats"), Stats):
                    continue
                blocks = [x.strip() for x in m.group(2).split("/")]
                for block in blocks:
                    if n := stat_individual.match(block):
                        s = _parse_stat(n.group(2))
                        if s is None:
                            continue
                        if m.group(1) == "EVs":
                            stats.evs[s] = StatPoint(number=int(n.group(1)))
                        elif m.group(1) == "IVs":
                            stats.ivs[s] = int(n.group(1))

            #

            elif m := nature.match(line):
                if not isinstance(stats := curr.get("stats"), Stats):
                    continue
                n = getattr(Nature, m.group(1).capitalize())
                if isinstance(n, Nature):
                    stats.nature = n

            elif m := level.match(line):
                if not isinstance(stats := curr.get("stats"), Stats):
                    continue
                stats.level = int(m.group(1))

            #

            elif m := move.match(line):
                if not isinstance(moveset := curr.get("moveset"), MoveSet) or not m.group(1):
                    continue
                move_name = m.group(1)
                match = moves.name(move_name)
                if match is None:
                    continue
                moveset.moves.append(match)

    if all(f in curr for f in Pokemon.__json_model__.keys()):
        yield Pokemon(**curr)


def _parse_stat(s: str) -> Stat | None:
    match s.lower():
        case "hp":
            return Stat.HP
        case "atk":
            return Stat.ATTACK
        case "def":
            return Stat.DEFENSE
        case "spa":
            return Stat.SP_ATTACK
        case "spd":
            return Stat.SP_DEFENSE
        case "spe":
            return Stat.SPEED
    return None