# this_file: Scripts/Names/Batch Rename.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from the archived Apache-2.0 FontLab samples
# Historical source: rescued/samples/names_batch_rename.py; provenance in NOTICE.
# FLM: Names · Batch Rename
"""Find and replace in glyph names, with a live preview and strict checks.

WHAT: A non-modal panel takes a Find text (plain or regular expression) and a
Replace text. It lists every glyph whose name would change, with the new name
and a check result. Rename applies all rows that pass.

HOW: The script scans the font on open and on Reload, and again before the
write. A row passes only when the new name is valid, does not exist, is not the
target of another row, and the glyph is not tied to an auto layer. The write is
one Undo step. The rename uses the font-owned FontGate record, never
flGlyph.fgGlyph. The scan, the refusal policy and the one-step write come from
the shared module fly.ap.names_edit. If a write fails part way, every planned
glyph is still notified and stamped, and the message asks you to use Edit >
Undo.

WHY: FontLab would replace an existing glyph that has the new name, so the
script refuses that. FontLab rebuilds auto layers when they are notified (it
turned ecircumflex into a lone "ee" after e was renamed). So the script REFUSES
glyphs that have auto layers and glyphs that are the base of an auto composite,
also through other composites. It never calls UpdateAll (fl#8537) and refuses
to write while native updates are pending. Kerning and features keep the old
names.

USE: Select glyphs in the Font window. Run the script. Type Find and Replace.
Use \\1 for groups in regular-expression mode. Press Rename. Choose "All
glyphs" to rename across the font.

BENEFIT: Bulk renames (for example uniXXXX to AGL names) are safe, previewed
and reversible with one Edit > Undo.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. Native acceptance pending.
"""

import re
from typing import Any

import fly.ap.names_edit as names_edit  # noqa: PLR0402 - fontlabapp.__getattr__ is native

TITLE = "Batch Rename"
KEY = "names_batch_rename"
OPERATION = "rename"  # names_edit refusal policy for this write
RESERVED = frozenset({".notdef", "space"})
VALID_NAME = re.compile(r"^(?![0-9])[A-Za-z0-9_.\-]{1,63}$")


# ------------------------------------------------------------------ core
def replaced(name: str, find: str, replace: str, regex: bool) -> str:
    """Return NAME after one find and replace. Raise re.error for a bad pattern."""
    if not find:
        return name
    return re.sub(find, replace, name) if regex else name.replace(find, replace)


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


def apply_renames(
    native: Any, qtcore: Any, package_id: int, pairs: list[tuple[str, str]]
) -> list[tuple[str, str]]:
    """Rename every pair that passes the checks. One Undo step. Return [(old, new)].

    Rescan first, so a stale preview cannot rename the wrong glyph. Raise
    ValueError for a switched font or pending host updates.
    """
    facts = names_edit.fresh_facts(package_id, native=native)
    todo = [
        (facts.entries[old], new)
        for old, new, status in plan_renames(facts, pairs)
        if status == "ok"
    ]
    if not todo:
        return []
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

    names_edit.commit(
        TITLE,
        [entry for entry, _ in todo],
        mutate,
        operation=OPERATION,
        facts=facts,
        native=native,
        stamp=qtcore.QDateTime.currentDateTimeUtc(),
    )
    return renamed


