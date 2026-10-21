# this_file: Scripts/Names/Suffix Tool.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from the archived Apache-2.0 FontLab samples
# (rescued/samples/names_suffix_tool.py); provenance in NOTICE.
# FLM: Names · Suffix Tool
"""Add, remove or replace a glyph-name suffix (.ss01, .sc, .alt) on the selected glyphs.

WHAT: A non-modal panel offers three operations. Add puts a suffix on each
selected name. Remove strips one suffix (or the last suffix when the field is
empty). Replace swaps one suffix for another. A table previews every new name
and a check result. Apply renames all rows that pass.

HOW: The script rescans the font before the write. A row passes only when the
new name is valid, does not exist, is not the target of another row, and the
glyph is not tied to an auto layer. The write is one Undo step with the App
history order (see commit). The rename and the optional Unicode removal use the
font-owned FontGate record, never flGlyph.fgGlyph. After clearing Unicode the
script reads the list back and compares it with the plan.

WHY: Suffixed alternates are normally unencoded, so the panel can clear their
Unicode in the same step. FontLab would replace an existing glyph that has the
new name, so the script refuses that. FontLab rebuilds auto layers when they
are notified, so the script REFUSES glyphs that have auto layers and glyphs
that are the base of an auto composite. It never calls UpdateAll (fl#8537) and
refuses to write while native updates are pending.
Before it removes Unicode, the script applies the guards of the App Unicode
writer: a regular Font window must be active and no Glyph editor may be open.

USE: Select glyphs in the Font window. Run the script. Choose the operation,
type or pick a suffix (a missing leading dot is added), then press Apply.

BENEFIT: Alternate sets (.ss01, .sc, .case) get consistent names in one
previewed, undoable step.

Credit: archived Apache-2.0 FontLab samples. Native acceptance pending.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

TITLE = "Suffix Tool"
KEY = "names_suffix_tool"
PRESETS = [
    ".ss01",
    ".ss02",
    ".sc",
    ".alt",
    ".case",
    ".sups",
    ".lf",
    ".osf",
    ".tf",
    ".001",
]
RESERVED = frozenset({".notdef", "space"})
VALID_NAME = re.compile(r"^(?![0-9])[A-Za-z0-9_.\-]{1,63}$")
MODES = [
    ("Add suffix", "add"),
    ("Remove suffix", "remove"),
    ("Replace suffix", "replace"),
]


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
def dotted(suffix: str) -> str:
    """Return SUFFIX with one leading dot. An empty suffix stays empty."""
    suffix = suffix.strip()
    return suffix if not suffix or suffix.startswith(".") else "." + suffix


def suffixed(name: str, mode: str, suffix: str, replacement: str = "") -> str:
    """Return the new name for one glyph, or NAME when the operation does not apply.

    Add: append SUFFIX unless NAME already ends with it.
    Remove: drop the last suffix when it equals SUFFIX (any last suffix if SUFFIX is empty).
    Replace: swap the last suffix for REPLACEMENT when it equals SUFFIX.
    The first character is never part of a suffix, so ".notdef" has none.
    """
    suffix, replacement = dotted(suffix), dotted(replacement)
    if mode == "add":
        return name + suffix if suffix and not name.endswith(suffix) else name
    base, dot, last = name[1:].rpartition(".")
    if not dot:
        return name
    stem = name[0] + base
    if mode == "remove":
        return stem if not suffix or "." + last == suffix else name
    return stem + replacement if "." + last == suffix and replacement else name


def plan_renames(
    facts: Facts, pairs: list[tuple[str, str]]
) -> list[tuple[str, str, str]]:
    """Return (old, new, status) for each pair whose name changes.

    Status is "ok" or the first reason the rename is refused, checked in this
    order: reserved glyph (.notdef, space), invalid name, auto-layer link, name
    exists, duplicate target.
    """
    rows = [(old, new) for old, new in pairs if new != old]
    targets: dict[str, int] = {}
    for _, new in rows:
        targets[new] = targets.get(new, 0) + 1
    out = []
    for old, new in rows:
        if old in RESERVED:
            status = "reserved glyph"
        elif not VALID_NAME.match(new):
            status = "invalid name"
        elif reason := refusal(facts, old):
            status = reason
        elif new in facts.entries:
            status = "exists in font"
        elif targets[new] > 1:
            status = "duplicate target"
        else:
            status = "ok"
        out.append((old, new, status))
    return out


def unicode_write_guard(package_id: int) -> None:
    """Apply the App Unicode writer guards before any history call.

    A regular Font window must be active, and no Glyph editor may be open, even
    inactive (the host has a Unicode save-cache gap). These App names are
    internal; a public App helper is proposed.
    """
    from time import monotonic

    from fly import qt
    from fly.ap.duplicate_unicodes_capture import require_no_editors
    from fly.ap.scripting import _require_selection_window

    _require_selection_window(package_id)
    require_no_editors(qt, monotonic() + 2.0)


def unicode_loss(
    facts: Facts, plan: list[tuple[str, str, str]]
) -> dict[str, list[int]]:
    """Return {old name: code points} that a Unicode removal would delete (rows "ok")."""
    return {
        old: [int(c) for c in facts.entries[old].record.unicodes]
        for old, _, status in plan
        if status == "ok"
    }


def hexes(codes: list[int]) -> str:
    """Return codes as "U+0041 U+0042", or an en dash for none."""
    return " ".join(f"U+{c:04X}" for c in codes) or "–"


def apply_suffix(
    native: Any,
    qtcore: Any,
    package_id: int,
    names: list[str],
    mode: str,
    suffix: str,
    replacement: str = "",
    clear_unicode: bool = False,
) -> list[tuple[str, str]]:
    """Rename NAMES by suffix. One Undo step. Return [(old, new)] renamed.

    Rescan first, so a stale preview cannot rename the wrong glyph. When
    CLEAR_UNICODE is true, each renamed glyph also loses its code points.
    Raise ValueError for an empty selection, a switched font or pending updates.
    """
    if not names:
        raise ValueError("Select at least one glyph.")
    facts = fresh_facts(native, package_id)
    pairs = [(n, suffixed(n, mode, suffix, replacement)) for n in names]
    todo = [
        (facts.entries[old], new)
        for old, new, status in plan_renames(facts, pairs)
        if status == "ok"
    ]
    if not todo:
        return []
    if clear_unicode:
        unicode_write_guard(package_id)
    renamed: list[tuple[str, str]] = []

    def mutate(attempted: list[Entry]) -> None:
        for entry, new in todo:
            attempted.append(entry)
            if not facts.package.renameGlyph(entry.record, new, False):
                raise RuntimeError(f"FontLab refused to rename {entry.name} to {new}.")
            renamed.append((entry.name, new))
            if facts.package.findName(new) is None:
                raise RuntimeError(
                    f"After renaming, {new} is missing; check Edit > Undo."
                )
            if clear_unicode:
                entry.record.unicodes = []
                if list(entry.record.unicodes or []):
                    raise RuntimeError(f"Native Unicode of {new} was not cleared.")

    commit(native, qtcore, TITLE, [entry for entry, _ in todo], mutate)
    return renamed


# ------------------------------------------------------------------ panel
def _dialog_type() -> type:
    """Build the panel class lazily. Import Qt and App code only inside FontLab."""
    from fly import ap, qt
    from fly.ap.scripting import names_dialog_type, names_selected_names

    native = ap.fontlab
    QtCore, QtGui = qt.QtCore, qt.QtGui

    def text_of(combo: Any) -> str:
        """Return an editable combo box text (PythonQt exposes it as a property)."""
        value = combo.currentText
        return str(value() if callable(value) else value)

    class SuffixTool(names_dialog_type()):
        """Modeless suffix editor for the selected glyphs."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent, TITLE, KEY)
            self.setMinimumWidth(520)
            self.facts: Facts | None = None
            self.names: list[str] = []
            self.plan: list[tuple[str, str, str]] = []
            form = QtGui.QGridLayout()
            form.setHorizontalSpacing(10)
            form.setVerticalSpacing(8)
            self.mode = QtGui.QComboBox()
            for label, _ in MODES:
                self.mode.addItem(label)
            self.suffix = QtGui.QComboBox()
            self.suffix.setEditable(True)
            self.replacement = QtGui.QComboBox()
            self.replacement.setEditable(True)
            for preset in PRESETS:
                self.suffix.addItem(preset)
                self.replacement.addItem(preset)
            self.replacement_label = QtGui.QLabel("With")
            self.clear_unicode = QtGui.QCheckBox(
                "Also remove Unicode from renamed glyphs (alternates are unencoded)"
            )
            form.addWidget(QtGui.QLabel("Operation"), 0, 0)
            form.addWidget(self.mode, 0, 1, 1, 3)
            form.addWidget(QtGui.QLabel("Suffix"), 1, 0)
            form.addWidget(self.suffix, 1, 1)
            form.addWidget(self.replacement_label, 1, 2)
            form.addWidget(self.replacement, 1, 3)
            form.addWidget(self.clear_unicode, 2, 1, 1, 3)
            form.setColumnStretch(1, 1)
            form.setColumnStretch(3, 1)
            self.root.addLayout(form)
            self.table = self.make_table(
                ["Glyph", "New name", "Check", "Unicode removed"]
            )
            self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
            header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
            self.table.setMinimumHeight(200)
            self.root.addWidget(self.table, 1)
            footer = QtGui.QHBoxLayout()
            self.status = QtGui.QLabel()
            footer.addWidget(self.status, 1)
            self.reload_button = QtGui.QPushButton("Reload selection")
            self.close_button = QtGui.QPushButton("Close")
            self.apply_button = QtGui.QPushButton("Apply")
            self.apply_button.setDefault(True)
            footer.addWidget(self.reload_button)
            footer.addWidget(self.close_button)
            footer.addWidget(self.apply_button)
            self.root.addLayout(footer)
            self._connect(self.mode.currentIndexChanged, lambda *a: self.mode_changed())
            for combo in (self.suffix, self.replacement):
                self._connect(combo.editTextChanged, lambda *a: self.refresh())
            self._connect(self.clear_unicode.toggled, lambda *a: self.refresh())
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

        def mode_key(self) -> str:
            """Return add, remove or replace."""
            return MODES[self.mode.currentIndex][1]

        def mode_changed(self) -> None:
            """Show only the fields that the operation needs."""
            replace = self.mode_key() == "replace"
            self.replacement.setVisible(replace)
            self.replacement_label.setVisible(replace)
            self.clear_unicode.setVisible(self.mode_key() != "remove")
            self.refresh()

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
            self.mode_changed()

        def refresh(self) -> None:
            """Rebuild the preview from the snapshot and the typed suffixes."""
            if self.facts is None:
                self.apply_button.setEnabled(False)
                self.plan = []
                self.table.setRowCount(0)
                return
            count = len(self.names)
            if not count:
                self.subtitle.setText(
                    "Select glyphs in the Font window, then press Reload selection."
                )
            else:
                shown = ", ".join(self.names[:8]) + (" …" if count > 8 else "")
                self.subtitle.setText(
                    f"{count} glyph{'s' if count != 1 else ''}: {shown}. "
                    "Components are expected to follow (native check pending); "
                    "kerning and features keep the old names."
                )
            pairs = [
                (
                    n,
                    suffixed(
                        n,
                        self.mode_key(),
                        text_of(self.suffix),
                        text_of(self.replacement),
                    ),
                )
                for n in self.names
            ]
            self.plan = plan_renames(self.facts, pairs)
            lost = {}
            if self.clear_unicode.isChecked() and self.mode_key() != "remove":
                lost = {
                    old: hexes(codes)
                    for old, codes in unicode_loss(self.facts, self.plan).items()
                }
            accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
            alert = QtGui.QColor("#d33")
            self.table.setRowCount(len(self.plan))
            for row, (old, new, status) in enumerate(self.plan):
                for column, text in enumerate(
                    (old, new, "✓" if status == "ok" else status, lost.get(old, ""))
                ):
                    item = QtGui.QTableWidgetItem(text)
                    if column == 1 and status == "ok":
                        item.setForeground(QtGui.QBrush(accent))
                    if column == 2:
                        item.setForeground(
                            QtGui.QBrush(accent if status == "ok" else alert)
                        )
                    self.table.setItem(row, column, item)
            good = sum(1 for r in self.plan if r[2] == "ok")
            refused = len(self.plan) - good
            self.apply_button.setEnabled(good > 0)
            parts = [f"{good} to rename"]
            if refused:
                parts.append(f"{refused} refused")
            if count - len(self.plan):
                parts.append(f"{count - len(self.plan)} not affected")
            self.status.setText(" · ".join(parts))

        def apply(self) -> None:
            """Rename the passing rows. One Undo step."""
            clear = self.clear_unicode.isChecked() and self.mode_key() != "remove"
            renamed = apply_suffix(
                native,
                QtCore,
                self.facts.package_id if self.facts else -1,
                self.names,
                self.mode_key(),
                text_of(self.suffix),
                text_of(self.replacement),
                clear,
            )
            self.last_result = {"renamed": renamed, "cleared_unicode": clear}
            self.reload()
            self.status.setText(
                f"Renamed {len(renamed)} glyph{'s' if len(renamed) != 1 else ''}"
            )

    return SuffixTool


def main() -> Any:
    """Open or replace the Suffix Tool panel."""
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(_dialog_type(), KEY)


if __name__ == "__main__":
    main()
