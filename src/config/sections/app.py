from dataclasses import dataclass
from typing import TypedDict


class AppSectionData(TypedDict):
    rpc: str
    user_agent: str


@dataclass(frozen=True)
class AppSection:
    _data: AppSectionData

    def rpc(self) -> str:
        return self._data["rpc"]

    def user_agent(self) -> str:
        return self._data["user_agent"]
