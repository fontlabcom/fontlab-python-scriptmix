# this_file: Scripts/Features/Suffix Report.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Features · Suffix Report
"""Suffix inventory across the whole font. Suggestions are naming hints; review the generated code.

Run with a font active. All original controls use the shared fly panel lifecycle.
Feature data is font-wide; reopen after switching fonts or changing source.
"""

import re
from collections.abc import Iterable
from typing import Any

from fly import ap, qt
from fly.ap.feature_code import (
    feature_text,
    safe_name,  # noqa: F401 - preserve sample helper interface
    suffix_pairs,
)
from fly.ap.scripting import (
    features_dialog_type,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = (qt.QtCore, qt.QtGui)
FeaturesDialog = features_dialog_type()


TITLE = "Suffix Feature Report"
KEY = "features_suffix_report"
SUBTITLE = "Suffix inventory across the whole font. Suggestions are naming hints; review the generated code."
ACTION = "Copy snippet"
SUGGESTIONS = {
    "sc": "smcp",
    "smcp": "smcp",
    "c2sc": "c2sc",
    "case": "case",
    "alt": "salt",
    "liga": "liga",
    "sups": "sups",
    "subs": "subs",
    "onum": "onum",
    "pnum": "pnum",
    "tnum": "tnum",
    "numr": "numr",
    "dnom": "dnom",
    "sinf": "sinf",
    "ordn": "ordn",
    "zero": "zero",
    "osf": "onum",
    "lf": "lnum",
    "tf": "tnum",
    "tosf": "onum",
    "frac": "frac",
    "init": "init",
    "medi": "medi",
    "fina": "fina",
    "isol": "isol",
}


def suggested_tag(suffix: str) -> str:
    """Suggest a feature tag from conventional suffix naming."""
    if re.fullmatch("ss(0[1-9]|1[0-9]|20)|cv(0[1-9]|[1-9][0-9])", suffix):
        return suffix
    if re.fullmatch("locl[A-Z]{2,3}", suffix):
        return "locl"
    return SUGGESTIONS.get(suffix.split(".")[0], "salt")


def run(names: Iterable[str]) -> list[tuple[str, int, int, str]]:
    """Return (suffix, glyph count, valid pair count, suggested tag) rows.

    Inventory the complete text after each glyph name's first dot, excluding
    leading-dot names. Counts include orphans; pairs require a safe existing
    base and alternate. Suggestions use naming conventions, not existing
    feature source or shaping analysis. Rows sort by suffix.
    """
    names = list(names)
    suffixes = sorted(
        {
            name.split(".", 1)[1]
            for name in names
            if "." in name and (not name.startswith("."))
        }
    )
    return [
        (
            suffix,
            sum(n.endswith("." + suffix) for n in names),
            len(suffix_pairs(names, suffix)),
            suggested_tag(suffix),
        )
        for suffix in suffixes
    ]


class Dialog(FeaturesDialog):
    def __init__(self, parent: Any = None) -> None:
        """Initialize this owned tool and preserve its original controls."""
        super().__init__(parent, title=TITLE, subtitle=SUBTITLE, key=KEY)

    def setup(self) -> None:
        """Build the original controls inside the shared owned panel."""
        root = self.prepare()
        self.apply_button.setText(ACTION)
        self.table = self.make_table(["Suffix", "Glyphs", "With base", "Suggested tag"])
        root.addWidget(self.table, 1)
        self.code = QtGui.QPlainTextEdit()
        mono = QtGui.QFont("Menlo")
        mono.setStyleHint(QtGui.QFont.Monospace)
        self.code.setFont(mono)
        self.code.setReadOnly(True)
        root.addWidget(self.code, 1)
        self._connect(self.table.itemSelectionChanged, lambda *a: self.preview())

    def refresh(self) -> None:
        """Rebuild the complete visible preview; invalidate it on failure."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self.package is not None:
            self.ensure_font()
        self.fill(run(self.names))
        if self.rows:
            self.table.selectRow(0)
        self.preview()
        self._preview_valid = True

    def preview(self) -> None:
        """Display the currently selected row and its usable feature snippet."""
        row = self.table.currentRow()
        pairs = (
            suffix_pairs(self.names, self.rows[row][0])
            if 0 <= row < len(self.rows)
            else []
        )
        self.snippet = feature_text(self.rows[row][3], pairs) if pairs else ""
        self.code.setPlainText(
            self.snippet
            or "No matching base glyphs. Select a suffix with usable pairs."
        )
        self.apply_button.setEnabled(bool(pairs))
        self.status.setText(
            f"{len(self.rows)} suffixes · {len(pairs)} safe substitution pairs selected"
        )

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
