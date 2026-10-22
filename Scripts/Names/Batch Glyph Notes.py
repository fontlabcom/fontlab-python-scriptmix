# this_file: Scripts/Names/Batch Glyph Notes.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from the archived Apache-2.0 FontLab samples
# Historical source: rescued/samples/utility_batch_glyph_notes.py; provenance in NOTICE.
# FLM: Names · Batch Glyph Notes
"""Set or append one note on every selected glyph at once.

WHAT: A non-modal panel takes a note text and an operation. Set replaces each
glyph note (an empty Set clears the notes). Append adds the text on a new line
after the existing note. A table shows every note before and after. Apply
writes only the glyphs whose note changes.

HOW: The script reads the selection through the shared App selection reader and
scans the whole font. For the write it rescans, plans, and writes as one Undo
step: layers and glyph in one notify list (a glyph alone adds no Undo step).
After the write it reads each note back and compares it with the plan. The
scan, the refusal policy and the one-step write come from the shared module
fly.ap.names_edit. If a write fails part way, every planned glyph is still
notified and stamped, and the message asks you to use Edit > Undo.

WHY: A glyph note belongs to the glyph, not to a master. FontLab rebuilds
all auto layers when an auto layer is notified, and Undo does not restore
them. So the script REFUSES glyphs that own an auto layer, shows the reason in
the table, and never puts an auto layer in the notify list. A base glyph of an
auto composite may get a note (native check pending). The script never reads
flGlyph.fgGlyph (that getter can clear a fresh note mirror on build 9784),
never calls UpdateAll (fl#8537), and discloses queued ids and their possible
date changes.

USE: Select glyphs in the Font window. Run the script. Choose Set or Append,
type the note, check the table, press Apply. Press Reload selection after you
change the selection.

BENEFIT: Review comments or to-do remarks reach many glyphs in one undoable
step, with a preview.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. The edit is recorded as one Undo step.
"""

from typing import Any

import fly.ap.names_edit as names_edit  # noqa: PLR0402 - fontlabapp.__getattr__ is native

TITLE = "Batch Glyph Notes"
KEY = "utility_batch_glyph_notes"
OPERATION = "metadata"  # names_edit refusal policy for this write


# ------------------------------------------------------------------ core
def note_text(existing: str, text: str, append: bool) -> str:
    """Return the new note. Append joins with one newline when both parts have text."""
    if not append:
        return text
    return existing + ("\n" if existing and text else "") + text


def plan_notes(
    facts: names_edit.Facts, names: list[str], text: str, append: bool
) -> list[tuple[str, str, str, str]]:
    """Return (name, old note, new note, status) for each glyph in NAMES.

    Status is "change", "same" or the reason the glyph is refused.
    """
    rows = []
    for name in names:
        if name not in facts.entries:
            rows.append((name, "", "", "not in font"))
            continue
        old = str(facts.entries[name].glyph.note or "")
        if reason := names_edit.refusal(facts, name, OPERATION):
            rows.append((name, old, old, reason))
            continue
        new = note_text(old, text, append)
        rows.append((name, old, new, "change" if new != old else "same"))
    return rows


def apply_notes(
    native: Any, qtcore: Any, package_id: int, names: list[str], text: str, append: bool
, *, disclosure: dict[str, Any] | None = None) -> list[str]:
    """Write the note to NAMES. One Undo step. Return the names changed.

    Refused glyphs are skipped. Raise ValueError for an empty selection, a
    switched font (queued updates are disclosed).
    """
    if not names:
        raise ValueError("Select at least one glyph.")
    facts = names_edit.fresh_facts(package_id, native=native)
    todo = [
        (facts.entries[name], new)
        for name, _, new, status in plan_notes(facts, names, text, append)
        if status == "change"
    ]
    if not todo:
        return []

    def mutate() -> None:
        for entry, new in todo:
            entry.glyph.note = new
            if str(entry.glyph.note or "") != new:
                raise RuntimeError(
                    f"Native note of {entry.name} differs from the plan."
                )

    _done = names_edit.commit(
        TITLE,
        [entry for entry, _ in todo],
        mutate,
        operation=OPERATION,
        facts=facts,
        native=native,
        stamp=qtcore.QDateTime.currentDateTimeUtc(),
    )
    import fly.ap.edit_guards as _guards
    _guards.disclose(_done, disclosure)
    return [entry.name for entry, _ in todo]


