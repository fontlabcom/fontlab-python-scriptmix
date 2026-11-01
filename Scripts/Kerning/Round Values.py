# this_file: Scripts/Kerning/Round Values.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Round Values
"""Round kerning values to a step (5, 10 …) on one or all masters, previewing every change.

What it does:
    Rounded kerning is easier to read, compare and edit by hand, and interpolates to tidier
    instances. Halves round away from zero, as FontLab rounds. Pairs that round to 0 can be deleted
    instead of being kept as explicit zeros. One Apply is one Undo step for all masters.

How it works:
    Build a complete explicit-pair plan for current or all masters. Round
    values to the chosen step with halves away from zero and apply the
    selected zero-pair policy.

Why this design:
    Previewing zero deletions separately avoids treating an explicit zero pair
    as interchangeable with an absent pair.

How to use:
    Run Kerning > Round Values. Choose a step, master scope and zero-pair
    option. Review the old/new rows, then Apply to write the displayed batch.

Benefit:
    Make stored kerning values easier to inspect; Apply is recorded as one
    Undo step.
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

TITLE = "Round Kerning"
KEY = "kerning_round_values"


def write_kerning(
    package: Any, edits: dict[str, dict[tuple[str, str], int | None]]
) -> None:
    """Apply a fully validated multi-master batch using the tool's native Undo label."""
    api.write_kerning(package, edits, TITLE)


round_to, plan = api.round_to, api.round_plan


class RoundKerning(KerningEditDialog):
    """Retain the complete original Round Values workflow with shared native safety."""

    def __init__(self, parent: Any = None) -> None:
        """Create all original controls on the shared snapshot-bound owned panel."""
        KerningEditDialog.__init__(self, parent, TITLE, KEY)
        root = self.root
        self.setMinimumWidth(540)
        self.todo = {}
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.step = QtGui.QSpinBox()
        self.step.setRange(2, 100)
        self.step.setValue(5)
        self.step.setSuffix(" units")
        self.step.setAlignment(QtCore.Qt.AlignRight)
        self.drop_zero = QtGui.QCheckBox("Delete pairs that round to 0")
        self.drop_zero.setChecked(True)
        form.addWidget(QtGui.QLabel("Round to"), 0, 0)
        form.addWidget(self.step, 0, 1)
        form.addWidget(self.drop_zero, 1, 1, 1, 2)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        form.addWidget(self.scope, 2, 1, 1, 2)
        form.setColumnStretch(1, 1)
        root.addLayout(form)
        self.table = make_table(["Pair", "Master", "Value", "New value"])
        root.addWidget(self.table, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self.add_refresh(footer, self.refresh)
        for widget in self.inputs():
            signal = (
                widget.toggled
                if isinstance(widget, QtGui.QCheckBox)
                else widget.currentIndexChanged
                if isinstance(widget, QtGui.QComboBox)
                else widget.valueChanged
            )
            self._connect(signal, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def chosen_masters(self) -> list[str]:
        """Return the original current-master scope or all original masters."""
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    @editor_refresh
    def refresh(self) -> None:
        """Render the complete shared preview."""
        self.refresh_values()

    @editor_apply
    def apply(self) -> None:
        """Render the complete shared preview."""
        self.apply_values(TITLE)

    def inputs(self) -> list[Any]:
        """List every original planning control whose change refreshes the preview."""
        return [self.step, self.drop_zero, self.scope]

    def plan(self) -> dict[str, dict[tuple[str, str], tuple[float, int | None]]]:
        """Build the complete per-master preview from the current control values."""
        return plan(
            self.package,
            self.chosen_masters(),
            self.step.value,
            self.drop_zero.isChecked(),
        )

    def explain(self) -> str:
        """Describe the selected numerical operation in the visible subtitle."""
        return f"Values snap to multiples of {self.step.value}; halves round away from zero."


def main() -> Any:
    """Replace only this tool's registry entry and show the owned modeless dialog."""
    return ap.scripting.show_script_dialog(RoundKerning, KEY)


if __name__ == "__main__":
    main()
