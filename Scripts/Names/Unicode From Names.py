# FLM: Names · Unicode From Names
# this_file: Scripts/Names/Unicode From Names.py
# SPDX-License-Identifier: Apache-2.0
"""Assign Unicode code points derived from glyph names, with a preview first.

Understands uniXXXX and uXXXX[XX] names, a small Adobe Glyph List table and
accented Latin names (Wacute -> LATIN CAPITAL LETTER W WITH ACUTE via
unicodedata). Suffixed alternates and ligatures are left alone. A code point
already used by another glyph is reported, never stolen. One Undo step.
"""

from typing import Any

import fly
import fontlab
from fly.ap.scripting import names_editor_api
from PythonQt import QtGui

scripting = fly.ap.scripting
api = names_editor_api()
NamesEditDialog = scripting.names_edit_dialog_type()
muted = NamesEditDialog.muted

TITLE = "Unicode from Names"
KEY = "names_unicode_from_names"
AGL_TEXT = api.AGL_TEXT
AGL = api.AGL
ACCENTS = api.ACCENTS
UNI = api.UNI
U = api.U


current_package = scripting.current_package

selected_names = api.selected_names

code_for_name = api.code_for_name

hexes = api.hexes

auto_dependants = api.auto_dependants

rebuild_note = api.rebuild_note

show_rebuilds = api.show_rebuilds

font_unicodes = api.font_unicodes

plan = api.unicode_plan


def run(package: Any, rows: list, *, expected: Any = None) -> list:
    """Assign only accepted derived encodings after complete preflight."""
    return api.assign_unicodes(package, rows, TITLE, expected=expected)


class UnicodeFromNames(NamesEditDialog):
    """Retain the original Unicode From Names controls, defaults and editing actions."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control before any fallible font read."""
        super().__init__(parent, TITLE, KEY, "unicodes")
        root = self.root
        self.setMinimumWidth(560)
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.scope = QtGui.QComboBox()
        self.overwrite = QtGui.QCheckBox("Replace a different existing code point")
        form.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
        form.addWidget(self.scope, 0, 1)
        form.addWidget(self.overwrite, 1, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = self.make_table(
            ["Glyph", "Current", "From name", "Source", "Action"]
        )
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setMinimumHeight(240)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)  # the auto-composite note can be long
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.show_all = QtGui.QCheckBox("Show unchanged")
        footer.addWidget(self.show_all)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Assign")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.overwrite.toggled, lambda *a: self.refresh())
        self._connect(self.show_all.toggled, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh(self.reload)

    @scripting.names_editor_reload
    def reload(self) -> None:
        """Re-read the font and the selection (also after edits made elsewhere)."""
        self.selection = selected_names() if self.package else []
        index = (
            self.scope.currentIndex
            if self.scope.count
            else (0 if len(self.selection) > 1 else 1)
        )
        with self.block_signals(self.scope):
            self.scope.clear()
            self.scope.addItem(f"Selected glyphs ({len(self.selection)})")
            self.scope.addItem("All glyphs in the font")
            self.scope.setCurrentIndex(index)
        self.refresh()

    @scripting.names_editor_read
    def refresh(self) -> None:
        """Render the complete original preview and enable only actionable results."""
        self.refresh_listing()
        show_rebuilds(self, [row[0] for row in self.rows if row[4] == "assign"])

    def refresh_listing(self) -> None:
        """Populate original counts and result cells without changing the font."""
        self.check_binding()
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.apply_button.setEnabled(False)
            return
        unicodes = font_unicodes()
        names = self.selection if self.scope.currentIndex == 0 else list(unicodes)
        self.rows = plan(names, unicodes, self.overwrite.isChecked())
        shown = [r for r in self.rows if r[4] != "same" or self.show_all.isChecked()]
        self.subtitle.setText(
            f"{len(names)} glyph{'s' if len(names) != 1 else ''} checked. Names like uni0141, "
            "u1F600, Lslash or Wacute give a code point; suffixed names are skipped.",
        )
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        alert = QtGui.QColor("#d33")
        self.table.setRowCount(len(shown))
        for row, (name, current, code, source, status) in enumerate(shown):
            cells = [name, hexes(current), hexes([code]), source, status]
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column == 2 and status == "assign":
                    item.setForeground(QtGui.QBrush(accent))
                if column == 4 and status not in {"assign", "same"}:
                    item.setForeground(QtGui.QBrush(alert))
                self.table.setItem(row, column, item)
        todo = sum(1 for r in self.rows if r[4] == "assign")
        blocked = sum(1 for r in self.rows if r[4] not in {"assign", "same"})
        same = len(self.rows) - todo - blocked
        self.apply_button.setEnabled(todo > 0)
        self.status.setText(
            f"{todo} to assign · {blocked} blocked · {same} already right",
        )

    @scripting.names_editor_apply
    def apply(self) -> None:
        """Write exactly the staged batch and refresh its visible outcome."""
        changed = run(self.package, self.rows, expected=self._names_snapshot)
        self._batch_written = bool(changed)
        self._last_applied = changed
        self.last_result = {"changed": changed}
        fontlab.UpdateAll()
        self.refresh()
        self.status.setText(
            f"Assigned {len(changed)} code point{'s' if len(changed) != 1 else ''}",
        )

    def load_initial(self) -> None:
        """Read the original selection and references after safe UI construction."""


def main() -> Any:
    """Replace only this owned tool and share guarded native Close disposal."""
    return scripting.show_script_dialog(UnicodeFromNames, KEY)


if __name__ == "__main__":
    main()
