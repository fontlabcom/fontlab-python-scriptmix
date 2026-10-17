# this_file: Scripts/Names/Glyph Finder.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from Apache-2.0 FontLab samples; provenance in migration.json.
# FLM: Names · Glyph Finder
"""Type to find glyphs by name, character or code point; Enter selects them in the Font window.

Accepts a name fragment (acute), a wildcard pattern (*.ss0?), a character
(é), or a code point (U+00E9, 0x1E82, uni00E9). The list updates as you
type; double-click a row to select just that glyph. Nothing in the font
changes.
"""

import fnmatch
import re
from collections.abc import Callable
from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    names_dialog_type,
    names_font_glyphs,
    names_muted,
    names_snapshot_refresh,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Glyph Finder"
KEY = "names_glyph_finder"
MAX_ROWS = 3000
CODE = re.compile(r"^(?:U\+|u\+|0x|0X|uni|u)([0-9A-Fa-f]{4,6})$")


# ---------------------------------------------------------------- font access
def font_glyphs() -> list[tuple[str, list[int]]]:
    """Read current font state through the shared Names access helper."""
    return names_font_glyphs()


# ---------------------------------------------------------------- core
def matcher(query: str) -> tuple[str, Callable[[str, list[int]], bool]]:
    """(kind, test(name, codes) -> bool) for a query string."""
    query = query.strip()
    code = CODE.match(query)
    if code:
        value = int(code.group(1), 16)
        return "code point", lambda name, codes: value in codes
    if (len(query) == 1 and not query.isalnum()) or (
        len(query) == 1 and ord(query) > 127
    ):
        value = ord(query)
        return "character", lambda name, codes: value in codes
    if any(c in query for c in "*?["):
        return "pattern", lambda name, codes: fnmatch.fnmatchcase(name, query)
    lowered = query.lower()
    if len(query) == 1:
        value = ord(query)
        return (
            "name or character",
            lambda name, codes: value in codes or lowered in name.lower(),
        )
    return "name", lambda name, codes: lowered in name.lower()


def find(
    glyphs: list[tuple[str, list[int]]], query: str
) -> tuple[str, list[tuple[str, list[int]]]]:
    """(kind, [(name, codes)]) matching the query; everything for an empty query."""
    if not query.strip():
        return "all", list(glyphs)
    kind, test = matcher(query)
    return kind, [(name, codes) for name, codes in glyphs if test(name, codes)]


# ---------------------------------------------------------------- GUI
muted = names_muted


class Finder(names_dialog_type()):
    def __init__(self, parent: Any = None) -> None:
        """Build original controls; refresh once and retain only owned resources."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(480)
        self.resize(500, 560)
        self.glyphs = font_glyphs()
        self.matches = []
        root = self.root

        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText("acute · *.ss0? · é · U+00E9")
        self.search.setClearButtonEnabled(True)
        big = self.search.font
        big.setPointSizeF(big.pointSizeF() * 1.15)
        self.search.setFont(big)
        root.addWidget(self.search)

        self.table = self.make_table(["Glyph", "Char", "Unicode"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select in Font window")
        self.close_button.setAutoDefault(False)
        self.select_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(self.search.textChanged, lambda *a: self.refresh())
        self._connect(self.search.returnPressed, lambda *a: self.select_matches())
        self._connect(
            self.table.cellDoubleClicked,
            lambda row, *a: self.select_row(row),
        )
        self._connect(self.select_button.clicked, lambda *a: self.select_matches())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()
        self.search.setFocus()

    @names_snapshot_refresh
    def refresh(self) -> None:
        """Read current font data; update original fields and action availability."""
        self.glyphs = font_glyphs()
        if not self.glyphs:
            self.subtitle.setText("Open a font first.")
            self.select_button.setEnabled(False)
            return
        kind, self.matches = find(self.glyphs, self.search.text)
        self.subtitle.setText(
            f"Searching {len(self.glyphs)} glyphs by {kind}. "
            "Enter selects every match in the Font window.",
        )
        shown = self.matches[:MAX_ROWS]
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setRowCount(len(shown))
        for row, (name, codes) in enumerate(shown):
            char = "".join(chr(c) for c in codes[:1])
            cells = [name, char, " ".join(f"U+{c:04X}" for c in codes) or "–"]
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column == 1:
                    item.setTextAlignment(int(QtCore.Qt.AlignCenter))
                    item.setForeground(QtGui.QBrush(accent))
                self.table.setItem(row, column, item)
        more = f" (showing {MAX_ROWS})" if len(self.matches) > MAX_ROWS else ""
        self.select_button.setEnabled(bool(self.matches))
        self.status.setText(
            f"{len(self.matches)} match{'es' if len(self.matches) != 1 else ''}{more}",
        )

    def select_matches(self) -> None:
        """Select chosen rows, or every match, in the scanned font only."""
        self.ensure_snapshot()
        rows = sorted(
            {index.row() for index in self.table.selectionModel().selectedRows()},
        )
        names = (
            [self.matches[r][0] for r in rows]
            if rows
            else [name for name, _ in self.matches]
        )
        count = len(self.select_names(names))
        self.last_result = {"selected": names}
        self.status.setText(
            f"Selected {count} glyph{'s' if count != 1 else ''} in the Font window",
        )

    def select_row(self, row: int) -> None:
        """Select one double-clicked result in the scanned font only."""
        self.ensure_snapshot()
        if 0 <= row < len(self.matches):
            count = len(self.select_names([self.matches[row][0]]))
            self.last_result = {"selected": [self.matches[row][0]]}
            self.status.setText(
                f"Selected {self.matches[row][0]}" if count else "Glyph not found",
            )


def main() -> Any:
    """Open or replace this owned modeless Names panel."""
    return show_script_dialog(Finder, KEY)


if __name__ == "__main__":
    main()
