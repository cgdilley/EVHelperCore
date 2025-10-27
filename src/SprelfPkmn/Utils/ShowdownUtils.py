
from SprelfPkmn.Objects import Name, VariantName, Variant, Region, MegaType, Gender


_FORM_CONVERSIONS = {
    ("Aegislash", "Shield Forme"): None,
    ("Aegislash", "Blade Forme"): "Blade",
    ("Basculin", "Red-Striped Form"): None,
    ("Basculin", "Blue-Striped Form"): "Blue-Striped",
    ("Basculin", "White-Striped Form"): "White-Striped",
    ("Burmy", "Plant Cloak"): None,
    ("Burmy", "Sandy Cloak"): "Sandy",
    ("Burmy", "Trash Cloak"): "Trash",
    ("Wormadam", "Plant Cloak"): "",
    ("Wormadam", "Sandy Cloak"): "Sandy",
    ("Wormadam", "Trash Cloak"): "Trash",
    ("Calyrex", "Shadow Rider"): "Shadow",
    ("Calyrex", "Ice Rider"): "Ice",
    ("Castform", "Sunny Form"): "Sunny",
    ("Castform", "Rainy Form"): "Rainy",
    ("Castform", "Snowy Form"): "Snowy",
    ("Darmanitan", "Standard Mode"): None,
    ("Darmanitan", "Zen Mode"): "Zen",
    ("Deoxys", "Normal Forme"): None,
    ("Deoxys", "Attack Forme"): "Attack",
    ("Deoxys", "Defense Forme"): "Defense",
    ("Deoxys", "Speed Forme"): "Speed",
    ("Dialga", "Origin Forme"): "Origin",
    ("Dudunsparce", "Two-Segment Form"): None,
    ("Dudunsparce", "Three-Segment Form"): "Three",
    ("Eevee", "Partner"): "Partner",
    ("Eiscue", "Ice Face"): None,
    ("Eiscue", "Noice Face"): "Noice",
    ("Enamorus", "Incarnate Forme"): None,
    ("Enamorus", "Therian Forme"): "Therian",
    ("Eternatus", "Eternamax"): "Eternamax",
    ("Floette", "Eternal Flower"): "Eternal",
    ("Gimmighoul", "Chest Form"): None,
    ("Gimmighoul", "Roaming Form"): "Roaming",
    ("Giratina", "Altered Forme"): None,
    ("Giratina", "Origin Forme"): "Origin",
    ("Gourgeist", "Average Size"): None,
    ("Gourgeist", "Small Size"): "Small",
    ("Gourgeist", "Large Size"): "Large",
    ("Gourgeist", "Super Size"): "Super",
    ("Greninja", "Ash-"): "Ash",
    ("Groudon", "Primal"): "Primal",
    ("Hoopa", "Confined"): None,
    ("Hoopa", "Unbound"): "Unbound",
    ("Keldeo", "Ordinary Form"): None,
    ("Keldeo", "Resolute Form"): "Resolute",
    ("Kyogre", "Primal"): "Primal",
    ("Kyurem", "Black"): "Black",
    ("Kyurem", "White"): "White",
    ("Landorus", "Incarnate Forme"): None,
    ("Landorus", "Therian Forme"): "Therian",
    ("Lycanroc", "Midday Form"): None,
    ("Lycanroc", "Dusk Form"): "Dusk",
    ("Lycanroc", "Midnight Form"): "Midnight",
    ("Maushold", "Family of Three"): None,
    ("Maushold", "Family of Four"): "Four",
    ("Meloetta", "Aria Forme"): None,
    ("Meloetta", "Pirouette Forme"): None,
    ("Minior", "Core Form"): None,
    ("Minior", "Meteor Form"): "Meteor",
    ("Morpeko", "Full Belly Mode"): None,
    ("Morpeko", "Hangry Mode"): "Hangry",
    ("Necrozma", "Dusk Mane"): "Dusk-Mane",
    ("Necrozma", "Dawn Wings"): "Dawn-Wings",
    ("Necrozma", "Ultra"): "Ultra",
    ("Ogerpon", "Teal Mask"): None,
    ("Ogerpon", "Wellspring Mask"): "Wellspring",
    ("Ogerpon", "Hearthflame Mask"): "Hearthflame",
    ("Ogerpon", "Cornerstone Mask"): "Cornerstone",
    ("Oricorio", "Baile Style"): None,
    ("Oricorio", "Pom-Pom Style"): "Pom-Pom",
    ("Oricorio", "Pa'u Style"): "Pa'u",
    ("Oricorio", "Sensu Style"): "Sensu",
    ("Palafin", "Zero Form"): None,
    ("Palafin", "Hero Form"): "Hero",
    ("Palkia", "Origin Forme"): "Origin",
    ("Pikachu", "Partner"): "Partner",
    ("Pumpkaboo", "Average Size"): None,
    ("Pumpkaboo", "Small Size"): "Small",
    ("Pumpkaboo", "Large Size"): "Large",
    ("Pumpkaboo", "Super Size"): "Super",
    ("Rockruff", "Own Tempo"): None,
    ("Rotom", "Heat"): "Heat",
    ("Rotom", "Wash"): "Wash",
    ("Rotom", "Frost"): "Frost",
    ("Rotom", "Fan"): "Fan",
    ("Rotom", "Mow"): "Mow",
    ("Shaymin", "Land Forme"): None,
    ("Shaymin", "Sky Forme"): "Sky",
    ("Squawkabilly", "Green Plumage"): None,
    ("Squawkabilly", "Blue Plumage"): "Blue",
    ("Squawkabilly", "White Plumage"): "White",
    ("Squawkabilly", "Yellow Plumage"): "Yellow",
    ("Tatsugiri", "Curly Form"): None,
    ("Tatsugiri", "Droopy Form"): "Droopy",
    ("Tatsugiri", "Stretchy Form"): "Stretchy",
    ("Tauros", "Combat Breed"): None,
    ("Tauros", "Blaze Breed"): "Blaze",
    ("Tauros", "Aqua Breed"): "Aqua",
    ("Terapagos", "Normal Form"): None,
    ("Terapagos", "Terastal Form"): "Terastal",
    ("Terapagos", "Stellar Form"): "Stellar",
    ("Thundurus", "Incarnate Forme"): None,
    ("Thundurus", "Therian Forme"): "Therian",
    ("Tornadus", "Incarnate Forme"): None,
    ("Tornadus", "Therian Forme"): "Therian",
    ("Toxtricity", "Amped Form"): None,
    ("Toxtricity", "Low Key Form"): "Low-Key",
    ("Ursaluna", "Bloodmoon"): "Bloodmoon",
    ("Urshifu", "Single Strike Style"): None,
    ("Urshifu", "Rapid Strike Style"): "Rapid-Strike",
    ("Wishiwashi", "Solo Form"): None,
    ("Wishiwashi", "School Form"): "School",
    ("Wormadam", "Plant Cloak"): None,
    ("Wormadam", "Sandy Cloak"): "Sandy",
    ("Wormadam", "Trash Cloak"): "Trash",
    ("Zacian", "Crowned Sword"): "Crowned",
    ("Zacian", "Hero of Many Battles"): None,
    ("Zamazenta", "Crowned Shield"): "Crowned",
    ("Zamazenta", "Hero of Many Battles"): None,
    ("Zygarde", "50% Forme"): None,
    ("Zygarde", "10% Forme"): "10%",
    ("Zygarde", "Complete Forme"): "Complete"
}

