# this_file: Scripts/Names/Suffix Tool.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from the archived Apache-2.0 FontLab samples
# Historical source: rescued/samples/names_suffix_tool.py; provenance in NOTICE.
# FLM: Names · Suffix Tool
"""Add, remove or replace a glyph-name suffix (.ss01, .sc, .alt) on the selected
glyphs.

WHAT: A non-modal panel offers three operations. Add puts a suffix on each
selected name. Remove strips one suffix (or the last suffix when the field is
empty). Replace swaps one suffix for another. A table previews every new name
and a check result. Apply renames all rows that pass.

HOW: The script rescans the font before the write. A row passes only when the
new name is valid, does not exist, is not the target of another row, and the
glyph is not tied to an auto layer. The write is one Undo step. The rename and
the optional Unicode removal use the font-owned FontGate record, never
flGlyph.fgGlyph. After clearing Unicode the script reads the list back and
compares it with the plan. The scan, the refusal policy and the one-step write
come from the shared module fly.ap.names_edit. If a write fails part way, every
planned glyph is still notified and stamped, and the message asks you to use
Edit > Undo.

WHY: Suffixed alternates are normally unencoded, so the panel can clear their
Unicode in the same step. FontLab would replace an existing glyph that has the
new name, so the script refuses that. FontLab rebuilds auto layers when they
are notified, so the script REFUSES glyphs that have auto layers and glyphs
that are the base of an auto composite, also through other composites. It never
calls UpdateAll (fl#8537) and discloses queued ids and their possible date
changes. Before it removes Unicode, the script applies the guards of the App
Unicode writer: a regular Font window must be active and no Glyph editor may be
open.

USE: Select glyphs in the Font window. Run the script. Choose the operation,
type or pick a suffix (a missing leading dot is added), then press Apply.

BENEFIT: Alternate sets (.ss01, .sc, .case) get consistent names in one
previewed, undoable step.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. The edit is recorded as one Undo step.
"""

import re
from typing import Any

import fly.ap.names_edit as names_edit  # noqa: PLR0402 - fontlabapp.__getattr__ is native

TITLE = "Suffix Tool"
KEY = "names_suffix_tool"
OPERATION = "rename"  # names_edit refusal policy for this write
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
    facts: names_edit.Facts, pairs: list[tuple[str, str]]
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
        elif reason := names_edit.refusal(facts, old, OPERATION):
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
    inactive (the host has a Unicode save-cache gap). The public App guards
    (fly.ap.edit_guards) do both checks; the editor scan has a 2-second limit.
    """
    import fly.ap.edit_guards as edit_guards  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    edit_guards.require_selection_window(package_id)
    edit_guards.require_no_editors()


def unicode_loss(
    facts: names_edit.Facts, plan: list[tuple[str, str, str]]
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
 *, disclosure: dict[str, Any] | None = None) -> list[tuple[str, str]]:
    """Rename NAMES by suffix. One Undo step. Return [(old, new)] renamed.

    Rescan first, so a stale preview cannot rename the wrong glyph. When
    CLEAR_UNICODE is true, each renamed glyph also loses its code points.
    Raise ValueError for an empty selection, a switched font (queued updates are disclosed).
    """
    if not names:
        raise ValueError("Select at least one glyph.")
    facts = names_edit.fresh_facts(package_id, native=native)
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

    def mutate() -> None:
        for entry, new in todo:
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
            self.facts: names_edit.Facts | None = None
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
                self.facts = names_edit.scan(native)
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
            import fly.ap.edit_guards as result_guards
            disclosure = {"pending_updates": (), "pending_note": ""}
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
            disclosure=disclosure)
            self.last_result = {"renamed": renamed, "cleared_unicode": clear}
            self.last_result.update(disclosure)
            self.reload()
            self.status.setText(
                result_guards.append_note((f"Renamed {len(renamed)} glyph{'s' if len(renamed) != 1 else ''}"), disclosure)
            )

    return SuffixTool


def main() -> Any:
    """Open or replace the Suffix Tool panel."""
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(_dialog_type(), KEY)


if __name__ == "__main__":
    main()
