# this_file: Scripts/Kerning/Compare Masters.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Compare Masters
"""Line up every kerning pair across all masters and flag the ones that look inconsistent.

What it does:
    Each row is one pair (glyph or @class sides) with its value on every master; a pair missing
    on a master shows a dash. Rows are flagged when the sign flips between masters, when a pair
    exists on some masters only, or when neighbouring masters differ by more than the jump
    threshold. Tick "Only flagged" to proof just those. Nothing is edited.

How it works:
    Union explicit pair keys across masters, preserve missing values as absent
    cells and flag sign changes, partial presence or jumps above the chosen
    threshold.

Why this design:
    A missing pair differs from an explicit zero; separate display values help
    identify the type of inconsistency.

How to use:
    Run Kerning > Compare Masters. Set the jump threshold, inspect reasons and
    use Only flagged to reduce the table to candidates for manual proofing.

Benefit:
    Review family kerning differences without filling absent pairs or changing
    values.
"""

import itertools
from typing import Any

from fly import ap, qt

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui
# The tiny facade stays lazy until a native menu script asks for its panel.
from fly.ap.scripting import (
    kerning_dialog_type,
    kerning_pairs,
)
from fly.ap.scripting import (
    kerning_snapshot_refresh as snapshot_refresh,
)
from fly.ap.scripting import (
    names_muted as muted,
)

KerningDialog = kerning_dialog_type()

TITLE = "Compare Kerning Across Masters"
KEY = "kerning_compare_masters"


# ---------------------------------------------------------------- core
def table(
    package: Any, masters: list[str]
) -> dict[tuple[str, str], list[float | None]]:
    """{(left, right): [value or None per master]} sorted by pair."""
    per_master = [kerning_pairs(package, m) for m in masters]
    keys = sorted(set().union(*per_master)) if per_master else []
    return {k: [p.get(k) for p in per_master] for k in keys}


def flags(values: list[float | None], threshold: float) -> list[str]:
    """Reasons a row looks inconsistent: 'sign', 'missing', 'jump'."""
    present = [v for v in values if v is not None]
    reasons = []
    if any(v < 0 for v in present) and any(v > 0 for v in present):
        reasons.append("sign")
    if len(present) < len(values):
        reasons.append("missing")
    if any(abs(b - a) > threshold for a, b in itertools.pairwise(present)):
        reasons.append("jump")
    return reasons


# ---------------------------------------------------------------- GUI


class CompareMasters(KerningDialog):
    """Retain the original Compare Masters controls on the shared owned panel."""

    def __init__(self, parent: Any = None) -> None:
        """Initialize owned controls without changing the font."""
        KerningDialog.__init__(self, parent, TITLE, KEY)

        self.rows, self.shown = {}, []
        root = self.root

        controls = QtGui.QHBoxLayout()
        controls.setSpacing(10)
        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText("Filter pairs, e.g. A or @L_")
        self.threshold = QtGui.QSpinBox()
        self.threshold.setRange(0, 1000)
        self.threshold.setValue(40)
        self.threshold.setSuffix(" units")
        self.threshold.setAlignment(QtCore.Qt.AlignRight)
        self.only_flagged = QtGui.QCheckBox("Only flagged")
        controls.addWidget(self.search, 1)
        controls.addWidget(QtGui.QLabel("Jump above"))
        controls.addWidget(self.threshold)
        controls.addWidget(self.only_flagged)
        root.addLayout(controls)

        self.table = QtGui.QTableWidget(0, len(self.masters) + 2)
        self.table.setHorizontalHeaderLabels(["Pair", *self.masters, "Flags"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(260)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.reload_button = QtGui.QPushButton("Reload")
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        self._connect(self.search.textChanged, lambda *a: self.fill())
        self._connect(self.threshold.valueChanged, lambda *a: self.fill())
        self._connect(self.only_flagged.toggled, lambda *a: self.fill())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.reload()

    @snapshot_refresh
    def reload(self) -> None:
        """Read every master without changing the active master."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        self.rows = table(self.package, self.masters)
        self.subtitle.setText(
            f"{len(self.rows)} pairs across {len(self.masters)} masters. Flags: sign = the value "
            "changes sign, missing = absent on some masters, jump = neighbouring masters "
            "differ by more than the threshold.",
        )
        self.fill()

    @snapshot_refresh
    def fill(self) -> None:
        """Render the complete filtered rows from the current snapshot."""
        needle = self.search.text.strip()
        threshold = self.threshold.value
        warn = QtGui.QColor(196, 72, 48)
        self.shown = []
        for (left, right), values in self.rows.items():
            if needle and needle not in left and needle not in right:
                continue
            reasons = flags(values, threshold)
            if self.only_flagged.checked and not reasons:
                continue
            self.shown.append(((left, right), values, reasons))
        self.table.setRowCount(len(self.shown))
        for row, ((left, right), values, reasons) in enumerate(self.shown):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(f"{left}  {right}"))
            for column, value in enumerate(values, 1):
                item = QtGui.QTableWidgetItem("–" if value is None else f"{value:g}")
                item.setTextAlignment(
                    int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter),
                )
                self.table.setItem(row, column, item)
            note = QtGui.QTableWidgetItem(", ".join(reasons))
            if reasons:
                note.setForeground(QtGui.QBrush(warn))
            self.table.setItem(row, len(values) + 1, note)
        flagged = sum(1 for values in self.rows.values() if flags(values, threshold))
        self.status.setText(
            f"{len(self.shown)} rows shown · {flagged} of {len(self.rows)} pairs flagged",
        )


def main() -> Any:
    """Replace the original registry window and show this owned modeless panel."""
    return ap.scripting.show_script_dialog(CompareMasters, KEY)


if __name__ == "__main__":
    main()
