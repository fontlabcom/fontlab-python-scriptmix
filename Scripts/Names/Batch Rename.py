# FLM: Names · Batch Rename
# this_file: Scripts/Names/Batch Rename.py
# SPDX-License-Identifier: Apache-2.0
"""Find and replace in glyph names (plain text or regular expression) with a live preview.

Every new name is checked before anything changes: invalid names, names that
already exist in the font and two glyphs getting the same name are refused
(FontLab would otherwise replace the existing glyph). Components that use a
renamed glyph follow it. One Apply is one Undo step.
"""

import re
from typing import Any

import fly
import fontlab
from fly.ap.scripting import names_editor_api
from PythonQt import QtGui

scripting = fly.ap.scripting
api = names_editor_api()
NamesEditDialog = scripting.names_edit_dialog_type()
muted = NamesEditDialog.muted

TITLE = "Batch Rename"
KEY = "names_batch_rename"
VALID = api.VALID


current_package = scripting.current_package

selected_names = api.selected_names

font_names = api.font_names

new_name = api.new_name

auto_links = api.auto_links

auto_refusal = api.auto_refusal

plan = api.rename_plan


def run(package: Any, rows: list, *, expected: Any = None) -> list:
    """Rename the complete accepted preview with native component propagation."""
    return api.rename(package, rows, TITLE, expected=expected)


class Renamer(NamesEditDialog):
    """Retain the original Batch Rename controls, defaults and editing actions."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control before any fallible font read."""
        super().__init__(parent, TITLE, KEY, "name")
        root = self.root
        self.setMinimumWidth(540)
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.find = QtGui.QLineEdit()
        self.find.setPlaceholderText("text or pattern, e.g. ^uni or \\.alt$")
        self.replace = QtGui.QLineEdit()
        self.replace.setPlaceholderText("replacement, groups as \\1")
        self.regex = QtGui.QCheckBox("Regular expression")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Selected glyphs ({len(self.selection)})")
        self.scope.addItem("All glyphs in the font")
        form.addWidget(QtGui.QLabel("Find"), 0, 0)
        form.addWidget(self.find, 0, 1)
        form.addWidget(QtGui.QLabel("Replace"), 1, 0)
        form.addWidget(self.replace, 1, 1)
        form.addWidget(QtGui.QLabel("Glyphs"), 2, 0)
        form.addWidget(self.scope, 2, 1)
        form.addWidget(self.regex, 3, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = self.make_table(["Glyph", "New name", "Check"])
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setMinimumHeight(220)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Rename")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        for line in (self.find, self.replace):
            self._connect(line.textChanged, lambda *a: self.refresh())
        self._connect(self.regex.toggled, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh(self.refresh)

    def names(self) -> list[str]:
        """Return the captured selection or every current name for this preview."""
        self.check_binding()
        return self.selection if self.scope.currentIndex == 0 else font_names()

    @scripting.names_editor_read
    def refresh(self) -> None:
        """Render the complete original preview and enable only actionable results."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.apply_button.setEnabled(False)
            return
        self.subtitle.setText(
            "Renames the glyphs and every component that uses them. "
            "Kerning and features keep the old names; glyphs in auto-layer composites are refused "
            "(FontLab rebuilds those from their names).",
        )
        self.links = auto_links(self.package, font_names())
        error = ""
        try:
            self.rows = plan(
                self.names(),
                font_names(),
                self.find.text,
                self.replace.text,
                self.regex.isChecked(),
                self.links,
            )
        except re.error as exc:
            self.rows, error = [], f"Pattern error: {exc}"
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        alert = QtGui.QColor("#d33")
        self.table.setRowCount(len(self.rows))
        for row, (old, new, status) in enumerate(self.rows):
            cells = [old, new, "✓" if status == "ok" else status]
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column == 1 and status == "ok":
                    item.setForeground(QtGui.QBrush(accent))
                if column == 2:
                    item.setForeground(
                        QtGui.QBrush(accent if status == "ok" else alert),
                    )
                self.table.setItem(row, column, item)
        ok = sum(1 for r in self.rows if r[2] == "ok")
        refused = len(self.rows) - ok
        self.apply_button.setEnabled(ok > 0)
        if error:
            self.status.setText(error)
        elif not self.find.text:
            self.status.setText("Type the text to find.")
        else:
            note = f" · {refused} refused" if refused else ""
            self.status.setText(f"{ok} glyph{'s' if ok != 1 else ''} to rename{note}")

    @scripting.names_editor_apply
    def apply(self) -> None:
        """Write exactly the staged batch and refresh its visible outcome."""
        renamed = run(self.package, self.rows, expected=self._names_snapshot)
        self._batch_written = bool(renamed)
        self._last_applied = renamed
        self.last_result = {
            "renamed": renamed,
            "refused": [r for r in self.rows if r[2] != "ok"],
        }
        self.links = auto_links(self.package, font_names())
        fontlab.UpdateAll()
        renamed_map = dict(renamed)
        self.selection = [renamed_map.get(n, n) for n in self.selection]
        self.refresh()
        self.status.setText(
            f"Renamed {len(renamed)} glyph{'s' if len(renamed) != 1 else ''}",
        )

    def load_initial(self) -> None:
        """Read the original selection and references after safe UI construction."""
        self.selection = selected_names()
        self.links = auto_links(self.package, font_names())
        blocked = self.scope.blockSignals(True)
        try:
            self.scope.setItemText(0, f"Selected glyphs ({len(self.selection)})")
            if not self.selection:
                self.scope.setCurrentIndex(1)
        finally:
            self.scope.blockSignals(blocked)


def main() -> Any:
    """Replace only this owned tool and share guarded native Close disposal."""
    return scripting.show_script_dialog(Renamer, KEY)


if __name__ == "__main__":
    main()
