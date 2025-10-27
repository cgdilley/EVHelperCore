from __future__ import annotations

from typing import Self

from SprelfJSON import JSONModel, JSONObject


class GenderRatio(JSONModel):
    male: float | None
    female: float | None

    def __str__(self) -> str:
        return "Genderless" if self.is_genderless() else \
            f"{self.male * 100:g}%m, {self.female * 100:g}%f"

    def is_genderless(self) -> bool:
        return not self.male and not self.female

    def to_json(self) -> JSONObject:
        j = super().to_json()
        if self.is_genderless():
            j["genderless"] = True
        return j

    @classmethod
    def from_json(cls, o: JSONObject, **kwargs) -> Self:
        _ = o.pop("genderless", None)
        return super().from_json(o, **kwargs)
