# this_file: Scripts/Names/Glyph Notes.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from the archived Apache-2.0 FontLab samples
# (rescued/samples/names_glyph_notes.py); provenance in NOTICE.
# FLM: Names · Glyph Notes
"""Read and edit the note of one glyph. Browse every glyph that has a note.

WHAT: A non-modal panel shows the note of the first glyph selected in the Font
window in an editor. Save writes it. A list below shows all glyphs that have a
note. A click loads that note into the editor. A double-click also selects the
glyph in the Font window.

HOW: The script scans the whole font. Save rescans, then writes one note as one
Undo step: layers and glyph in one notify list (a glyph alone adds no Undo
step). It then reads the note back and compares it with the text. Double-click
selection goes through the App selection helper, which checks that a regular
Font window is active (fl#8528). The scan, the refusal policy and the one-step
write come from the shared module fly.ap.names_edit. If a write fails part way,
every planned glyph is still notified and stamped, and the message asks you to
use Edit > Undo.

WHY: FontLab rebuilds all auto layers when an auto layer is notified, and Undo
does not restore them. So the script REFUSES to save a note on a glyph that
owns an auto layer, says why, and never puts an auto layer in the notify list.
A base glyph of an auto composite may get a note (native check pending). The
script never reads flGlyph.fgGlyph (that getter can clear a fresh note mirror
on build 9784), never calls UpdateAll (fl#8537), and refuses to write while
native updates are pending.

USE: Select a glyph in the Font window. Run the script. Edit the note. Press
Save note. Pick a row in the list to edit another glyph.

BENEFIT: Notes travel with the glyph in .vfc and .vfj files. The list gives an
overview of all remarks in the font. One Edit > Undo reverts one save.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. Native acceptance pending.
"""

from typing import Any

import fly.ap.names_edit as names_edit  # noqa: PLR0402 - fontlabapp.__getattr__ is native

TITLE = "Glyph Notes"
KEY = "names_glyph_notes"
OPERATION = "metadata"  # names_edit refusal policy for this write


# ------------------------------------------------------------------ core
def notes_in_font(facts: names_edit.Facts) -> list[tuple[str, str]]:
    """Return (glyph name, note) for each glyph with a non-blank note, in font order."""
    out = []
    for name, entry in facts.entries.items():
        text = str(entry.glyph.note or "")
        if text.strip():
            out.append((name, text))
    return out


def first_line(text: str) -> str:
    """Return the first non-blank line of TEXT, trimmed. Empty text gives ""."""
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def save_note(native: Any, qtcore: Any, package_id: int, name: str, text: str) -> bool:
    """Set the note of glyph NAME. One Undo step. Return True when it changed.

    Raise ValueError when the glyph is refused (auto layers, auto base, no
    layers), unknown, the font switched or host updates are pending.
    """
    facts = names_edit.fresh_facts(package_id, native=native)
    if name not in facts.entries:
        raise ValueError(f"{name} is not in the font.")
    if reason := names_edit.refusal(facts, name, OPERATION):
        raise ValueError(f"Cannot edit {name}: {reason}.")
    entry = facts.entries[name]
    if str(entry.glyph.note or "") == text:
        return False

    def mutate() -> None:
        entry.glyph.note = text
        if str(entry.glyph.note or "") != text:
            raise RuntimeError(f"Native note of {name} differs from the text.")

    names_edit.commit(
        TITLE,
        [entry],
        mutate,
        operation=OPERATION,
        facts=facts,
        native=native,
        stamp=qtcore.QDateTime.currentDateTimeUtc(),
    )
    return True