# ------------------------------------------------------------------ panel
def _dialog_type() -> type:
    """Build the panel class lazily. Import Qt and App code only inside FontLab."""
    from fly import ap, qt
    from fly.ap.scripting import names_dialog_type, names_selected_names

    native = ap.fontlab
    QtCore, QtGui = qt.QtCore, qt.QtGui

    class BatchGlyphNotes(names_dialog_type()):
        """Modeless note writer for the selected glyphs."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent, TITLE, KEY)
            self.setMinimumWidth(620)
            self.facts: names_edit.Facts | None = None
            self.names: list[str] = []
            self.plan: list[tuple[str, str, str, str]] = []
            form = QtGui.QFormLayout()
            self.mode = QtGui.QComboBox()
            self.mode.addItems(["Set (replace existing notes)", "Append on a new line"])
            self.note_input = QtGui.QPlainTextEdit()
            self.note_input.setMaximumHeight(95)
            form.addRow("Operation", self.mode)
            form.addRow("Note", self.note_input)
            self.root.addLayout(form)
            self.table = self.make_table(["Glyph", "Existing note", "Resulting note"])
            self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            self.table.setFocusPolicy(QtCore.Qt.NoFocus)
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
            header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
            self.table.setMinimumHeight(250)
            self.root.addWidget(self.table, 1)
            footer = QtGui.QHBoxLayout()
            self.status = QtGui.QLabel()
            self.status.setWordWrap(True)
            footer.addWidget(self.status, 1)
            self.reload_button = QtGui.QPushButton("Reload selection")
            self.close_button = QtGui.QPushButton("Close")
            self.apply_button = QtGui.QPushButton("Apply")
            self.apply_button.setDefault(True)
            footer.addWidget(self.reload_button)
            footer.addWidget(self.close_button)
            footer.addWidget(self.apply_button)
            self.root.addLayout(footer)
            self._connect(self.mode.currentIndexChanged, lambda *a: self.refresh())
            self._connect(self.note_input.textChanged, lambda *a: self.refresh())
            self._connect(self.reload_button.clicked, lambda *a: self.reload())
            self._connect(self.apply_button.clicked, lambda *a: self.apply())
            self._connect(self.close_button.clicked, lambda *a: self.close())
            self.reload()

        def invalidate(self) -> None:
            """Also disable Apply when the snapshot is stale."""
            super().invalidate()
            button = getattr(self, "apply_button", None)
            if button is not None:
                button.setEnabled(False)

        def reload(self) -> None:
            """Rescan the font and re-read the selection."""
            try:
                self.facts = names_edit.scan(native)
                self.names = [
                    n for n in names_selected_names() if n in self.facts.entries
                ]
            except ValueError as error:
                self.facts, self.names = None, []
                self.subtitle.setText(str(error))
            self.refresh()

        def refresh(self) -> None:
            """Rebuild the before and after table from the snapshot and the typed note."""
            if self.facts is None:
                self.apply_button.setEnabled(False)
                self.plan = []
                self.table.setRowCount(0)
                return
            self.plan = plan_notes(
                self.facts,
                self.names,
                self.note_input.toPlainText(),
                self.mode.currentIndex == 1,
            )
            self.subtitle.setText(
                "Selected glyphs. A glyph note is shared by all masters. "
                "Set with an empty note clears the notes."
                if self.names
                else "Select glyphs in the Font window, then press Reload selection."
            )
            self.table.setRowCount(len(self.plan))
            for row, (name, old, new, status) in enumerate(self.plan):
                shown = new if status in {"change", "same"} else f"refused: {status}"
                for column, value in enumerate((name, old, shown)):
                    self.table.setItem(
                        row,
                        column,
                        QtGui.QTableWidgetItem(value.replace("\n", "  ⏎  ")),
                    )
            changing = sum(1 for r in self.plan if r[3] == "change")
            refused = sum(1 for r in self.plan if r[3] not in {"change", "same"})
            self.apply_button.setEnabled(changing > 0)
            note = f" · {refused} refused" if refused else ""
            self.status.setText(
                f"{changing} of {len(self.plan)} glyph note"
                f"{'' if len(self.plan) == 1 else 's'} "
                f"change{'s' if len(self.plan) == 1 else ''}{note}"
            )

        def apply(self) -> None:
            """Write the note to the selected glyphs. One Undo step."""
            import fly.ap.edit_guards as result_guards
            disclosure = {"pending_updates": (), "pending_note": ""}
            changed = apply_notes(
                native,
                QtCore,
                self.facts.package_id if self.facts else -1,
                self.names,
                self.note_input.toPlainText(),
                self.mode.currentIndex == 1,
            disclosure=disclosure)
            self.last_result = {"glyphs": len(changed), "changed": changed}
            self.last_result.update(disclosure)
            self.reload()
            self.status.setText(
                result_guards.append_note(("Updated the note on 1 glyph"
                if len(changed) == 1
                else f"Updated notes on {len(changed)} glyphs"), disclosure)
            )

    return BatchGlyphNotes


def main() -> Any:
    """Open or replace the Batch Glyph Notes panel."""
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(_dialog_type(), KEY)


if __name__ == "__main__":
    main()
