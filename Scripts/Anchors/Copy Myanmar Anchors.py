# this_file: Scripts/Anchors/Copy Myanmar Anchors.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Copy Myanmar Anchors
"""Copy Myanmar bowl anchors with Unicode routing across named masters.

What: Copy U+101D anchors to single-bowl letters and U+1000 anchors to
double-bowl letters. Unencoded alternates stay unchanged.
How: Capture Unicode routing once per scan. Match source and target layers
by master name. Cache each source layer once per plan. Give each layer its
own time budget; doubtful source layers become note rows. Existing target
pins keep their style. Automatic layers are kept.
Why: Copy Anchors From Glyph can perform the copies in two manual passes;
this tool supplies the Myanmar Unicode routing preset for both passes.
Use: Open a Myanmar font, inspect the whole-font preview, then click Copy.
Benefit: Set consistent starter anchors across both bowl families. Each
application is recorded as one Undo step.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.
"""

from time import monotonic
from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup

TITLE = "Copy Myanmar Anchors"
KEY = "anchors_copy_myanmar_anchors"


SINGLE = (
    0x1001,
    0x1002,
    0x1004,
    0x1005,
    0x100E,
    0x1012,
    0x1013,
    0x1015,
    0x1016,
    0x1017,
    0x1019,
    0x1027,
    0x100B,
    0x100C,
    0x100D,
)
DOUBLE = (
    0x1003,
    0x1006,
    0x100A,
    0x1010,
    0x1011,
    0x1018,
    0x101A,
    0x101C,
    0x101E,
    0x101F,
    0x1021,
    0x1022,
)


def route_names(rows: list[tuple[str, str, str]]) -> dict[str, str]:
    """Resolve the two bowl families from every Unicode assignment in the catalogue."""
    encoded: dict[int, str] = {}
    wanted = set(SINGLE + DOUBLE + (0x101D, 0x1000))
    for name, codes, _ in rows:
        for token in codes.split():
            code = int(token.removeprefix("U+"), 16)
            if code not in wanted:
                continue
            if code in encoded and encoded[code] != name:
                raise ValueError(f"Several glyphs encode U+{code:04X}.")
            encoded[code] = name
    if not all(code in encoded for code in (0x101D, 0x1000)):
        raise ValueError("Both Myanmar source glyphs U+101D and U+1000 are required.")
    routes = {encoded[code]: encoded[0x101D] for code in SINGLE if code in encoded}
    for code in DOUBLE:
        if code in encoded:
            name = encoded[code]
            source = encoded[0x1000]
            if name in routes and routes[name] != source:
                raise ValueError(f"{name} belongs to both bowl families.")
            routes[name] = source
    return routes


class MyanmarAnchorCopy(anchor_panel.panel_type()):
    """Whole-font, all-master routed copy, with an explicit preview."""

    TITLE, KEY, ACTION = TITLE, KEY, "Copy"

    def refresh(self) -> None:
        """Contain scan errors inside the panel and disable its write action."""
        try:
            super().refresh()
        except (ValueError, RuntimeError, TimeoutError) as error:
            self.apply_button.setEnabled(False)
            self.status.setText(str(error))

    def glyph_names(self) -> list[str]:
        self.routes = self.live_routes()
        return list(self.routes)

    def live_routes(self) -> dict[str, str]:
        import fly.ap.glyph_catalog as glyph_catalog  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup

        return route_names(glyph_catalog.capture().rows)

    def planner(self) -> anchor_writer.Planner:
        routes = self.routes
        sources: dict[tuple[str, str], tuple[dict, str]] = {}

        def source_points(source: str, master: str) -> tuple[dict, str]:
            deadline = monotonic() + 1.5
            try:
                glyph = self.package.findName(source)
                layer = anchor_writer.layer_of(glyph, master) if glyph else None
                if layer is None or layer.autoLayer:
                    return {}, "plain source layer required, skipped"
                points = {}
                for pin in layer.anchors:
                    if monotonic() >= deadline:
                        raise TimeoutError("source layer time budget exceeded, skipped")
                    if pin.name in points:
                        return {}, "repeated source anchor names, skipped"
                    points[pin.name] = anchor_writer.raw_point(pin)
                return points, ""
            except (ValueError, RuntimeError, TimeoutError) as error:
                return {}, str(error)

        def changes(glyph: Any, master: str, layer: Any) -> list[anchor_writer.Change]:
            key = (routes[glyph.name], master)
            if key not in sources:
                sources[key] = source_points(*key)
            points, note = sources[key]
            if note:
                return [anchor_writer.Change("source", "", f"{key[0]}: {note}")]
            deadline = monotonic() + 1.5
            old = anchor_writer.anchor_points(layer)
            rows = []
            for name, point in points.items():
                if monotonic() >= deadline:
                    return [
                        anchor_writer.Change(
                            "copy", "", "target layer time budget exceeded, skipped"
                        )
                    ]
                if old.get(name) != point:
                    rows.append(
                        anchor_writer.Change(
                            name,
                            str(old.get(name, "missing")),
                            str(point),
                            ("set", name, point),
                        )
                    )
            return rows

        return changes


def main() -> Any:
    """Open the routed preview; no Unicode-to-glyph-name guesses are used."""
    return scripting.show_script_dialog(MyanmarAnchorCopy, KEY)


if __name__ == "__main__":
    main()
