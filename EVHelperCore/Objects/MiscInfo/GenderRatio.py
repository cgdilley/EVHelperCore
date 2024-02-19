from EVHelperCore.Interfaces.IJsonable import IJsonExchangeable

from typing import Optional


class GenderRatio(IJsonExchangeable):

    def __init__(self, male: Optional[float], female: Optional[float]):
        self.male = male if male else 0
        self.female = female if female else 0

    def __str__(self) -> str:
        return "Genderless" if self.is_genderless() else \
            f"{self.male * 100:g}%m, {self.female * 100:g}%f"

    def is_genderless(self) -> bool:
        return not self.male and not self.female

    def to_json(self) -> dict:
        vals = []
        if self.male > 0:
            vals.append(("male", self.male))
        if self.female > 0:
            vals.append(("female", self.female))
        if self.is_genderless():
            vals.append(("genderless", True))
        return {k: v for k, v in vals}

    @classmethod
    def from_json(cls, obj: dict) -> IJsonExchangeable:
        return GenderRatio(obj.get("male", None), obj.get("female", None))
