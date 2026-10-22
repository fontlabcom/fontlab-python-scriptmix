# this_file: Scripts/Contours/Node Statistics.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Node Statistics
"""Contours and nodes per glyph and master in one table, with incompatible glyphs flagged.

What it does:
    Each cell reads "contours / nodes" for a master; a glyph is flagged when its masters differ,
    which breaks interpolation. Work on the selection or the whole font, then select the flagged
    glyphs in the Font window with one click. Read-only: nothing in the font changes.

How it works:
    Read contour and node counts on the selection or whole font, grouped by
    master. Flag differing counts and keep the source snapshot for the
    selection action.

Why this design:
    Count differences can rule out compatibility, but matching counts alone do
    not prove matching contour structure.

How to use:
    Run Contours > Node Statistics. Choose the source scope, inspect each
    contours/nodes cell and use the action button to select flagged glyphs in
    the Font window.

Benefit:
    Find count mismatches quickly while preserving node positions, topology
    and layer data.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package as current_package,  # noqa: PLC0414 - original public helper
)
from fly.ap.scripting import (
    inspectors_api,
    inspectors_dialog_type,
    inspectors_snapshot_refresh,
    show_script_dialog,
)
from fly.ap.scripting import (
    masters_fill_table as fill_table,
)
from fly.ap.scripting import (
    masters_make_table as make_table,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = inspectors_api()
muted = _api.muted
selected_names = _api.selected_names
master_layers = _api.master_layers
own_contours = _api.own_contours
layer_counts = _api.layer_counts
glyph_counts = _api.glyph_counts
incompatible = _api.incompatible
all_names = _api.all_names
TITLE = "Node Statistics"
KEY = "outlines_node_statistics"


class SampleDialog(inspectors_dialog_type()):
    """Original menu shell on the existing owned Proof/Names/Masters lifecycle."""

    def __init__(self, parent: Any = None) -> None:
        """Finish controls/status/Close before fallible font reads."""
        super().__init__(parent, TITLE, KEY)


def select_in_font_window(names: list[str]) -> None:
    """Select through the active panel's complete source and identity preflight."""
    import sys

    dialog = getattr(sys, "_fontlab_samples", {}).get(KEY)
    if dialog is None:
        raise ValueError("Open this panel before selecting its results.")
    dialog.select_names(names)


class NodeStatistics(SampleDialog):
    """Complete original inspector with complete snapshots and owned cleanup."""

    ACTION = "Select Flagged"

    def build(self) -> None:
        """Create every original control and guarded signal before native reads."""
        grid = self.form()
        self.source = QtGui.QComboBox()
        self.source.addItem(f"Selected glyphs ({len(self.names)})")
        self.source.addItem("Whole font")
        self._connect(self.source.currentIndexChanged, lambda *a: self.refresh())
        self.only_flagged = QtGui.QCheckBox("Show flagged glyphs only")
        self._connect(self.only_flagged.toggled, lambda *a: self.refresh())
        grid.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
        grid.addWidget(self.source, 0, 1)
        grid.addWidget(self.only_flagged, 0, 2)
        grid.setColumnStretch(1, 1)
        self.table = make_table(["Glyph", *list(self.masters), "Masters"], 300)
        self.root.addWidget(self.table, 1)

    def source_names(self) -> Any:
        """Return captured selection or actual ordered Whole-font membership."""
        if self.package is None:
            return []
        return all_names(self.package) if self.source.currentIndex == 1 else self.names

    @inspectors_snapshot_refresh
    def refresh(self) -> None:
        """Read a complete original report under the shared font/master snapshot guard."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.apply_button.setEnabled(False)
            return
        self.table.setColumnCount(len(self.masters) + 2)
        self.table.setHorizontalHeaderLabels(["Glyph", *self.masters, "Masters"])
        self._scope_whole = self.source.currentIndex == 1
        names = self.source_names()
        self._scope_names = tuple(names)
        self.data, self.flagged = {}, []
        for name in names:
            glyph = self.require_glyphs([name])[0]
            if glyph is not None:
                self.data[name] = glyph_counts(glyph, self.masters)
                if incompatible(self.data[name]):
                    self.flagged.append(name)
        self.subtitle.setText(
            f"{len(self.data)} glyphs × {len(self.masters)} masters · "
            f"cells show contours / nodes drawn in each master",
        )
        rows, odd = [], {}
        for name, counts in self.data.items():
            if self.only_flagged.isChecked() and name not in self.flagged:
                continue
            values = [v for v in counts.values() if v is not None]
            common = max(set(values), key=values.count) if values else None
            cells = [name]
            for column, master in enumerate(self.masters, start=1):
                value = counts.get(master)
                cells.append("auto" if value is None else f"{value[0]} / {value[1]}")
                if value is not None and value != common:
                    odd[len(rows), column] = True
            cells.append("✗ differ" if name in self.flagged else "✓")
            rows.append(tuple(cells))
        last = len(self.masters) + 1
        fill_table(
            self.table,
            rows,
            lambda r, c, text: (
                odd.get((r, c), False) or (c == last and text.startswith("✗"))
            ),
        )
        self.apply_button.setEnabled(bool(self.flagged))
        self.status.setText(
            f"{len(self.flagged)} of {len(self.data)} glyphs have masters that differ",
        )

    def apply(self) -> None:
        """Preflight displayed counts before selecting exactly the flagged glyphs."""
        self.ensure_snapshot()
        self.select_names(self.flagged)
        self.last_result = {"selected": list(self.flagged)}
        fontlab.UpdateAll()
        self.status.setText(
            f"Selected {len(self.flagged)} flagged glyphs in the Font window",
        )


def main() -> Any:
    """Replace and show the complete original owned inspector."""
    return show_script_dialog(NodeStatistics, KEY)


if __name__ == "__main__":
    main()
