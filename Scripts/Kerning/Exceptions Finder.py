# this_file: Scripts/Kerning/Exceptions Finder.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Exceptions Finder
"""Find kerning exceptions: pairs that override a class pair, and remove the ones you tick.

An exception is a pair whose glyph side belongs to a kerning class that already has a pair
with the same partner (A V overriding @A V). Exceptions with the same value as the class pair
are redundant and safe to delete; the others are deliberate overrides worth a second look.
Tick rows (or "Tick redundant") and Remove; one Undo step for all masters.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import kerning_edit_dialog_type, kerning_selection_api
from fly.ap.scripting import kerning_editor_apply as editor_apply
from fly.ap.scripting import kerning_editor_make_table as make_table
from fly.ap.scripting import kerning_editor_refresh as editor_refresh
from fly.ap.scripting import names_muted as muted

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui
api = kerning_selection_api()
KerningEditDialog = kerning_edit_dialog_type()
current_package = ap.scripting.current_package
kerning_pairs = ap.scripting.kerning_pairs

TITLE = "Kerning Exceptions"
KEY = "kerning_exceptions_finder"


class_maps = api.class_maps
native_side = ap.scripting.kerning_editor_api().native_side
exceptions = api.exceptions
find = api.find


def write_kerning(
    package: Any, edits: dict[str, dict[tuple[str, str], int | None]]
) -> None:
    """Retain the original console interface through the shared preflight writer."""
    ap.scripting.kerning_editor_api().write_kerning(package, edits, TITLE)


class ExceptionsFinder(KerningEditDialog):
    """Preserve all original controls on the shared snapshot-bound native panel."""

    def __init__(self, parent: Any = None) -> None:
        """Create original controls; connect every callback through owned guards."""
        KerningEditDialog.__init__(self, parent, TITLE, KEY)
        self.setMinimumWidth(640)
        self.resize(680, 560)
        self.rows = []
        self.filling = False
        root = self.root

        form = QtGui.QHBoxLayout()
        form.setSpacing(10)
        form.addWidget(QtGui.QLabel("Masters"))
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(self.scope, 1)
        self.tick_redundant = QtGui.QPushButton("Tick redundant")
        self.tick_none = QtGui.QPushButton("Untick all")
        form.addWidget(self.tick_redundant)
        form.addWidget(self.tick_none)
        root.addLayout(form)

        self.table = make_table(
            ["Exception", "Master", "Value", "Overrides", "Class value", "Δ"]
        )
        self.table.setMinimumHeight(240)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Remove ticked")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self.add_refresh(footer, self.refresh)
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.table.itemChanged, lambda *a: self.count())
        self._connect(
            self.tick_redundant.clicked,
            lambda *a: self.tick(lambda row: row[2] == row[4]),
        )
        self._connect(self.tick_none.clicked, lambda *a: self.tick(lambda row: False))
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def chosen_masters(self) -> list[str]:
        """Return current or all originally captured masters, retaining scope semantics."""
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    @editor_refresh
    def refresh(self) -> None:
        """Re-scan the kerning (call again after editing kerning elsewhere)."""
        self.rows = find(self.package, self.chosen_masters()) if self.package else []
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            redundant = sum(1 for r in self.rows if r[2] == r[4])
            self.subtitle.setText(
                f"{len(self.rows)} exceptions, {redundant} of them redundant (same value as the class pair "
                "they override). Tick the ones to delete.",
            )
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        dim = QtGui.QColor(muted(self))
        self.filling = True
        self.table.setRowCount(len(self.rows))
        for row, (master, pair, value, broader, broader_value) in enumerate(self.rows):
            name = QtGui.QTableWidgetItem(f"{pair[0]}  {pair[1]}")
            name.setCheckState(QtCore.Qt.Unchecked)
            self.table.setItem(row, 0, name)
            self.table.setItem(row, 1, QtGui.QTableWidgetItem(master))
            delta = value - broader_value
            cells = [
                (2, f"{value:g}"),
                (3, f"{broader[0]}  {broader[1]}"),
                (4, f"{broader_value:g}"),
                (5, "same" if not delta else f"{delta:+g}"),
            ]
            for column, text in cells:
                item = QtGui.QTableWidgetItem(text)
                if column != 3:
                    item.setTextAlignment(
                        int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter),
                    )
                if column == 5:
                    item.setForeground(QtGui.QBrush(dim if not delta else accent))
                self.table.setItem(row, column, item)
        self.filling = False
        self.count()

    def ticked(
        self,
    ) -> list[tuple[str, tuple[str, str], float, tuple[str, str], float]]:
        """Read actual table check states; never substitute stored tick intentions."""
        return [
            self.rows[r]
            for r in range(self.table.rowCount)
            if self.table.item(r, 0).checkState() == QtCore.Qt.Checked
        ]

    def tick(self, rule: Any) -> None:
        """Apply a predicate to actual row checkboxes and recount once."""
        self.filling = True
        for r, row in enumerate(self.rows):
            self.table.item(r, 0).setCheckState(
                QtCore.Qt.Checked if rule(row) else QtCore.Qt.Unchecked,
            )
        self.filling = False
        self.count()

    def count(self) -> None:
        """Update original tick counts and enable Apply only for selected rows."""
        if self.filling:
            return
        ticked = self.ticked()
        self.status.setText(
            f"{len(ticked)} of {len(self.rows)} ticked"
            if self.rows
            else "No exceptions found",
        )
        self.apply_button.setEnabled(bool(ticked))
        self.tick_redundant.setEnabled(any(r[2] == r[4] for r in self.rows))

    @editor_apply
    def apply(self) -> None:
        """Preflight the complete ticked batch, write once, then refresh its baseline."""
        edits = api.exception_plan(self.ticked())
        self.write_edits(edits, TITLE)
        self.last_result = {m: len(p) for m, p in edits.items()}
        fontlab.UpdateAll()
        self.refresh_after_apply(self.refresh)
        self.status.setText(f"Removed {sum(self.last_result.values())} exceptions")


def main() -> Any:
    """Replace only this tool's registry entry and show its owned modeless dialog."""
    return ap.scripting.show_script_dialog(ExceptionsFinder, KEY)


if __name__ == "__main__":
    main()
