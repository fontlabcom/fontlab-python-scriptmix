# this_file: Scripts/Names/Glyph Tags.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from the archived Apache-2.0 FontLab samples
# Historical source: rescued/samples/names_glyph_tags.py; provenance in NOTICE.
# FLM: Names · Glyph Tags
"""Add tags to, or remove tags from, the selected glyphs in one step.

WHAT: A non-modal panel lists each tag used by the selected glyphs and how
many glyphs carry it. Type a tag and press Add, or tick tags and press Remove.
The tag field completes from all tags in the font.

HOW: The script reads the selection through the shared App selection reader. It
then scans the whole font once. For each edit it rescans, builds a plan, and
writes the plan as one Undo step. After the write it reads each tag list back
and compares it with the plan. The scan, the refusal policy and the one-step
write come from the shared module fly.ap.names_edit. If a write fails part way,
every planned glyph is still notified and stamped, and the message asks you to
use Edit > Undo.

WHY: FontLab rebuilds all auto layers when an auto layer is notified. Undo
does not restore the rebuilt layers. So the script REFUSES glyphs that own an
auto layer and never puts an auto layer in the notify list. A base glyph of
an auto composite may be tagged: its tags do not reach the composites (native
check pending). The script never reads flGlyph.fgGlyph (that getter can clear
a fresh glyph note on build 9784). It never calls UpdateAll (that feeds the
fl#8537 pending-update queue). It refuses to write when native updates are
pending.

USE: Select glyphs in the Font window. Run the script. Press Reload selection
after you change the selection. A tag has 1 to 64 characters, no spaces and
no commas.

BENEFIT: Review states, spacing status and similar marks stay on the glyphs
and travel with the font. One Edit > Undo reverts one Add or Remove.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. Native acceptance pending.
"""

import re
from collections.abc import Sequence
from typing import Any

import fly.ap.names_edit as names_edit  # noqa: PLR0402 - fontlabapp.__getattr__ is native

TITLE = "Glyph Tags"
KEY = "names_glyph_tags"
OPERATION = "metadata"  # names_edit refusal policy for this write
VALID = re.compile(r"^[^\s,]{1,64}$")


# ------------------------------------------------------------------ core
def valid_tag(tag: str) -> bool:
    """Return True for 1 to 64 characters without whitespace or commas."""
    return VALID.match(tag) is not None


