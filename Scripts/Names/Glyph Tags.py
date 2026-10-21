# this_file: Scripts/Names/Glyph Tags.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from the archived Apache-2.0 FontLab samples
# (rescued/samples/names_glyph_tags.py); provenance in NOTICE.
# FLM: Names · Glyph Tags
"""Add tags to, or remove tags from, the selected glyphs in one step.

WHAT: A non-modal panel lists each tag used by the selected glyphs and how
many glyphs carry it. Type a tag and press Add, or tick tags and press Remove.
The tag field completes from all tags in the font.

HOW: The script reads the selection through the App helper. It then scans the
whole font once. For each edit it rescans, builds a plan, and writes the plan
as one Undo step with the App history order (see commit). After the write it
reads each tag list back and compares it with the plan.

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

Credit: archived Apache-2.0 FontLab samples. Native acceptance pending.
"""

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

TITLE = "Glyph Tags"
KEY = "names_glyph_tags"
VALID = re.compile(r"^[^\s,]{1,64}$")


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


def font_tags(facts: Facts) -> list[str]:
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
    facts = fresh_facts(native, package_id)
    allowed, _ = editable(facts, names, bases=False)
    plans = []
    for name in allowed:
        glyph = facts.entries[name].glyph
        old = list(glyph.tags or [])
        new = edit_tags(old, list(add), list(remove))
        if new != old:
            plans.append((facts.entries[name], new))
    if not plans:
        return []

    def mutate(attempted: list[Entry]) -> None:
        for entry, new in plans:
            attempted.append(entry)
            entry.glyph.tags = new
            if list(entry.glyph.tags or []) != new:
                raise RuntimeError(f"Native tags of {entry.name} differ from the plan.")

    commit(native, qtcore, TITLE, [entry for entry, _ in plans], mutate)
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
            self.facts: Facts | None = None
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
                self.facts = scan(native)
                names = [n for n in names_selected_names() if n in self.facts.entries]
            except ValueError as error:
                self.facts, names, message = None, [], str(error)
            self.names = names
            if self.facts is not None:
                self.targets, self.refused = editable(self.facts, names, bases=False)
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
