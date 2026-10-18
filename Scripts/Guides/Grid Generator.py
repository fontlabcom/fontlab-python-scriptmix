# this_file: Scripts/Guides/Grid Generator.py
# SPDX-License-Identifier: Apache-2.0
"""Preview and add named horizontal, vertical or combined glyph-guide grids.

Select glyphs, choose current or all masters and inspect the complete preview.
Existing matching guides and automatic layers are kept. Apply uses one named Undo
step. Unsafe automatic dependants are refused before history. Close releases all
owned signals and preview paths. No font-wide guides or outlines are changed.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    components_action,
    current_package,  # noqa: F401 - retain the original public helper.
    guides_api,
    guides_dialog_type,
    guides_preview_type,
    masters_make_table,
    masters_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
TITLE, KEY = "Grid Generator", "guides_grid_generator"
_api = guides_api()
master_layers, guide_record, glyph_guides = (
    _api.master_layers,
    _api.guide_record,
    _api.glyph_guides,
)
layer_path, grid = _api.layer_path, _api.grid

DIRECTIONS = ["Horizontal and vertical", "Horizontal", "Vertical"]
GridPreview = guides_preview_type()


class GridGenerator(guides_dialog_type()):
    """Complete original guide controls on the shared owned modeless shell."""

    ACTION = "Apply"

    def __init__(self, parent: Any = None) -> None:
        """Use the shared owned shell and late native binding."""
        super().__init__(parent, TITLE, KEY)

    def build(self) -> None:
        """Build all original controls before reading native source."""
        self.setMinimumWidth(540)
        (self.glyphs, self.planned) = ([], [])
        self.pending_targets = set()
        self.last_result = None
        root = self.root
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.direction = QtGui.QComboBox()
        self.direction.addItems(DIRECTIONS)
        self.origin = self._spin(-5000, 5000, 0)
        self.step = self._spin(1, 5000, 100)
        self.count = self._spin(1, 100, 5)
        self.count.setSuffix("")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Lines"), 0, 0)
        form.addWidget(self.direction, 0, 1, 1, 3)
        form.addWidget(QtGui.QLabel("Origin"), 1, 0)
        form.addWidget(self.origin, 1, 1)
        form.addWidget(QtGui.QLabel("Step"), 1, 2)
        form.addWidget(self.step, 1, 3)
        form.addWidget(QtGui.QLabel("Count"), 2, 0)
        form.addWidget(self.count, 2, 1)
        form.addWidget(QtGui.QLabel("Masters"), 3, 0)
        form.addWidget(self.scope, 3, 1, 1, 3)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        root.addLayout(form)
        self.preview = GridPreview()
        self.preview.on_error = lambda message: self.status.setText(
            f"Preview error: {message}"
        )
        root.addWidget(self.preview, 1)
        self._connect(self.direction.currentIndexChanged, lambda *a: self.refresh())
        for spin in (self.origin, self.step, self.count):
            self._connect(spin.valueChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self.table = masters_make_table(
            ["Glyph · master", "Guides to add", "Already there"], 120
        )
        root.addWidget(self.table)
        self.preview.before_draw = self.check_preview
        self.preview.on_error = self.paint_report
        self.preview.failure_cleanup = self.paint_report

    def records(self) -> Any:
        """Retain original guide controls, complete data and guarded native actions."""
        return grid(
            self.direction.currentIndex,
            self.origin.value,
            self.step.value,
            self.count.value,
        )

    def plan(self) -> Any:
        """[(glyph, master, layer, [records to add], [records already there])]."""
        self.check_binding()
        wanted = self.records()
        planned = []
        for glyph in self.glyphs:
            for master, layer in master_layers(glyph, self.chosen_masters()):
                existing = {guide_record(g) for g in glyph_guides(layer)}
                planned.append(
                    (
                        glyph,
                        master,
                        layer,
                        [r for r in wanted if r not in existing],
                        [r for r in wanted if r in existing],
                    )
                )
        self.pending_targets = {
            g.name
            for (g, m, layer, add, there) in planned
            if add and (not layer.autoLayer)
        }
        return planned

    @masters_snapshot_refresh
    def refresh(self) -> None:
        """Retain original guide controls, complete data and guarded native actions."""
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
                f"Adds grid guides to {count} glyph{('s' if count != 1 else '')}: {names}"
            )
        records = self.records()
        if self.glyphs:
            layer = self.glyphs[0].findLayer(self.current_master)
            metrics = fontlab.FontMetrics(self.package, self.current_master)
            frame = (float(metrics.descender), float(metrics.ascender))
            if layer is not None and (not layer.isNull):
                self.preview.set_content(
                    layer_path(layer), layer.advanceWidth, records, frame
                )
        else:
            self.preview.set_content(None, 0, records, (-250.0, 750.0))
        rows = []
        for glyph, master, layer, add, there in self.plan() if self.glyphs else []:
            if layer.autoLayer:
                rows.append((f"{glyph.name} · {master}", "auto layer, skipped", ""))
            else:
                rows.append(
                    (f"{glyph.name} · {master}", str(len(add)), str(len(there)))
                )
        self.fill_guide_rows(rows, {1, 2}, None)
        adds = sum(int(cells[1]) for cells in rows if cells[1].isdigit())
        self.apply_button.setEnabled(adds > 0)
        self.status.setText(
            f"{len(records)} grid lines · {adds} guide{('s' if adds != 1 else '')} to add"
        )
        self.guard_apply(adds)

    @components_action
    def apply(self) -> None:
        """Retain original guide controls, complete data and guarded native actions."""
        jobs = [
            (glyph, layer, add)
            for (glyph, master, layer, add, there) in self.plan()
            if not layer.autoLayer
        ]
        self.last_result = _api.add_guides(self.package, jobs, TITLE)
        self.refresh()
        self.status.setText(
            f"Added {self.last_result['guides']} guides to {self.last_result['layers']} layers"
        )

    def option_values(self) -> tuple:
        """Bind each visible control used by the guide preview."""
        return (
            self.scope.currentIndex,
            self.direction.currentIndex,
            self.origin.value,
            self.step.value,
            self.count.value,
        )


def main() -> Any:
    """Replace and show the complete owned modeless guide panel."""
    return show_script_dialog(GridGenerator, KEY)


if __name__ == "__main__":
    main()
