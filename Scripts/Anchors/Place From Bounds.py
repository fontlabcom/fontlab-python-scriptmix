# this_file: Scripts/Anchors/Place From Bounds.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Place From Bounds
"""Add or move top and bottom anchors from the outline bounds.

What: Puts top, bottom, _top and _bottom anchors on the ink box of each layer.
Each anchor sits at the horizontal centre of the box, on the chosen edge,
plus an offset. The offset pushes the anchor away from the glyph.

How: top follows the upper edge; bottom follows the lower edge; _top follows
the lower edge; _bottom follows the upper edge. A missing anchor is
added with its name-derived appearance. An existing anchor moves and
keeps its style. Empty layers are left alone. The centre rounds half up.

Why: This gives a quick first anchor set for a new font. Refine it later by hand.

Use: Select glyphs. Run the script. Tick the anchors. Set offsets. Check the
table. Press Place.

Benefit: Many glyphs get consistent starter anchors in one Undo step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- an existing anchor would move to 0, 0 (FontLab cannot Redo that);
- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- several anchors on a layer share a name (the edit is ambiguous);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads every value back. It reports any value
that FontLab did not keep, for example under a strong rounding preference.
If FontLab fails part-way, the error says that native changes may remain.
The edit is recorded as one Undo step. The plan, the safety checks, the one-step
write and the panel base are shared with the other anchor scripts
(fly.ap.anchor_writer, fly.ap.anchor_panel); the planner and the controls
belong to this script.

Source: the author's own FontLab sample
anchors_place_from_bounds.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
import fly.ap.scripting as scripting

QtGui = qt.QtGui
TITLE = "Place Anchors from Bounds"
KEY = "anchors_place_from_bounds"

# ---------------------------------------------------------------- bounds logic
# name, edge of the ink box it follows, default offset, on by default
ANCHORS: list[tuple[str, str, int, bool]] = [
    ("top", "top", 0, True),
    ("bottom", "bottom", 0, True),
    ("_top", "bottom", 0, False),
    ("_bottom", "top", 0, False),
]


def ink_box(layer: Any) -> tuple[float, float, float, float] | None:
    """(xmin, ymin, xmax, ymax) of the outline. None for an empty layer."""
    box = layer.boundingBox
    if box.width() <= 0 and box.height() <= 0:
        return None
    return box.x(), box.y(), box.x() + box.width(), box.y() + box.height()


def target_point(
    box: tuple[float, float, float, float], edge: str, offset: int
) -> tuple[int, int]:
    """Centre of the box on the chosen edge, pushed out by `offset`."""
    xmin, ymin, xmax, ymax = box
    x = anchor_writer.half_up((xmin + xmax) / 2)
    y = (
        anchor_writer.half_up(ymax + offset)
        if edge == "top"
        else anchor_writer.half_up(ymin - offset)
    )
    return x, y


def bounds_changes(
    layer: Any, wanted: list[tuple[str, str, int]]
) -> list[anchor_writer.Change]:
    """Rows for `wanted` = [(name, edge, offset)]. Empty layer: no rows."""
    box = ink_box(layer)
    if box is None:
        return []
    current = anchor_writer.anchor_points(layer)
    changes: list[anchor_writer.Change] = []
    for name, edge, offset in wanted:
        new = target_point(box, edge, offset)
        old = current.get(name)
        if old is not None and tuple(old) == new:
            continue
        before = (
            "–"
            if old is None
            else f"{anchor_writer.fmt(old[0])}, {anchor_writer.fmt(old[1])}"
        )
        changes.append(
            anchor_writer.Change(
                name, before, f"{new[0]}, {new[1]}", ("set", name, new)
            )
        )
    clash = anchor_writer.duplicated(layer, [c.name for c in changes])
    return anchor_writer.refusal(clash) if clash else changes


class PlaceFromBounds(anchor_panel.panel_type()):
    """One checkbox and one offset per anchor, plus the master scope."""

    TITLE, KEY, ACTION = TITLE, KEY, "Place"

    def build_controls(self) -> None:
        self.checks: dict[str, Any] = {}
        self.offsets: dict[str, Any] = {}
        for row, (name, edge, offset, enabled) in enumerate(ANCHORS):
            check = QtGui.QCheckBox(name)
            check.setChecked(enabled)
            spin = self.spin(
                -1000,
                1000,
                offset,
                "  above ink top" if edge == "top" else "  below ink bottom",
            )
            self.checks[name], self.offsets[name] = check, spin
            self.form.addWidget(check, row, 0)
            self.form.addWidget(spin, row, 1)
            self.watch(check.toggled)
            self.watch(spin.valueChanged)
        self.scope = self.scope_box()
        self.form.addWidget(QtGui.QLabel("Masters"), len(ANCHORS), 0)
        self.form.addWidget(self.scope, len(ANCHORS), 1)
        self.watch(self.scope.currentIndexChanged)

    def chosen_masters(self) -> list[str]:
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def planner(self) -> anchor_writer.Planner:
        wanted = [
            (name, edge, int(self.offsets[name].value))
            for name, edge, _, _ in ANCHORS
            if self.checks[name].isChecked()
        ]
        if not wanted:
            raise ValueError("Tick at least one anchor.")
        return lambda glyph, master, layer: bounds_changes(layer, wanted)


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(PlaceFromBounds, KEY)


if __name__ == "__main__":
    main()
