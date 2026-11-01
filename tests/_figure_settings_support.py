# this_file: tests/_figure_settings_support.py
"""Stateful owned QSettings doubles; no real user preferences are accessed."""

from typing import Any


class Settings:
    NoError = 0

    def __init__(self, data: dict | None = None) -> None:
        self.data = {} if data is None else data
        self.writes = []
        self.fallbacks = True
        self.writable = True
        self.error = 0

    def value(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def setValue(self, key: str, value: Any) -> None:
        self.writes.append((key, value))
        self.data[key] = value

    def setFallbacksEnabled(self, enabled: bool) -> None:
        self.fallbacks = enabled

    def isWritable(self) -> bool:
        return self.writable

    def sync(self) -> None:
        pass

    def status(self) -> int:
        return self.error


def settings_factory():
    stores = {}

    def make(organization, application, parent=None):
        assert (organization, application) == ("FontLab", "ScriptDefaultFigures")
        result = Settings(stores.setdefault((organization, application), {}))
        result.parent = parent
        return result

    return make
