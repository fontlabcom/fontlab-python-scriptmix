# this_file: Scripts/Names/Case Pairs.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from Apache-2.0 FontLab samples; provenance in migration.json.
# FLM: Names · Case Pairs
"""Find the upper- or lowercase counterparts of the selected glyphs and select them.

What it does:
    Counterparts come from Unicode case mapping of each glyph's code point;
    unencoded alternates use their base name (a.ss01 -> A.ss01). Select the
    counterparts alone or together with the originals. Nothing in the font
    changes.

How it works:
    Map Unicode case counterparts to existing glyphs. For unencoded suffixed
    names, try the base counterpart with the original suffix; reject multi-
    character case expansions.

Why this design:
    A Unicode case change is not always one glyph, so missing or expanding
    mappings remain visible rather than guessed.

How to use:
    Select source glyphs and run Names > Case Pairs. Review the mapping rows,
    choose whether originals stay selected and select the available
    counterparts.

Benefit:
    Move between related case glyphs while preserving names, encodings and
    outlines.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    names_dialog_type,
    names_font_glyphs,
    names_muted,
    names_selected_names,
    names_snapshot_refresh,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Case Pairs"
KEY = "names_case_pairs"


# ---------------------------------------------------------------- font access
def selected_names() -> list[str]:
    """Read current font state through the shared Names access helper."""
    return names_selected_names()


def font_glyphs() -> list[tuple[str, list[int]]]:
    """Read current font state through the shared Names access helper."""
    return names_font_glyphs()


# ---------------------------------------------------------------- core
def swap_case(char: str) -> str:
    """The single-character case counterpart, or "" (ß -> SS has no single counterpart)."""
    other = char.lower() if char != char.lower() else char.upper()
    return other if len(other) == 1 and other != char else ""


def index(
    glyphs: list[tuple[str, list[int]]],
) -> tuple[dict[str, list[int]], dict[int, str]]:
    """(codes by name, first glyph by code) for fast lookups."""
    by_code = {}
    for glyph, codes in glyphs:
        for code in codes:
            by_code.setdefault(code, glyph)
    return dict(glyphs), by_code


def counterpart(
    name: str, codes_of: dict[str, list[int]], by_code: dict[int, str]
) -> tuple[str | None, str]:
    """(counterpart name or None, how) for one glyph name."""
    codes = codes_of.get(name, [])
    if codes:
        other = swap_case(chr(codes[0]))
        if other and ord(other) in by_code:
            return by_code[ord(other)], f"{chr(codes[0])} → {other}"
        return (
            None,
            f"{chr(codes[0])} has no counterpart in the font" if other else "no case",
        )
    base, dot, suffix = name.partition(".")
    base_codes = codes_of.get(base, [])
    if dot and base_codes:
        partner, _ = counterpart(base, codes_of, by_code)
        if partner and f"{partner}.{suffix}" in codes_of:
            return f"{partner}.{suffix}", f"via {base} → {partner}"
    return None, "unencoded"


# ---------------------------------------------------------------- GUI
muted = names_muted


class CasePairs(names_dialog_type()):
    def __init__(self, parent: Any = None) -> None:
        """Build original controls; refresh once and retain only owned resources."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(480)
        self.resize(500, 440)
        self.pairs = []
        root = self.root

        self.table = self.make_table(["Glyph", "Counterpart", "How"])
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        root.addWidget(self.table, 1)
        self.keep = QtGui.QCheckBox("Keep the original glyphs selected too")
        root.addWidget(self.keep)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Reload selection")
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select counterparts")
        self.select_button.setDefault(True)
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.select_button.clicked, lambda *a: self.select_counterparts())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.reload()

    @names_snapshot_refresh
    def reload(self) -> None:
        """Rescan the current font; render complete rows before enabling selection."""
        glyphs = font_glyphs()
        self.selection = selected_names() if glyphs else []
        codes_of, by_code = index(glyphs)
        self.pairs = [
            (name, *counterpart(name, codes_of, by_code)) for name in self.selection
        ]
        found = [p for p in self.pairs if p[1]]
        if not glyphs:
            self.subtitle.setText("Open a font first.")
        elif not self.selection:
            self.subtitle.setText(
                "Select glyphs in the Font window, then click Reload selection.",
            )
        else:
            self.subtitle.setText(
                f"{len(found)} of {len(self.selection)} selected glyphs have a case counterpart "
                "in this font.",
            )
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setRowCount(len(self.pairs))
        for row, (name, partner, how) in enumerate(self.pairs):
            for column, text in enumerate((name, partner or "–", how)):
                item = QtGui.QTableWidgetItem(text)
                if column == 1 and partner:
                    item.setForeground(QtGui.QBrush(accent))
                if column == 2:
                    item.setForeground(QtGui.QBrush(QtGui.QColor(muted(self))))
                self.table.setItem(row, column, item)
        self.select_button.setEnabled(bool(found))
        self.status.setText(f"{len(found)} counterpart{'s' if len(found) != 1 else ''}")

    def select_counterparts(self) -> None:
        """Select mapped partners; optionally retain the originally scanned glyphs."""
        self.ensure_snapshot()
        names = [p[1] for p in self.pairs if p[1]]
        if self.keep.isChecked():
            names += self.selection
        selected = self.select_names(names)
        self.last_result = {"selected": selected}
        self.status.setText(
            f"Selected {len(selected)} glyph{'s' if len(selected) != 1 else ''}",
        )


def main() -> Any:
    """Open or replace this owned modeless Names panel."""
    return show_script_dialog(CasePairs, KEY)


if __name__ == "__main__":
    main()