# ------------------------------------------------------------------ panel
def _dialog_type() -> type:
    """Build the panel class lazily. Import Qt and App code only inside FontLab."""
    from fly import ap, qt
    from fly.ap.scripting import names_dialog_type, names_selected_names

    native = ap.fontlab
    QtCore, QtGui = qt.QtCore, qt.QtGui

    class BatchRename(names_dialog_type()):
        """Modeless find-and-replace renamer with a live preview."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent, TITLE, KEY)
            self.setMinimumWidth(540)
            self.facts: names_edit.Facts | None = None
            self.names: list[str] = []
            self.plan: list[tuple[str, str, str]] = []
            form = QtGui.QGridLayout()
            form.setHorizontalSpacing(10)
            form.setVerticalSpacing(8)
            self.find = QtGui.QLineEdit()
            self.find.setPlaceholderText("text or pattern, e.g. ^uni or \\.alt$")
            self.replace = QtGui.QLineEdit()
            self.replace.setPlaceholderText("replacement, groups as \\1")
            self.regex = QtGui.QCheckBox("Regular expression")
            self.scope = QtGui.QComboBox()
            self.scope.addItem("Selected glyphs (0)")
            self.scope.addItem("All glyphs in the font")
            form.addWidget(QtGui.QLabel("Find"), 0, 0)
            form.addWidget(self.find, 0, 1)
            form.addWidget(QtGui.QLabel("Replace"), 1, 0)
            form.addWidget(self.replace, 1, 1)
            form.addWidget(QtGui.QLabel("Glyphs"), 2, 0)
            form.addWidget(self.scope, 2, 1)
            form.addWidget(self.regex, 3, 1)
            form.setColumnStretch(1, 1)
            self.root.addLayout(form)
            self.table = self.make_table(["Glyph", "New name", "Check"])
            self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
            header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
            self.table.setMinimumHeight(220)
            self.root.addWidget(self.table, 1)
            footer = QtGui.QHBoxLayout()
            self.status = QtGui.QLabel()
            footer.addWidget(self.status, 1)
            self.reload_button = QtGui.QPushButton("Reload selection")
            self.close_button = QtGui.QPushButton("Close")
            self.apply_button = QtGui.QPushButton("Rename")
            self.apply_button.setDefault(True)
            footer.addWidget(self.reload_button)
            footer.addWidget(self.close_button)
            footer.addWidget(self.apply_button)
            self.root.addLayout(footer)
            for line in (self.find, self.replace):
                self._connect(line.textChanged, lambda *a: self.refresh())
            self._connect(self.regex.toggled, lambda *a: self.refresh())
            self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
            self._connect(self.reload_button.clicked, lambda *a: self.reload())
            self._connect(self.apply_button.clicked, lambda *a: self.apply())
            self._connect(self.close_button.clicked, lambda *a: self.close())
            self.reload()

        def invalidate(self) -> None:
            """Also disable Rename when the snapshot is stale."""
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
            self.scope.setItemText(0, f"Selected glyphs ({len(self.names)})")
            if not self.names:
                self.scope.setCurrentIndex(1)
            self.refresh()

        def refresh(self) -> None:
            """Rebuild the preview from the snapshot and the typed texts."""
            if self.facts is None:
                self.apply_button.setEnabled(False)
                self.plan = []
                self.table.setRowCount(0)
                return
            self.subtitle.setText(
                "Renames the glyphs. Components that use them are expected to follow "
                "(native check pending). Kerning and features keep the old names. "
                "Glyphs tied to auto layers are refused."
            )
            names = (
                self.names if self.scope.currentIndex == 0 else list(self.facts.entries)
            )
            error = ""
            try:
                pairs = [
                    (
                        n,
                        replaced(
                            n, self.find.text, self.replace.text, self.regex.isChecked()
                        ),
                    )
                    for n in names
                ]
            except re.error as exc:
                pairs, error = [], f"Pattern error: {exc}"
            self.plan = plan_renames(self.facts, pairs)
            accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
            alert = QtGui.QColor("#d33")
            self.table.setRowCount(len(self.plan))
            for row, (old, new, status) in enumerate(self.plan):
                for column, text in enumerate(
                    (old, new, "✓" if status == "ok" else status)
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
            if error:
                self.status.setText(error)
            elif not self.find.text:
                self.status.setText("Type the text to find.")
            else:
                note = f" · {refused} refused" if refused else ""
                self.status.setText(
                    f"{good} glyph{'s' if good != 1 else ''} to rename{note}"
                )

        def apply(self) -> None:
            """Rename the passing rows. One Undo step."""
            pairs = [(old, new) for old, new, _ in self.plan]
            renamed = apply_renames(
                native, QtCore, self.facts.package_id if self.facts else -1, pairs
            )
            self.last_result = {"renamed": renamed}
            self.reload()
            self.status.setText(
                f"Renamed {len(renamed)} glyph{'s' if len(renamed) != 1 else ''}"
            )

    return BatchRename


def main() -> Any:
    """Open or replace the Batch Rename panel."""
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(_dialog_type(), KEY)


if __name__ == "__main__":
    main()
