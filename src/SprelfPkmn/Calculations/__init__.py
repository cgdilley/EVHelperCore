"""
Relevant calculations emulating those found in-game
"""
from .Damage import DamageReport, calculate_damage, get_damage_rolls
from .Stats import get_stat_value_from_info, get_base_stat_from_value, get_evs_from_value, get_ivs_from_value, \
    get_stat_range, get_stat_value
from .StatTemplates import get_combinations_for_value
