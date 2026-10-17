# FLM: Names · Glyph Notes
# this_file: Scripts/Names/Glyph Notes.py
# SPDX-License-Identifier: Apache-2.0
"""Read and edit the note of the selected glyph, and browse every glyph that has a note.

The editor shows the note of the first glyph selected in the Font window;
Save writes it (one Undo step). The list below collects all notes in the
font; click one to edit it, double-click to also select that glyph.
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

TITLE = "Glyph Notes"
KEY = "names_glyph_notes"


current_package = scripting.current_package

focused_name = api.focused_name

select_in_font_window = api.select_in_font_window

notes = api.notes

auto_dependants = api.auto_dependants

rebuild_note = api.rebuild_note

show_rebuilds = api.show_rebuilds


def run(package: Any, name: str, text: str, *, expected: Any = None) -> bool:
    """Save complete note text, skipping identical text without history."""
    return api.set_note(package, name, text, TITLE, expected=expected)


class GlyphNotes(NamesEditDialog):
    """Retain the original Glyph Notes controls, defaults and editing actions."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control before any fallible font read."""
        super().__init__(parent, TITLE, KEY, "note")
        root = self.root
        self.setMinimumWidth(480)
        self.resize(500, 540)
        self.editor_label = QtGui.QLabel()
        bold = self.editor_label.font
        bold.setBold(True)
        self.editor_label.setFont(bold)
        root.addWidget(self.editor_label)
        self.editor = QtGui.QPlainTextEdit()
        self.editor.setPlaceholderText("Write a note for this glyph…")
        self.editor.setMinimumHeight(110)
        root.addWidget(self.editor)

        self.list_label = QtGui.QLabel()
        self.list_label.setFont(bold)
        root.addWidget(self.list_label)
        self.list = self.make_table(["Glyph", "Note"])
        self.list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        header = self.list.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        root.addWidget(self.list, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)  # the auto-composite note can be long
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Save note")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.editor.textChanged, lambda *a: self.edited())
        self._connect(self.list.cellClicked, lambda row, *a: self.load_row(row))
        self._connect(
            self.list.cellDoubleClicked,
            lambda row, *a: self.load_row(row, select=True),
        )
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh(self.initialize_notes)

    def stored(self) -> str:
        """Return the exact note displayed when this editor was loaded."""
        return self.stored_note()

    @scripting.names_editor_read
    def load(self, name: Any) -> None:
        """Load the chosen note without changing Font-window selection."""
        self.glyph_name = name
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            self.subtitle.setText(
                "Notes travel with the glyph in .vfc/.vfj files. Select a glyph in the Font "
                "window, or pick one below.",
            )
        self.editor_label.setText(f"Note for {name}" if name else "No glyph selected")
        self.editor.setEnabled(bool(name))
        self.editor.setPlainText(self.stored())
        self.edited()

    def load_row(self, row: Any, select: Any = False) -> None:
        """Load a listed note and optionally select its glyph in the Font window."""
        self.ensure_edit_snapshot()
        if 0 <= row < len(self.entries):
            self.load(self.entries[row][0])
            if select:
                self.ensure_edit_snapshot()
                select_in_font_window(self.entries[row][0])
                self._names_snapshot = self.capture()

    @scripting.names_editor_read
    def reload_list(self) -> None:
        """Read every nonblank note and show its first line with complete tooltips."""
        self.entries = notes(self.package) if self.package else []
        self.list_label.setText(f"Glyphs with notes ({len(self.entries)})")
        self.list.setRowCount(len(self.entries))
        for row, (name, text) in enumerate(self.entries):
            first = text.strip().splitlines()[0]
            for column, value in enumerate((name, first)):
                item = QtGui.QTableWidgetItem(value)
                item.setToolTip(text)
                self.list.setItem(row, column, item)

    def edited(self) -> None:
        """Update note dirty state and the original auto-layer warning."""
        self.edited_listing()
        show_rebuilds(self, [self.glyph_name] if self.glyph_name else [])

    def edited_listing(self) -> None:
        """Enable Save only when editor text differs from its displayed baseline."""
        dirty = bool(self.glyph_name) and self.editor.toPlainText() != self.stored()
        self.apply_button.setEnabled(dirty)
        self.status.setText("Unsaved changes" if dirty else "")

    @scripting.names_editor_apply
    def apply(self) -> None:
        """Write exactly the staged batch and refresh its visible outcome."""
        changed = run(
            self.package,
            self.glyph_name,
            self.editor.toPlainText(),
            expected=self._names_snapshot,
        )
        self._batch_written = bool(changed)
        self._last_applied = changed
        self.last_result = {"glyph": self.glyph_name, "changed": changed}
        fontlab.UpdateAll()
        self.reload_list()
        self.edited()
        self.status.setText(
            f"Saved note for {self.glyph_name}" if changed else "No change",
        )

    def load_initial(self) -> None:
        """Read the original selection and references after safe UI construction."""
        self.glyph_name = focused_name()

    @scripting.names_editor_read
    def initialize_notes(self) -> None:
        """Load the selected editor and complete notes list as one initial scan."""
        self.load(self.glyph_name)
        self.reload_list()


def main() -> Any:
    """Replace only this owned tool and share guarded native Close disposal."""
    return scripting.show_script_dialog(GlyphNotes, KEY)


if __name__ == "__main__":
    main()
