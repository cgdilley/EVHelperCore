from unittest import TestCase

from SprelfPkmn import *

POKEMON = PokemonDataMap.from_file("../../Scraping/data/json/dex.json")
MOVES = MoveDataMap.from_file("../../Scraping/data/json/moves.json")

class TestCalculations(TestCase):

    def test_paste_parse(self):
        paste = f"""therm (Camerupt) @ Aspear Berry  
Ability: Magma Armor  
Level: 50  
EVs: 252 HP / 252 Def / 4 SpA  
Gentle Nature  
- Eruption  
- Heat Wave  
- Heavy Slam  
- Earth Power"""

        parsed = parse_pokepaste(paste, POKEMON, MOVES)
        print(parsed)
