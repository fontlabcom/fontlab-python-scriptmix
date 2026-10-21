# this_file: Scripts/Names/Batch Glyph Notes.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from the archived Apache-2.0 FontLab samples
# (rescued/samples/utility_batch_glyph_notes.py); provenance in NOTICE.
# FLM: Names · Batch Glyph Notes
"""Set or append one note on every selected glyph at once.

WHAT: A non-modal panel takes a note text and an operation. Set replaces each
glyph note (an empty Set clears the notes). Append adds the text on a new line
after the existing note. A table shows every note before and after. Apply
writes only the glyphs whose note changes.

HOW: The script reads the selection through the App helper and scans the whole
font. For the write it rescans, plans, and writes as one Undo step with the App
history order: layers and glyph in one notify list (a glyph alone adds no Undo
step). After the write it reads each note back and compares it with the plan.

WHY: A glyph note belongs to the glyph, not to a master. FontLab rebuilds
all auto layers when an auto layer is notified, and Undo does not restore
them. So the script REFUSES glyphs that own an auto layer, shows the reason in
the table, and never puts an auto layer in the notify list. A base glyph of an
auto composite may get a note (native check pending). The script never reads
flGlyph.fgGlyph (that getter can clear a fresh note mirror on build 9784),
never calls UpdateAll (fl#8537), and refuses to write while native updates are
pending.

USE: Select glyphs in the Font window. Run the script. Choose Set or Append,
type the note, check the table, press Apply. Press Reload selection after you
change the selection.

BENEFIT: Review comments or to-do remarks reach many glyphs in one undoable
step, with a preview.

Credit: archived Apache-2.0 FontLab samples. Native acceptance pending.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

TITLE = "Batch Glyph Notes"
KEY = "utility_batch_glyph_notes"


# ------------------------------------------------------------------ shared
# This block is identical in all seven Names editors. Reason: each menu script
# stays one file. A shared App helper could replace it later.
@dataclass(frozen=True)
class Entry:
    """One glyph. RECORD is the FontGate glyph (rename, Unicode). GLYPH is the FontLab glyph."""

    name: str
    record: Any
    glyph: Any


@dataclass(frozen=True)
class Facts:
    """Whole-font snapshot. Never patched: a stale snapshot is rescanned."""

    package: Any
    package_id: int
    entries: dict[str, Entry]
    autos: frozenset[str]
    bases: dict[str, tuple[str, ...]]


def scan(native: Any) -> Facts:
    """Read every glyph and every auto-layer dependency of the current font.

    Use font-owned records and package.findFgId. Never read flGlyph.fgGlyph:
    on build 9784 that getter can clear a fresh note mirror.
    """
    package = native.flWorkspace.instance().currentPackage
    font = native.CurrentFont()
    if package is None or package.isNull or font is None:
        raise ValueError("Open a font first.")
    entries: dict[str, Entry] = {}
    autos: set[str] = set()
    users: dict[str, set[str]] = {}
    for record in font.glyphs:
        glyph = package.findFgId(int(record.id))
        if (
            glyph is None
            or glyph.isNull
            or glyph.name != record.name
            or int(glyph.fgGlyphId) != int(record.id)
        ):
            raise ValueError("Native glyph mapping is inconsistent; reload the font.")
        entries[str(record.name)] = Entry(str(record.name), record, glyph)
        for layer in glyph.layers:
            if not layer.autoLayer:
                continue
            autos.add(str(record.name))
            for shape in layer.shapes:
                if shape.isComponent:
                    base = str(shape.shapeData.componentGlyph)
                    users.setdefault(base, set()).add(str(record.name))
    bases = {base: tuple(sorted(names)) for base, names in users.items()}
    return Facts(package, int(package.id), entries, frozenset(autos), bases)


def refusal(facts: Facts, name: str, *, bases: bool = True) -> str:
    """Return why NAME must not be edited, or "" when it may be.

    FontLab rebuilds every auto layer when an auto layer or the base of an
    auto composite is notified, and Undo does not restore the result.
    Glyphs that own an auto layer are always refused. With BASES false, a base
    of an auto composite is allowed: use that for metadata (tags, marks, notes)
    that does not reach the composites. Renames and Unicode keep BASES true.
    """
    entry = facts.entries.get(name)
    if entry is None:
        return "not in font"
    if not tuple(entry.glyph.layers):
        return "has no layers"
    if name in facts.autos:
        return "has auto layers"
    users = facts.bases.get(name)
    if bases and users:
        return "base of auto " + ", ".join(users[:2]) + ("…" if len(users) > 2 else "")
    return ""


def editable(
    facts: Facts, names: list[str], *, bases: bool = True
) -> tuple[list[str], dict[str, str]]:
    """Split NAMES into (names that may be edited, {refused name: reason})."""
    refused = {n: r for n in names if (r := refusal(facts, n, bases=bases))}
    return [n for n in names if n not in refused], refused


def fresh_facts(native: Any, package_id: int) -> Facts:
    """Rescan just before a write. Refuse a switched font or pending host updates."""
    facts = scan(native)
    if facts.package_id != package_id:
        raise ValueError("The scanned font is no longer current; reload.")
    if tuple(native.flGlyph.updatedFgGlyphs()):
        raise ValueError(
            "Native glyph updates are pending; finish the current edit first."
        )
    return facts


def commit(
    native: Any,
    qtcore: Any,
    title: str,
    entries: list[Entry],
    mutate: Callable[[list[Entry]], Any],
) -> Any:
    """Run MUTATE as one Undo step, in the order the App writers use.

    1. checkInitHistoryState(0) on every layer and glyph, before any change.
    2. MUTATE(attempted). It appends each entry to ATTEMPTED before it changes it.
    3. One notifyChangesApplied([layers..., glyphs...]) for ATTEMPTED entries only.
    4. Same UTC lastModified stamp on every attempted glyph, before and after the notify.
    Finalise even when MUTATE fails, so a partial edit stays on the Undo stack.
    Glyphs that MUTATE never reached get no stamp and no notify.
    """
    stamp = qtcore.QDateTime.currentDateTimeUtc()
    work = {id(e): (e.glyph, tuple(e.glyph.layers)) for e in entries}
    for glyph, layers in work.values():
        for item in (*layers, glyph):
            item.checkInitHistoryState(0)
    errors: list[Exception] = []
    attempted: list[Entry] = []
    result = None
    try:
        result = mutate(attempted)
    except Exception as error:  # noqa: BLE001 - finalise history first
        errors.append(error)
    done = [work[id(e)] for e in attempted]
    if done:
        objects = [layer for _, layers in done for layer in layers]
        objects += [glyph for glyph, _ in done]
        try:
            for glyph, _ in done:
                glyph.lastModified = stamp
            native.flItems().notifyChangesApplied(title, objects)
        except Exception as error:  # noqa: BLE001 - never report a failed notify
            errors.append(error)
        finally:
            for glyph, _ in done:
                try:
                    glyph.lastModified = stamp
                except Exception as error:  # noqa: BLE001 - keep every observer error
                    errors.append(error)
    if errors:
        raise RuntimeError(
            f"{title} did not finish cleanly ({errors[0]!r}); check Edit > Undo."
        ) from errors[0]
    return result


# ------------------------------------------------------------------ core
def note_text(existing: str, text: str, append: bool) -> str:
    """Return the new note. Append joins with one newline when both parts have text."""
    if not append:
        return text
    return existing + ("\n" if existing and text else "") + text


def plan_notes(
    facts: Facts, names: list[str], text: str, append: bool
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
        if reason := refusal(facts, name, bases=False):
            rows.append((name, old, old, reason))
            continue
        new = note_text(old, text, append)
        rows.append((name, old, new, "change" if new != old else "same"))
    return rows


def apply_notes(
    native: Any, qtcore: Any, package_id: int, names: list[str], text: str, append: bool
) -> list[str]:
    """Write the note to NAMES. One Undo step. Return the names changed.

    Refused glyphs are skipped. Raise ValueError for an empty selection, a
    switched font or pending host updates.
    """
    if not names:
        raise ValueError("Select at least one glyph.")
    facts = fresh_facts(native, package_id)
    todo = [
        (facts.entries[name], new)
        for name, _, new, status in plan_notes(facts, names, text, append)
        if status == "change"
    ]
    if not todo:
        return []

    def mutate(attempted: list[Entry]) -> None:
        for entry, new in todo:
            attempted.append(entry)
            entry.glyph.note = new
            if str(entry.glyph.note or "") != new:
                raise RuntimeError(
                    f"Native note of {entry.name} differs from the plan."
                )

    commit(native, qtcore, TITLE, [entry for entry, _ in todo], mutate)
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
            self.facts: Facts | None = None
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
                self.facts = scan(native)
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
            changed = apply_notes(
                native,
                QtCore,
                self.facts.package_id if self.facts else -1,
                self.names,
                self.note_input.toPlainText(),
                self.mode.currentIndex == 1,
            )
            self.last_result = {"glyphs": len(changed), "changed": changed}
            self.reload()
            self.status.setText(
                "Updated the note on 1 glyph"
                if len(changed) == 1
                else f"Updated notes on {len(changed)} glyphs"
            )

    return BatchGlyphNotes


def main() -> Any:
    """Open or replace the Batch Glyph Notes panel."""
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(_dialog_type(), KEY)


if __name__ == "__main__":
    main()
