# this_file: Scripts/Kerning/Remove Small Pairs.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Remove Small Pairs
"""Delete kerning pairs whose value is smaller than a threshold, on one or all masters.

What it does:
    Tiny pairs (±1 … ±5 units) are invisible in print, bloat the kern feature and often come from
    auto-kerning or interpolation. The preview lists every pair that would go, with the count per
    master; zero pairs are included. Class pairs (@name) count like glyph pairs. One Apply is one
    Undo step for all masters.

How it works:
    Read explicit glyph and class pairs, compare their magnitudes with the
    chosen threshold and stage every deletion before calling the shared
    kerning writer.

Why this design:
    Zero and small pairs can still be intentional, so the complete preview
    leaves the deletion choice visible.

How to use:
    Run Kerning > Remove Small Pairs. Choose the threshold and master scope,
    inspect the pair list and counts, then Apply to remove the displayed
    candidates.

Benefit:
    Clean a chosen explicit-pair range in one recorded Undo step across the
    selected masters.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    kerning_edit_dialog_type,
    kerning_editor_api,
)
from fly.ap.scripting import (
    kerning_editor_apply as editor_apply,
)
from fly.ap.scripting import (
    kerning_editor_make_table as make_table,
)
from fly.ap.scripting import (
    kerning_editor_refresh as editor_refresh,
)
from fly.ap.scripting import (
    names_muted as muted,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui
api = kerning_editor_api()
KerningEditDialog = kerning_edit_dialog_type()
native_side = api.native_side
current_package = ap.scripting.current_package
kerning_pairs = ap.scripting.kerning_pairs

TITLE = "Remove Small Kerning"
KEY = "kerning_remove_small"


def write_kerning(
    package: Any, edits: dict[str, dict[tuple[str, str], int | None]]
) -> None:
    """Apply a fully validated multi-master batch using the tool's native Undo label."""
    api.write_kerning(package, edits, TITLE)


small_pairs = api.small_pairs


def run(
    package: Any, masters: list[str], threshold: float, *, expected: Any = None
) -> dict[str, int]:
    """Preflight every deletion before a single snapshot-bound history batch."""
    return api.remove_run(
        package, masters, threshold, expected=expected, undo_name=TITLE
    )


class RemoveSmall(KerningEditDialog):
    """Retain the complete original Remove Small Pairs workflow with shared native safety."""

    def __init__(self, parent: Any = None) -> None:
        """Create all original controls on the shared snapshot-bound owned panel."""
        KerningEditDialog.__init__(self, parent, TITLE, KEY)
        root = self.root
        self.setMinimumWidth(520)
        self.found = {}
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.threshold = QtGui.QSpinBox()
        self.threshold.setRange(1, 500)
        self.threshold.setValue(5)
        self.threshold.setPrefix("|value| < ")
        self.threshold.setSuffix(" units")
        self.threshold.setAlignment(QtCore.Qt.AlignRight)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Remove"), 0, 0)
        form.addWidget(self.threshold, 0, 1)
        form.addWidget(QtGui.QLabel("Masters"), 1, 0)
        form.addWidget(self.scope, 1, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)
        self.table = make_table(["Pair", "Master", "Value"])
        root.addWidget(self.table, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Remove")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self.add_refresh(footer, self.refresh)
        self._connect(self.threshold.valueChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def chosen_masters(self) -> list[str]:
        """Return the original current-master scope or all original masters."""
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    @editor_refresh
    def refresh(self) -> None:
        """Render preview values and counts; enable Apply only for actual staged edits."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.found = {}
        else:
            self.found = small_pairs(
                self.package, self.chosen_masters(), self.threshold.value
            )
            total = sum(
                len(kerning_pairs(self.package, m)) for m in self.chosen_masters()
            )
            self.subtitle.setText(
                f"{total} pairs in {len(self.chosen_masters())} master{('s' if len(self.chosen_masters()) != 1 else '')}; pairs closer to zero than the threshold are deleted."
            )
        rows = [
            (f"{l}  {r}", m, v)
            for (m, found) in self.found.items()
            for (l, r, v) in found
        ]
        warn = QtGui.QColor("#d33")
        self.table.setRowCount(len(rows))
        for row, (pair, master, value) in enumerate(rows):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(pair))
            self.table.setItem(row, 1, QtGui.QTableWidgetItem(master))
            item = QtGui.QTableWidgetItem(f"{value:g}")
            item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
            item.setForeground(QtGui.QBrush(warn))
            self.table.setItem(row, 2, item)
        counts = " · ".join(f"{m} {len(f)}" for (m, f) in self.found.items())
        self.status.setText(
            f"{len(rows)} to remove ({counts})"
            if rows
            else "No pairs below the threshold"
        )
        self.apply_button.setEnabled(bool(rows))

    @editor_apply
    def apply(self) -> None:
        """Write the complete displayed batch, refresh its baseline and report counts."""
        result = run(
            self.package,
            self.chosen_masters(),
            self.threshold.value,
            expected=self._kerning_snapshot,
        )
        self.last_result = result
        self._batch_written = any(result.values())
        fontlab.UpdateAll()
        self.refresh_after_apply(self.refresh)
        self.status.setText(
            f"Removed {sum(result.values())} pairs ("
            + " · ".join(f"{m} {n}" for (m, n) in result.items())
            + ")"
        )


def main() -> Any:
    """Replace only this tool's registry entry and show the owned modeless dialog."""
    return ap.scripting.show_script_dialog(RemoveSmall, KEY)


if __name__ == "__main__":
    main()