def tag_counts(tag_lists: list[list[str]]) -> list[tuple[str, int]]:
    """Return (tag, count), most used first, then alphabetical."""
    counts: dict[str, int] = {}
    for tags in tag_lists:
        for tag in tags:
            counts[tag] = counts.get(tag, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def edit_tags(old: list[str], add: list[str], remove: list[str]) -> list[str]:
    """Remove first. Then append each new tag once, in the order given.

    Surviving old tags keep their order. A tag that is already present is not
    added again.
    """
    new = [tag for tag in old if tag not in remove]
    for tag in add:
        if tag not in new:
            new.append(tag)
    return new


def font_tags(facts: names_edit.Facts) -> list[str]:
    """Return every tag used in the font, sorted."""
    found: set[str] = set()
    for entry in facts.entries.values():
        found.update(entry.glyph.tags or [])
    return sorted(found)


def apply_tags(
    native: Any,
    qtcore: Any,
    package_id: int,
    names: list[str],
    add: Sequence[str] = (),
    remove: Sequence[str] = (),
) -> list[str]:
    """Add and remove tags on NAMES. One Undo step. Return the names changed.

    Refused glyphs (those that own an auto layer) are skipped. Raise ValueError for
    an empty selection, a bad tag, a switched font or pending host updates.
    """
    if not names:
        raise ValueError("Select at least one glyph.")
    bad = [tag for tag in add if not valid_tag(tag)]
    if bad:
        raise ValueError(
            f"Invalid tag {bad[0]!r}: use 1 to 64 characters, no spaces or commas."
        )
    facts = names_edit.fresh_facts(package_id, native=native)
    allowed, _ = names_edit.editable(facts, names, OPERATION)
    plans = []
    for name in allowed:
        glyph = facts.entries[name].glyph
        old = list(glyph.tags or [])
        new = edit_tags(old, list(add), list(remove))
        if new != old:
            plans.append((facts.entries[name], new))
    if not plans:
        return []

    def mutate() -> None:
        for entry, new in plans:
            entry.glyph.tags = new
            if list(entry.glyph.tags or []) != new:
                raise RuntimeError(f"Native tags of {entry.name} differ from the plan.")

    names_edit.commit(
        TITLE,
        [entry for entry, _ in plans],
        mutate,
        operation=OPERATION,
        facts=facts,
        native=native,
        stamp=qtcore.QDateTime.currentDateTimeUtc(),
    )
    return [entry.name for entry, _ in plans]


# ------------------------------------------------------------------ panel
def _dialog_type() -> type:
    """Build the panel class lazily. Import Qt and App code only inside FontLab."""
    from fly import ap, qt
    from fly.ap.scripting import names_dialog_type, names_selected_names

    native = ap.fontlab
    QtCore, QtGui = qt.QtCore, qt.QtGui

    class GlyphTags(names_dialog_type()):
        """Modeless tag editor for the selected glyphs."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent, TITLE, KEY)
            self.resize(620, 460)
            self.setMinimumWidth(600)
            self.facts: names_edit.Facts | None = None
            self.names: list[str] = []
            self.targets: list[str] = []
            self.refused: dict[str, str] = {}
            self.counts: list[tuple[str, int]] = []
            row = QtGui.QHBoxLayout()
            row.setSpacing(8)
            self.tag = QtGui.QLineEdit()
            self.tag.setPlaceholderText("tag, e.g. review, spacing, done")
            self.completer_model = QtGui.QStringListModel()
            self.completer = QtGui.QCompleter()
            self.completer.setModel(self.completer_model)
            self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            self.tag.setCompleter(self.completer)
            self.add_button = QtGui.QPushButton("Add to selection")
            row.addWidget(QtGui.QLabel("Tag"))
            row.addWidget(self.tag, 1)
            row.addWidget(self.add_button)
            self.root.addLayout(row)
            self.table = self.make_table(["Tag (tick to remove)", "Selected glyphs"])
            self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
            header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
            self.root.addWidget(self.table, 1)
            footer = QtGui.QHBoxLayout()
            self.status = QtGui.QLabel()
            self.status.setWordWrap(True)
            footer.addWidget(self.status, 1)
            self.reload_button = QtGui.QPushButton("Reload selection")
            self.close_button = QtGui.QPushButton("Close")
            self.remove_button = QtGui.QPushButton("Remove ticked")
            footer.addWidget(self.reload_button)
            footer.addWidget(self.close_button)
            footer.addWidget(self.remove_button)
            self.root.addLayout(footer)
            self._connect(self.tag.textChanged, lambda *a: self.update_buttons())
            self._connect(self.tag.returnPressed, lambda *a: self.add_tag())
            self._connect(self.add_button.clicked, lambda *a: self.add_tag())
            self._connect(self.remove_button.clicked, lambda *a: self.remove_ticked())
            self._connect(self.table.itemChanged, lambda *a: self.update_buttons())
            self._connect(self.reload_button.clicked, lambda *a: self.reload())
            self._connect(self.close_button.clicked, lambda *a: self.close())
            self.reload()

        def invalidate(self) -> None:
            """Also disable both edit buttons when the snapshot is stale."""
            super().invalidate()
            for name in ("add_button", "remove_button"):
                button = getattr(self, name, None)
                if button is not None:
                    button.setEnabled(False)

        def reload(self) -> None:
            """Rescan the font and re-read the selection."""
            message = ""
            try:
                self.facts = names_edit.scan(native)
                names = [n for n in names_selected_names() if n in self.facts.entries]
            except ValueError as error:
                self.facts, names, message = None, [], str(error)
            self.names = names
            if self.facts is not None:
                self.targets, self.refused = names_edit.editable(
                    self.facts, names, OPERATION
                )
                self.completer_model.setStringList(font_tags(self.facts))
            else:
                self.targets, self.refused = [], {}
            self.refresh(message)

        def refresh(self, message: str = "") -> None:
            """Redraw the tag table and the buttons from the snapshot."""
            count = len(self.targets)
            if self.facts is None:
                self.subtitle.setText(message or "Open a font first.")
            elif not self.names:
                self.subtitle.setText(
                    "Select glyphs in the Font window, then press Reload selection."
                )
            else:
                shown = ", ".join(self.targets[:8]) + (" …" if count > 8 else "")
                self.subtitle.setText(
                    f"{count} glyph{'s' if count != 1 else ''}: {shown}"
                )
            self.counts = tag_counts(
                [list(self.facts.entries[n].glyph.tags or []) for n in self.targets]
                if self.facts is not None
                else []
            )
            accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
            self.table.blockSignals(True)
            self.table.setRowCount(len(self.counts))
            for row, (tag, used) in enumerate(self.counts):
                item = QtGui.QTableWidgetItem(tag)
                item.setFlags(
                    int(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                )
                item.setCheckState(QtCore.Qt.Unchecked)
                share = QtGui.QTableWidgetItem(f"{used} of {count}")
                share.setTextAlignment(
                    int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                )
                if used == count:
                    share.setForeground(QtGui.QBrush(accent))
                self.table.setItem(row, 0, item)
                self.table.setItem(row, 1, share)
            self.table.blockSignals(False)
            self.update_buttons()
            text = f"{len(self.counts)} tag{'s' if len(self.counts) != 1 else ''} in the selection"
            if self.refused:
                first = next(iter(self.refused.items()))
                text += f" · {len(self.refused)} refused ({first[0]}: {first[1]})"
            self.status.setText(text)

        def ticked(self) -> list[str]:
            """Return the tags whose row is ticked."""
            return [
                self.counts[row][0]
                for row in range(self.table.rowCount)
                if self.table.item(row, 0).checkState() == QtCore.Qt.Checked
            ]

        def update_buttons(self) -> None:
            """Enable Add for a valid tag and Remove for ticked tags."""
            self.add_button.setEnabled(
                bool(self.targets) and valid_tag(self.tag.text.strip())
            )
            self.remove_button.setEnabled(bool(self.targets) and bool(self.ticked()))

        def _write(self, add: list[str], remove: list[str], message: str) -> None:
            """Write one plan. Reload from the font afterwards. Show MESSAGE."""
            changed = apply_tags(
                native,
                QtCore,
                self.facts.package_id if self.facts else -1,
                self.targets,
                add,
                remove,
            )
            self.last_result = {"added": add, "removed": remove, "changed": changed}
            self.reload()
            noun = "glyph" if len(changed) == 1 else "glyphs"
            self.status.setText(f"{message} on {len(changed)} {noun}")

        def add_tag(self) -> None:
            """Add the typed tag to the selected glyphs."""
            tag = self.tag.text.strip()
            self._write([tag], [], f"Added '{tag}'")
            self.tag.clear()

        def remove_ticked(self) -> None:
            """Remove the ticked tags from the selected glyphs."""
            tags = self.ticked()
            self._write([], tags, "Removed " + ", ".join(tags))

    return GlyphTags


def main() -> Any:
    """Open or replace the Glyph Tags panel."""
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(_dialog_type(), KEY)


if __name__ == "__main__":
    main()
