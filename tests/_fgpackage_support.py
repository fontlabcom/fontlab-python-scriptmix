# this_file: tests/_fgpackage_support.py
"""Realistic ``flPackage.fgPackage`` for owned package fakes (Issue 250).

The real ``flPackage.fgPackage.glyphs`` is the package's own glyph order; App's
``dependency_values`` reads it. ``fgPackage[name].unicodes`` is the only Unicode
binding; ``flGlyph`` has none. Fake glyphs expose theirs privately as ``codes``. The view stays live, so fakes that add or drop
glyphs after construction keep matching.
"""

from collections.abc import Mapping
from types import SimpleNamespace
from typing import Any


class FgPackage:
    """Live ``fgPackage`` view whose ``glyphs`` lists the fake's glyphs in order."""

    def __init__(self, glyphs: Mapping[str, Any]) -> None:
        self._glyphs = glyphs

    def __getitem__(self, name: str) -> Any:
        """Return the package's own glyph record: it alone carries ``unicodes``.

        Native ``fgPackage[missing]`` returns ``None`` instead of raising (A2 report 43).
        """
        glyph = self._glyphs.get(name)
        if glyph is None:
            return None
        return SimpleNamespace(name=name, unicodes=list(glyph.codes))

    @property
    def glyphs(self) -> list[Any]:
        return list(self._glyphs.values())


def fg_package(glyphs: Mapping[str, Any]) -> FgPackage:
    return FgPackage(glyphs)
