# this_file: Scripts/Guides/Clear Glyph Guides.py
# SPDX-License-Identifier: Apache-2.0
"""Remove matching glyph guides while preserving hints and retained guides.

What it does:
    Select glyphs. Choose current or all masters, direction and name text. Inspect
    every matching guide, then use Remove. Retained native colour, tags and geometry
    are kept. Batches with unsafe automatic dependants are refused before history.
    Changed font, selection or source clears the plan; Close releases owned signals.

How it works:
    Filter each selected layer's glyph guides by direction and name text. Plan
    removals separately from retained native guides, preserving hints and
    unrelated properties.

Why this design:
    A removal preview exposes exactly which guides match before a broad
    master-scope operation starts.

How to use:
    Select glyphs and run Guides > Clear Glyph Guides. Choose master scope and
    filters, inspect matching guide rows and press Remove. Refresh the plan
    after source changes.

Benefit:
    Remove a targeted guide subset; the action is recorded as one Undo step.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    components_action,
    guide_rewrite_api,
    guide_rewrite_dialog_type,
    guides_api,
    masters_make_table,
    masters_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
TITLE, KEY = "Clear Glyph Guides", "guides_clear"
_api, _guide = guide_rewrite_api(), guides_api()
master_layers, guide_record, glyph_guides = (
    _guide.master_layers,
    _guide.guide_record,
    _guide.glyph_guides,
)
DIRECTIONS, direction_of, matches = _api.DIRECTIONS, _api.direction_of, _api.matches


class ClearGuides(guide_rewrite_dialog_type()):
    """Complete original guide controls on the shared owned lifecycle."""

    ACTION = "Remove"

    def __init__(self, parent: Any = None) -> None:
        """Finish controls before any native source read."""
        super().__init__(parent, TITLE, KEY)

    def build(self) -> None:
        """Retain every original control and callback."""
        self.setMinimumWidth(540)
        self.last_result = None
        self.glyphs = []
        self.glyph = None
        self.pending_targets = set()
        root = self.root
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.direction = QtGui.QComboBox()
        self.direction.addItems(DIRECTIONS)
        self.name_filter = QtGui.QLineEdit()
        self.name_filter.setPlaceholderText("any name")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Direction"), 0, 0)
        form.addWidget(self.direction, 0, 1)
        form.addWidget(QtGui.QLabel("Name contains"), 1, 0)
        form.addWidget(self.name_filter, 1, 1)
        form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        form.addWidget(self.scope, 2, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)
        self.table = masters_make_table(
            ["Glyph · master", "Guide", "Direction", "Position"], 220
        )
        root.addWidget(self.table, 1)
        self._connect(self.direction.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.name_filter.textChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())

    def plan(self) -> Any:
        """[(glyph, master, layer, [guides to remove], [guides to keep])]."""
        self.check_binding()
        direction, text = (self.direction.currentText, self.name_filter.text)
        planned = []
        for glyph in self.glyphs:
            for master, layer in master_layers(glyph, self.chosen_masters()):
                guides = glyph_guides(layer)
                remove = [
                    g for g in guides if matches(guide_record(g), direction, text)
                ]
                keep = [g for g in guides if g not in remove]
                planned.append((glyph, master, layer, remove, keep))
        self.pending_targets = {
            g.name
            for g, m, layer, remove, keep in planned
            if remove and not layer.autoLayer
        }
        return planned

    @masters_snapshot_refresh
    def refresh(self) -> Any:
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText(
                "Select glyphs in the Font window, then run this script again."
            )
        else:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (
                " …" if count > 8 else ""
            )
            self.subtitle.setText(
                f"Removes matching glyph guides from {count} glyph{('s' if count != 1 else '')}: {names}"
            )
        rows = []
        for glyph, master, layer, remove, _keep in self.plan() if self.glyphs else []:
            if layer.autoLayer:
                if remove:
                    rows.append(
                        (f"{glyph.name} · {master}", "auto layer, skipped", "", "")
                    )
                continue
            for guide in remove:
                x, y, angle, name = guide_record(guide)
                kind = direction_of((x, y, angle, name))
                position = (
                    f"{y:g}"
                    if kind == "Horizontal"
                    else f"{x:g}"
                    if kind == "Vertical"
                    else f"{x:g}, {y:g} · {angle:g}°"
                )
                rows.append(
                    (f"{glyph.name} · {master}", name or "(unnamed)", kind, position)
                )
        self.fill_guide_rows(rows, {3})
        removable = sum(1 for cells in rows if cells[1] != "auto layer, skipped")
        self.apply_button.setEnabled(removable > 0)
        self.status.setText(
            f"{removable} guide{('s' if removable != 1 else '')} to remove"
        )
        self.guard_apply(removable)

    @components_action
    def apply(self) -> Any:
        jobs = [
            (glyph, layer, keep)
            for glyph, master, layer, remove, keep in self.plan()
            if remove and (not layer.autoLayer)
        ]
        self.last_result = _api.clear(self.package, jobs, TITLE)
        self.refresh()
        note = (
            f" · {self.last_result['left']} could not be removed"
            if self.last_result["left"]
            else ""
        )
        self.status.setText(
            f"Removed {self.last_result['removed']} guides from {self.last_result['layers']} layers{note}"
        )


def main() -> Any:
    """Replace and show the complete owned guide editor."""
    return show_script_dialog(ClearGuides, KEY)


if __name__ == "__main__":
    main()