_FORM_CONVERSIONS_REVERSE = {(pok, showdown): full for (pok, full), showdown in _FORM_CONVERSIONS.items()}

_REGION_CONVERSIONS = {
    Region.ALOLA: "Alola",
    Region.GALAR: "Galar",
    Region.HISUI: "Hisui",
    Region.PALDEA: "Paldea",
    Region.KANTO: None,
    Region.JOHTO: None,
    Region.HOENN: None,
    Region.SINNOH: None,
    Region.UNOVA: None,
    Region.KALOS: None,
    Region.NONE: None
}

_REGION_CONVERSIONS_REVERSE = {showdown: region for region, showdown in _REGION_CONVERSIONS.items()}

_GENDER_CONVERSIONS = {
    Gender.IRRELEVANT: None,
    Gender.MALE: "M",
    Gender.FEMALE: "F",
    Gender.GENDERLESS: None
}

_GENDER_CONVERSIONS_REVERSE = {showdown: gender for gender, showdown in _GENDER_CONVERSIONS.items()}

_MEGA_CONVERSIONS = {
    MegaType.NONE: None,
    MegaType.NORMAL: "Mega",
    MegaType.X: "Mega-X",
    MegaType.Y: "Mega-Y"
}

_MEGA_CONVERSIONS_REVERSE = {showdown: mega_type for mega_type, showdown in _MEGA_CONVERSIONS.items()}


def format_name(name: str, variant: Variant) -> str:
    """
    Determines the appropriate identifier for the Pokémon with the given name and variant as used on
    Pokémon Showdown.

    :param name: The name of the Pokémon to generate the Showdown name for.
    :param variant: The variant of the Pokémon to generate the Showdown name for.
    :return: The Showdown name for the Pokémon with the given name and variant.
    """
    components = [name]

    if variant.is_regional():
        components.append(_REGION_CONVERSIONS[variant.region])
    if variant.is_form():
        components.append(_FORM_CONVERSIONS[(name, variant.form)])
    if variant.is_gender():
        components.append(_GENDER_CONVERSIONS[variant.gender])
    if variant.is_mega():
        components.append(_MEGA_CONVERSIONS[variant.mega_type])

    return "-".join(c for c in components if c)