# ------------------------------------------------------------------ panel
def _dialog_type() -> type:
    """Build the panel class lazily. Import Qt and App code only inside FontLab."""
    from fly import ap, qt
    from fly.ap.scripting import names_dialog_type, names_selected_names, select_glyphs

    native = ap.fontlab
    QtCore, QtGui = qt.QtCore, qt.QtGui

    class GlyphNotes(names_dialog_type()):
        """Modeless note editor with a list of all notes."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent, TITLE, KEY)
            self.resize(500, 540)
            self.facts: names_edit.Facts | None = None
            self.glyph_name: str | None = None
            self.entries: list[tuple[str, str]] = []
            self.loaded = ""
            bold = self.subtitle.font
            bold.setBold(True)
            self.editor_label = QtGui.QLabel()
            self.editor_label.setFont(bold)
            self.root.addWidget(self.editor_label)
            self.editor = QtGui.QPlainTextEdit()
            self.editor.setPlaceholderText("Write a note for this glyph…")
            self.editor.setMinimumHeight(110)
            self.root.addWidget(self.editor)
            self.list_label = QtGui.QLabel()
            self.list_label.setFont(bold)
            self.root.addWidget(self.list_label)
            self.list = self.make_table(["Glyph", "Note"])
            self.list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            header = self.list.horizontalHeader()
            header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
            header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
            self.root.addWidget(self.list, 1)
            footer = QtGui.QHBoxLayout()
            self.status = QtGui.QLabel()
            self.status.setWordWrap(True)
            footer.addWidget(self.status, 1)
            self.reload_button = QtGui.QPushButton("Reload")
            self.close_button = QtGui.QPushButton("Close")
            self.apply_button = QtGui.QPushButton("Save note")
            self.apply_button.setDefault(True)
            footer.addWidget(self.reload_button)
            footer.addWidget(self.close_button)
            footer.addWidget(self.apply_button)
            self.root.addLayout(footer)
            self._connect(self.editor.textChanged, lambda *a: self.edited())
            self._connect(self.list.cellClicked, lambda row, *a: self.load_row(row))
            self._connect(
                self.list.cellDoubleClicked,
                lambda row, *a: self.load_row(row, select=True),
            )
            self._connect(self.reload_button.clicked, lambda *a: self.reload())
            self._connect(self.apply_button.clicked, lambda *a: self.apply())
            self._connect(self.close_button.clicked, lambda *a: self.close())
            self.reload()

        def invalidate(self) -> None:
            """Also disable Save when the snapshot is stale."""
            super().invalidate()
            button = getattr(self, "apply_button", None)
            if button is not None:
                button.setEnabled(False)
            self.entries = []
            listing = getattr(self, "list", None)
            if listing is not None:
                listing.setRowCount(0)

        def reload(self, focus: str | None = None) -> None:
            """Rescan the font, rebuild the list, focus FOCUS or the first selected glyph."""
            try:
                self.facts = names_edit.scan(native)
                selected = [
                    n for n in names_selected_names() if n in self.facts.entries
                ]
                self.entries = notes_in_font(self.facts)
                self.subtitle.setText(
                    "Notes travel with the glyph in .vfc and .vfj files. Select a glyph "
                    "in the Font window, or pick one below."
                )
            except ValueError as error:
                self.facts, selected, self.entries = None, [], []
                self.subtitle.setText(str(error))
            self.list_label.setText(f"Glyphs with notes ({len(self.entries)})")
            self.list.setRowCount(len(self.entries))
            for row, (name, text) in enumerate(self.entries):
                for column, value in enumerate((name, first_line(text))):
                    item = QtGui.QTableWidgetItem(value)
                    item.setToolTip(text)
                    self.list.setItem(row, column, item)
            keep = (
                focus
                if self.facts is not None and focus in self.facts.entries
                else None
            )
            self.load(keep or (selected[0] if selected else None))

        def stored(self) -> str:
            """Return the note now stored in the font for the focused glyph."""
            if self.facts is None or self.glyph_name not in self.facts.entries:
                return ""
            return str(self.facts.entries[self.glyph_name].glyph.note or "")

        def load(self, name: str | None) -> None:
            """Show the note of glyph NAME in the editor.

            Keep an unsaved edit: never replace the editor text while it differs
            from the text that was loaded.
            """
            if self.glyph_name and self.editor.toPlainText() != self.loaded:
                self.status.setText("Unsaved note kept. Save it first, then switch.")
                return
            self.glyph_name = name
            self.editor_label.setText(
                f"Note for {name}" if name else "No glyph selected"
            )
            self.editor.setEnabled(bool(name))
            self.loaded = self.stored()
            self.editor.setPlainText(self.loaded)
            self.edited()

        def load_row(self, row: int, select: bool = False) -> None:
            """Load the glyph of list ROW. A double-click also selects it."""
            if 0 <= row < len(self.entries):
                name = self.entries[row][0]
                self.load(name)
                if select and self.facts is not None:
                    select_glyphs([name], package_id=self.facts.package_id)

        def edited(self) -> None:
            """Enable Save only for a changed note on an editable glyph."""
            name = self.glyph_name
            blocked = (
                names_edit.refusal(self.facts, name, OPERATION)
                if self.facts is not None and name
                else ""
            )
            dirty = (
                bool(name)
                and not blocked
                and self.editor.toPlainText() != self.stored()
            )
            self.apply_button.setEnabled(bool(dirty))
            self.status.setText(
                f"Cannot edit {name}: {blocked}"
                if blocked
                else ("Unsaved changes" if dirty else "")
            )

        def apply(self) -> None:
            """Save the note of the focused glyph. One Undo step."""
            name = self.glyph_name
            if self.facts is None or not name:
                raise ValueError("Select a glyph first.")
            text = self.editor.toPlainText()
            changed = save_note(native, QtCore, self.facts.package_id, name, text)
            self.last_result = {"glyph": name, "changed": changed}
            self.loaded = text
            self.reload(focus=name)
            self.status.setText(f"Saved note for {name}" if changed else "No change")

    return GlyphNotes


def main() -> Any:
    """Open or replace the Glyph Notes panel."""
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(_dialog_type(), KEY)


if __name__ == "__main__":
    main()
