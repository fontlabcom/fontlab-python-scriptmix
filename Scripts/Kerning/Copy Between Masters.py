# this_file: Scripts/Kerning/Copy Between Masters.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Copy Between Masters
"""Copy the kerning of one master to other masters, optionally scaled.

Start a new master's kerning from an existing one, or push corrections from the Regular to its
neighbours. "Replace" makes the targets identical to the source, "Add missing" only adds pairs
the target lacks, "Overwrite matching" updates pairs both have. The summary shows, per target,
how many pairs are added, changed and removed. One Apply is one Undo step for all targets."""

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

TITLE = "Copy Kerning Between Masters"
KEY = "kerning_copy_between_masters"
MODES = [
    ("Replace all pairs", "replace"),
    ("Add missing pairs only", "missing"),
    ("Overwrite matching pairs, keep others", "matching"),
]


def write_kerning(
    package: Any, edits: dict[str, dict[tuple[str, str], int | None]]
) -> None:
    """Apply a fully validated multi-master batch using the tool's native Undo label."""
    api.write_kerning(package, edits, TITLE)


scaled, plan, summary = api.scaled, api.copy_plan, api.summary


def run(
    package: Any,
    source_master: str,
    targets: list[str],
    mode: str,
    percent: float,
    *,
    expected: Any = None,
) -> dict[str, tuple[int, int, int]]:
    """Stage all target masters before a single snapshot-bound history batch."""
    return api.copy_run(
        package,
        source_master,
        targets,
        mode,
        percent,
        expected=expected,
        undo_name=TITLE,
    )


