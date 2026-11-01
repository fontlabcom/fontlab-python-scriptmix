# this_file: Scripts/Names/Character Set Compare.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from Apache-2.0 FontLab samples; provenance in migration.json.
# FLM: Names · Charset Compare
"""Paste a text or a character set and compare it with the font's encoded characters.

What it does:
    Lists characters of the text the font lacks and characters the font has
    that the text does not use, with names from unicodedata. Language presets
    fill in common alphabets. Copy the missing set, or select the extra glyphs
    in the Font window. Nothing in the font changes.

How it works:
    Compare distinct non-whitespace input characters with every encoded font
    character. Show missing and extra sets with Unicode names and code points.

Why this design:
    A character-set comparison answers a repertoire question without confusing
    unencoded alternates with encoded characters.

How to use:
    Run Names > Character Set Compare. Paste text or choose a language preset,
    inspect both lists, then copy missing characters or select extra glyphs as
    required.

Benefit:
    Prepare a character-coverage review while leaving encodings and glyph
    membership intact.
"""

import unicodedata
from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    names_dialog_type,
    names_muted,
    names_snapshot_refresh,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Charset Compare"
KEY = "names_charset_compare"
LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
PRESETS = [
    ("Paste your own text…", ""),
    ("Basic Latin (ASCII)", "".join(chr(c) for c in range(0x21, 0x7F))),
    (
        "Latin-1 letters",
        LATIN + "".join(chr(c) for c in range(0xC0, 0x100) if chr(c).isalpha()),
    ),
    ("Polish", LATIN + "ĄĆĘŁŃÓŚŹŻąćęłńóśźż"),
    ("Czech", LATIN + "ÁČĎÉĚÍŇÓŘŠŤÚŮÝŽáčďéěíňóřšťúůýž"),
    ("German", LATIN + "ÄÖÜẞäöüß„“‚‘"),
    ("French", LATIN + "ÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸàâæçéèêëîïôœùûüÿ«»"),
    ("Spanish", LATIN + "ÁÉÍÑÓÚÜáéíñóúü¡¿"),
    ("Turkish", LATIN + "ÇĞİÖŞÜçğıöşü"),
]


# ---------------------------------------------------------------- font access
def font_chars() -> dict[str, str]:
    """{character: glyph name} for every encoded glyph of the current font."""
    font = fontlab.CurrentFont()
    out = {}
    for glyph in font.glyphs if font is not None else []:
        for code in glyph.unicodes:
            out.setdefault(chr(code), glyph.name)
    return out


# ---------------------------------------------------------------- core
def text_chars(text: str) -> list[str]:
    """Distinct non-whitespace characters of the text, sorted by code point."""
    return sorted({c for c in text if not c.isspace()}, key=ord)


def compare(text: str, available: dict[str, str]) -> tuple[list[str], list[str]]:
    """(missing, extra): characters of the text absent from the font, and font characters absent from it."""
    wanted = text_chars(text)
    wanted_set = set(wanted)
    missing = [c for c in wanted if c not in available]
    extra = sorted(
        (c for c in available if c not in wanted_set and not c.isspace()),
        key=ord,
    )
    return missing, extra


def describe(char: str) -> str:
    """Format a character, code point and Unicode name for comparison lists."""
    return f"{char}   U+{ord(char):04X}   {unicodedata.name(char, '').title()}"


# ---------------------------------------------------------------- GUI
muted = names_muted


