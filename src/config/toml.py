from dataclasses import dataclass
from pathlib import Path

import tomllib

from config.sections.app import AppSection
from config.sections.user import UserSection


@dataclass(frozen=True)
class AppConfig:
    _path: Path = Path(__file__).parent.parent.parent / "config.toml"

    def app(self) -> AppSection:
        toml = tomllib.load(self._path.open("rb"))
        return AppSection(toml["app"])

    def user(self) -> UserSection:
        toml = tomllib.load(self._path.open("rb"))
        return UserSection(toml["user"])