class CopyKerning(KerningEditDialog):
    """Retain the complete original Copy Between Masters workflow with shared native safety."""

    def __init__(self, parent: Any = None) -> None:
        """Create all original controls on the shared snapshot-bound owned panel."""
        KerningEditDialog.__init__(self, parent, TITLE, KEY)
        root = self.root
        self.setMinimumWidth(560)
        self.filling = False
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.source = QtGui.QComboBox()
        for name in self.masters:
            self.source.addItem(name)
        if self.current_master in self.masters:
            self.source.setCurrentIndex(self.masters.index(self.current_master))
        self.mode = QtGui.QComboBox()
        for label, _ in MODES:
            self.mode.addItem(label)
        self.percent = QtGui.QDoubleSpinBox()
        self.percent.setRange(0.0, 400.0)
        self.percent.setDecimals(1)
        self.percent.setValue(100.0)
        self.percent.setSuffix(" %")
        self.percent.setAlignment(QtCore.Qt.AlignRight)
        form.addWidget(QtGui.QLabel("From"), 0, 0)
        form.addWidget(self.source, 0, 1)
        form.addWidget(QtGui.QLabel("Scale"), 0, 2)
        form.addWidget(self.percent, 0, 3)
        form.addWidget(QtGui.QLabel("Mode"), 1, 0)
        form.addWidget(self.mode, 1, 1, 1, 3)
        form.setColumnStretch(1, 2)
        form.setColumnStretch(3, 1)
        root.addLayout(form)
        targets_label = QtGui.QLabel("To masters")
        targets_label.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(targets_label)
        self.targets = QtGui.QTableWidget(0, 5)
        self.targets.setHorizontalHeaderLabels(
            ["Master", "Pairs now", "Added", "Changed", "Removed"]
        )
        self.targets.verticalHeader().setVisible(False)
        self.targets.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.targets.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.targets.setAlternatingRowColors(True)
        self.targets.setShowGrid(False)
        header = self.targets.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.targets.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.targets.setMinimumHeight(160)
        root.addWidget(self.targets, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Copy")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self.add_refresh(footer, self.rebuild)
        self.checked = dict.fromkeys(self.masters, False)
        self._connect(self.source.currentIndexChanged, lambda *a: self.rebuild())
        self._connect(self.mode.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.percent.valueChanged, lambda *a: self.refresh())
        self._connect(self.targets.itemChanged, self.toggled)
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.rebuild()

    def source_master(self) -> str:
        """Return the chosen source master without activating it in FontLab."""
        return self.masters[self.source.currentIndex] if self.masters else ""

    def chosen_targets(self) -> list[str]:
        """Return checked target names, excluding the current source."""
        return [
            m for m in self.masters if self.checked.get(m) and m != self.source_master()
        ]

    def set_targets(self, names: list[str]) -> None:
        """Tick exactly these target masters (used by scripts and tests)."""
        self.checked = {m: m in names for m in self.masters}
        self.refresh()

    def toggled(self, item: Any) -> None:
        """Update the original controls while retaining the shared safety boundary."""
        if self.filling or item.column() != 0:
            return
        self.checked[item.text()] = item.checkState() == QtCore.Qt.Checked
        self.refresh()

    def rebuild(self) -> None:
        """One checkable row per target master; rebuilt only when the source changes."""
        others = [m for m in self.masters if m != self.source_master()]
        self.filling = True
        self.targets.setRowCount(len(others))
        for row, master in enumerate(others):
            name = QtGui.QTableWidgetItem(master)
            name.setCheckState(
                QtCore.Qt.Checked if self.checked.get(master) else QtCore.Qt.Unchecked
            )
            self.targets.setItem(row, 0, name)
            for column in range(1, 5):
                item = QtGui.QTableWidgetItem("")
                item.setTextAlignment(
                    int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                )
                self.targets.setItem(row, column, item)
        self.filling = False
        self.refresh()

    @editor_refresh
    def refresh(self) -> None:
        """Update the numbers in place: items are never replaced inside their own signal."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        source_name = self.source_master()
        source = kerning_pairs(self.package, source_name)
        self.subtitle.setText(
            f"{source_name} has {len(source)} pairs. Tick the masters that receive them."
        )
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        plain = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        self.filling = True
        total = 0
        for row in range(self.targets.rowCount):
            name = self.targets.item(row, 0)
            master = name.text()
            name.setCheckState(
                QtCore.Qt.Checked if self.checked.get(master) else QtCore.Qt.Unchecked
            )
            target = kerning_pairs(self.package, master)
            numbers = [len(target), "", "", ""]
            if self.checked.get(master):
                (added, changed, removed) = summary(
                    target, plan(source, target, self.mode_key(), self.percent.value)
                )
                numbers = [len(target), added, changed, removed]
                total += added + changed + removed
            for column, value in enumerate(numbers, 1):
                item = self.targets.item(row, column)
                item.setText(str(value))
                item.setForeground(
                    QtGui.QBrush(accent if column > 1 and value else plain)
                )
        self.filling = False
        chosen = self.chosen_targets()
        self.status.setText(
            f"{total} pair edits in {len(chosen)} master{('s' if len(chosen) != 1 else '')}"
            if chosen
            else "Tick at least one target master"
        )
        self.apply_button.setEnabled(bool(chosen) and total > 0)

    def mode_key(self) -> str:
        """Return the exact selected copy policy used in preview and Apply."""
        return MODES[self.mode.currentIndex][1]

    @editor_apply
    def apply(self) -> None:
        """Write the complete displayed batch, refresh its baseline and report counts."""
        result = run(
            self.package,
            self.source_master(),
            self.chosen_targets(),
            self.mode_key(),
            self.percent.value,
            expected=self._kerning_snapshot,
        )
        self.last_result = result
        self._batch_written = any(sum(counts) for counts in result.values())
        fontlab.UpdateAll()
        self.refresh_after_apply(self.refresh)
        self.status.setText(
            "Copied: "
            + " · ".join(f"{m} +{a} ~{c} −{r}" for (m, (a, c, r)) in result.items())
        )


def main() -> Any:
    """Replace only this tool's registry entry and show the owned modeless dialog."""
    return ap.scripting.show_script_dialog(CopyKerning, KEY)


if __name__ == "__main__":
    main()
