# this_file: Scripts/Features/Classes Browser.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Features · Classes Browser
"""Browse feature classes and their members. Filter by class name or glyph; font-wide across masters.

What it does:
    Run with a font active. All original controls use the shared fly panel lifecycle.
    Feature data is font-wide; reopen after switching fonts or changing source.

How it works:
    Read feature-class records, exclude kerning-only classes and strip the
    native key-member marker. Filter the captured class names and member text.

Why this design:
    Feature classes and kerning classes serve different tasks; this view keeps
    the feature membership explicit.

How to use:
    Run Features > Classes Browser with a font open. Type a class or member
    filter, choose a row and copy the displayed class declaration when needed.

Benefit:
    Check which glyphs belong to a feature class without editing membership or
    feature source.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    features_dialog_type,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = (qt.QtCore, qt.QtGui)
FeaturesDialog = features_dialog_type()
TITLE = "OpenType Class Browser"
KEY = "features_classes_browser"
SUBTITLE = "Browse feature classes and their members. Filter by class name or glyph; font-wide across masters."
ACTION = "Copy class"


def run(groups: Any) -> list[tuple[str, int, str]]:
    """Return sorted (class name, member count, space-separated members) rows.

    groups is a native fontgate group collection exposing items(), each group's
    isFeaGroup(), and getAsClassRecords(). Exclude kerning-only classes using
    isFeaGroup and remove the native trailing apostrophe key-member marker.
    This browses font-wide membership without parsing or editing feature code.
    """
    modes = {str(name): group.isFeaGroup() for name, group in groups.items()}
    rows = []
    for record in groups.getAsClassRecords() or []:
        name, _, body = str(record).partition(":")
        if modes.get(name):
            members = [part.rstrip("'") for part in body.split()]
            rows.append((name, len(members), " ".join(members)))
    return sorted(rows)


class Dialog(FeaturesDialog):
    def __init__(self, parent: Any = None) -> None:
        """Initialize this owned tool and preserve its original controls."""
        super().__init__(parent, title=TITLE, subtitle=SUBTITLE, key=KEY)

    def setup(self) -> None:
        """Build the original controls inside the shared owned panel."""
        root = self.prepare()
        self.apply_button.setText(ACTION)
        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText("Filter class names or members…")
        root.addWidget(self.search)
        self.table = self.make_table(["Class", "Members", "Glyph names"])
        root.addWidget(self.table, 1)
        self.members = QtGui.QPlainTextEdit()
        self.members.setReadOnly(True)
        root.addWidget(self.members, 1)
        self.all_rows = run(self.font_data.groups) if self.font_data else []
        self._connect(self.search.textChanged, lambda *a: self.refresh())
        self._connect(self.table.itemSelectionChanged, lambda *a: self.preview())

    def refresh(self) -> None:
        """Rebuild the complete visible preview; invalidate it on failure."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self.package is not None:
            self.ensure_font()
        needle = self.search.text.lower()
        self.fill(
            [row for row in self.all_rows if needle in (row[0] + " " + row[2]).lower()]
        )
        if self.rows:
            self.table.selectRow(0)
        self.preview()
        self.status.setText(f"{len(self.rows)} of {len(self.all_rows)} feature classes")
        self._preview_valid = True

    def preview(self) -> None:
        """Display the currently selected row and its usable feature snippet."""
        row = self.table.currentRow()
        self.snippet = ""
        if 0 <= row < len(self.rows):
            name, _, members = self.rows[row]
            self.snippet = "@" + name.lstrip("@") + " = [" + members + "];"
        self.members.setPlainText(self.snippet or "No matching feature classes.")
        self.apply_button.setEnabled(bool(self.snippet))

    def apply(self) -> None:
        """Perform the selected original tool action on its valid preview."""
        self.ensure_preview()
        if self.snippet:
            self.copy_text(self.snippet)


def main() -> Any:
    """Replace this tool through the shared owned-window registry."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