class CharsetCompare(names_dialog_type()):
    def __init__(self, parent: Any = None) -> None:
        """Build original controls; refresh once and retain only owned resources."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(620)
        self.resize(680, 560)
        self.available = font_chars()
        self.missing, self.extra = [], []
        root = self.root

        row = QtGui.QHBoxLayout()
        row.addWidget(QtGui.QLabel("Preset"))
        self.preset = QtGui.QComboBox()
        for label, _ in PRESETS:
            self.preset.addItem(label)
        row.addWidget(self.preset, 1)
        root.addLayout(row)
        self.text = QtGui.QPlainTextEdit()
        self.text.setPlaceholderText("Paste a text or a list of characters…")
        self.text.setMaximumHeight(90)
        root.addWidget(self.text)

        lists = QtGui.QHBoxLayout()
        lists.setSpacing(12)
        self.missing_label, self.missing_list = self._column(lists)
        self.extra_label, self.extra_list = self._column(lists)
        root.addLayout(lists, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.copy_button = QtGui.QPushButton("Copy missing")
        self.select_button = QtGui.QPushButton("Select extra glyphs")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.copy_button)
        footer.addWidget(self.select_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        self._connect(
            self.preset.currentIndexChanged,
            lambda *a: self.use_preset(self.preset.currentIndex),
        )
        self._connect(self.text.textChanged, lambda *a: self.refresh())
        self._connect(self.copy_button.clicked, lambda *a: self.copy_missing())
        self._connect(self.select_button.clicked, lambda *a: self.select_extra())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _column(self, parent: Any) -> tuple[Any, Any]:
        """Create a read-only character list with its count heading."""
        column = QtGui.QVBoxLayout()
        label = QtGui.QLabel()
        bold = label.font
        bold.setBold(True)
        label.setFont(bold)
        listing = QtGui.QListWidget()
        listing.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        listing.setAlternatingRowColors(True)
        listing.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        listing.setTextElideMode(QtCore.Qt.ElideRight)
        column.addWidget(label)
        column.addWidget(listing, 1)
        parent.addLayout(column, 1)
        return label, listing

    def use_preset(self, index: int) -> None:
        """Fill the text control with the complete selected language alphabet."""
        if 0 < index < len(PRESETS):
            self.text.setPlainText(PRESETS[index][1])

    @names_snapshot_refresh
    def refresh(self) -> None:
        """Read current font data; update original fields and action availability."""
        self.available = font_chars()
        text = self.text.toPlainText()
        self.missing, self.extra = compare(text, self.available)
        count = len(text_chars(text))
        if not self.available:
            self.subtitle.setText("Open a font with encoded glyphs first.")
        else:
            self.subtitle.setText(
                f"The font encodes {len(self.available)} characters; the text uses {count}.",
            )
        self.missing_label.setText(f"Missing from the font ({len(self.missing)})")
        self.extra_label.setText(f"In the font, not in the text ({len(self.extra)})")
        alert = QtGui.QColor("#d33")
        self.missing_list.clear()
        for char in self.missing:
            item = QtGui.QListWidgetItem(describe(char))
            item.setForeground(QtGui.QBrush(alert))
            self.missing_list.addItem(item)
        self.extra_list.clear()
        for char in self.extra:
            self.extra_list.addItem(
                QtGui.QListWidgetItem(f"{describe(char)}   · {self.available[char]}"),
            )
        self.copy_button.setEnabled(bool(self.missing))
        self.select_button.setEnabled(bool(self.extra) and bool(text.strip()))
        covered = count - len(self.missing)
        self.status.setText(
            f"Coverage {covered}/{count}"
            + (f" · {100.0 * covered / count:.0f}%" if count else ""),
        )

    def copy_missing(self) -> None:
        """Copy the missing character set from a valid comparison snapshot."""
        self.ensure_snapshot()
        QtGui.QApplication.clipboard().setText("".join(self.missing))
        self.status.setText(f"Copied {len(self.missing)} characters")

    def select_extra(self) -> None:
        """Select encoded characters absent from the text in the scanned font."""
        self.ensure_snapshot()
        names = [self.available[c] for c in self.extra]
        count = len(self.select_names(names))
        self.last_result = {"selected": names}
        self.status.setText(
            f"Selected {count} extra glyph{'s' if count != 1 else ''} in the Font window",
        )


def main() -> Any:
    """Open or replace this owned modeless Names panel."""
    return show_script_dialog(CharsetCompare, KEY)


if __name__ == "__main__":
    main()
