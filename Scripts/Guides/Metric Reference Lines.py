# this_file: Scripts/Guides/Metric Reference Lines.py
# SPDX-License-Identifier: Apache-2.0
"""Add named glyph guides at the selected metric levels of each master.

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
    masters_make_table,
    masters_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
TITLE, KEY = "Metric Reference Lines", "guides_metric_lines"
_api = guides_api()
master_layers, guide_record, glyph_guides, layer_path, metric_values = (
    _api.master_layers,
    _api.guide_record,
    _api.glyph_guides,
    _api.layer_path,
    _api.metric_values,
)
METRICS = _api.METRICS


class MetricLines(guides_dialog_type()):
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
        checks = QtGui.QHBoxLayout()
        checks.setSpacing(14)
        self.metric_checks = {}
        for label, _ in METRICS:
            check = QtGui.QCheckBox(label)
            check.setChecked(True)
            self.metric_checks[label] = check
            checks.addWidget(check)
        checks.addStretch(1)
        self.offset = self._spin(-2000, 2000, 0)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Lines"), 0, 0)
        form.addLayout(checks, 0, 1)
        form.addWidget(QtGui.QLabel("Offset"), 1, 0)
        form.addWidget(self.offset, 1, 1)
        form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        form.addWidget(self.scope, 2, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)
        for check in self.metric_checks.values():
            self._connect(check.toggled, lambda *a: self.refresh())
        self._connect(self.offset.valueChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self.table = masters_make_table(["Glyph · master", "Guide", "y", "Action"], 220)
        root.addWidget(self.table, 1)

    def plan(self) -> Any:
        """[(glyph, master, layer, [(record, action)])]; action is add / exists / auto."""
        self.check_binding()
        wanted = [
            label for (label, _) in METRICS if self.metric_checks[label].isChecked()
        ]
        values = {m: metric_values(self.package, m) for m in self.chosen_masters()}
        rows = []
        for glyph in self.glyphs:
            for master, layer in master_layers(glyph, self.chosen_masters()):
                records = [
                    (
                        0.0,
                        round(values[master][label] + self.offset.value, 2),
                        0.0,
                        label,
                    )
                    for label in wanted
                ]
                if layer.autoLayer:
                    rows.append(
                        (
                            glyph,
                            master,
                            layer,
                            [(r, "auto layer, skipped") for r in records],
                        )
                    )
                    continue
                existing = {guide_record(g) for g in glyph_guides(layer)}
                rows.append(
                    (
                        glyph,
                        master,
                        layer,
                        [(r, "exists" if r in existing else "add") for r in records],
                    )
                )
        self.pending_targets = {
            g.name
            for (g, m, layer, entries) in rows
            if any(action == "add" for (record, action) in entries)
        }
        return rows

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
                f"Adds horizontal glyph guides to {count} glyph{('s' if count != 1 else '')}: {names}"
            )
        self.planned = self.plan() if self.glyphs else []
        rows = [
            (f"{g.name} · {m}", r[3], f"{r[1]:g}", action)
            for (g, m, layer, entries) in self.planned
            for (r, action) in entries
        ]
        self.fill_guide_rows(rows, {2}, 3)
        adds = sum(1 for cells in rows if cells[3] == "add")
        self.apply_button.setEnabled(adds > 0)
        self.status.setText(f"{adds} guide{('s' if adds != 1 else '')} to add")
        self.guard_apply(adds)

    @components_action
    def apply(self) -> None:
        """Retain original guide controls, complete data and guarded native actions."""
        jobs = [
            (g, layer, [r for (r, action) in entries if action == "add"])
            for (g, m, layer, entries) in self.plan()
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
            self.offset.value,
            tuple(
                (label, check.isChecked())
                for (label, check) in self.metric_checks.items()
            ),
        )


def main() -> Any:
    """Replace and show the complete owned modeless guide panel."""
    return show_script_dialog(MetricLines, KEY)


if __name__ == "__main__":
    main()
