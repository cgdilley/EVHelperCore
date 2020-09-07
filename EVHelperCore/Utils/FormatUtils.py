from EVHelperCore.Objects import Name, Variant, Region, Gender, MegaType

import re
from typing import Optional

LETTER_CHARS = r"A-ZÀÁÈÉÌÍÒÓÙÚ0-9"
NAME_REGEX = re.compile(rf"^[{LETTER_CHARS}]+(['\-_][{LETTER_CHARS}]+)*$")


def format_name_as_id(name: Name, variant: Optional[Variant] = None,
                      ignore_mega: bool = False) -> str:
    components = [name.base_name()]
    if variant:
        if variant.is_regional():
            if variant.region == Region.ALOLA:
                components.insert(0, "ALOLAN")
            elif variant.region == Region.GALAR:
                components.insert(0, "GALARIAN")
        if variant.is_gender():
            if variant.gender == Gender.MALE:
                components.append("M")
            elif variant.gender == Gender.FEMALE:
                components.append("F")
            elif variant.gender == Gender.GENDERLESS:
                components.append("G")
        if variant.is_form():
            components.extend(v.strip("-") for v in variant.form.split(" "))
        if variant.is_mega() and not ignore_mega:
            components.insert(0, "MEGA")
            if variant.mega_type == MegaType.X:
                components.append("X")
            elif variant.mega_type == MegaType.Y:
                components.append("Y")
    s = "_".join(components)
    s = s.replace("♂", "-M") \
        .replace("♀", "-F") \
        .upper()
    s = re.sub(r"[:.,%]", "", s)
    s = re.sub(r"[\s-]+", "_", s)
    if not NAME_REGEX.match(s):
        raise Exception(f"Could not format name '{name.name}'... best effort: '{s}'")
    return s


# def format_regional_name_as_id(name: Name, variant: Variant) -> str:
#     components = [format_name_as_id(name.base_name())]
#     if variant.is_regional():
#         if variant.region == Region.ALOLA:
#             components.insert(0, "ALOLAN")
#         elif variant.region == Region.GALAR:
#             components.insert(0, "GALARIAN")
#     return "_".join(components)
