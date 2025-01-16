from dataclasses import dataclass
from typing import TypedDict


class UserSectionData(TypedDict):
    clicks_per_loop: int
    delay_between_loop: int

    clicks_delay_from: float
    clicks_delay_to: float


@dataclass(frozen=True)
class UserSection:
    _data: UserSectionData

    def clicks_per_loop(self) -> int:
        return self._data["clicks_per_loop"]

    def delay_between_loop(self) -> int:
        return self._data["delay_between_loop"]

    def clicks_delay_from(self) -> float:
        return self._data["clicks_delay_from"]

    def clicks_delay_to(self) -> float:
        return self._data["clicks_delay_to"]
