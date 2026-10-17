# this_file: Scripts/Features/Ligature Finder.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Features · Ligature Finder
"""Find underscore-named glyphs and existing input glyphs. Name-derived recipes do not imply outline components.

Run with a font active. All original controls use the shared fly panel lifecycle.
Feature data is font-wide; reopen after switching fonts or changing source.
"""

from collections.abc import Iterable
from typing import Any

from fly import ap, qt
from fly.ap.feature_code import safe_name
from fly.ap.scripting import (
    features_dialog_type,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = (qt.QtCore, qt.QtGui)
FeaturesDialog = features_dialog_type()


TITLE = "Ligature Recipe Finder"
KEY = "features_ligature_finder"
SUBTITLE = "Find underscore-named glyphs and existing input glyphs. Name-derived recipes do not imply outline components."
ACTION = "Copy liga snippet"


def run(names: Iterable[str]) -> list[tuple[str, str, str]]:
    """Return (ligature, space-separated inputs, status) rows in name order.

    Split the stem at underscores and apply the ligature suffix to every input.
    Ready requires safe names and every input to exist in the supplied glyph
    names. Other rows report missing/invalid inputs; underscore-only or leading
    dot names do not imply a recipe. Recipes are naming hints, not evidence of
    outline components or successful shaping. Duplicate names collapse.
    """
    known = set(names)
    rows = []
    for name in sorted(known):
        if "_" not in name or name.startswith("."):
            continue
        stem, separator, suffix = name.partition(".")
        parts = [
            part + (separator + suffix if separator else "") for part in stem.split("_")
        ]
        missing = [part for part in parts if not part or part not in known]
        valid = (
            not missing and safe_name(name) and all(safe_name(part) for part in parts)
        )
        rows.append(
            (
                name,
                " ".join(parts),
                "Ready"
                if valid
                else "Missing / invalid input: "
                + ", ".join(p or "(empty)" for p in missing),
            )
        )
    return rows


def liga_text(rows: list[tuple[str, str, str]]) -> str:
    """Build liga rules for recipes whose input glyphs all exist."""
    rules = [
        "    sub " + inputs + " by " + name + ";"
        for name, inputs, state in rows
        if state == "Ready"
    ]
    return "feature liga {\n" + "\n".join(rules) + "\n} liga;" if rules else ""


class Dialog(FeaturesDialog):
    def __init__(self, parent: Any = None) -> None:
        """Initialize this owned tool and preserve its original controls."""
        super().__init__(parent, title=TITLE, subtitle=SUBTITLE, key=KEY)

    def setup(self) -> None:
        """Build the original controls inside the shared owned panel."""
        root = self.prepare()
        self.apply_button.setText(ACTION)
        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText("Filter ligature names or input glyphs…")
        root.addWidget(self.search)
        self.table = self.make_table(
            ["Ligature glyph", "Input glyphs", "Recipe status"]
        )
        root.addWidget(self.table, 1)
        self.code = QtGui.QPlainTextEdit()
        self.code.setReadOnly(True)
        root.addWidget(self.code, 1)
        self.all_rows = run(self.names)
        self._connect(self.search.textChanged, lambda *a: self.refresh())

    def refresh(self) -> None:
        """Rebuild the complete visible preview; invalidate it on failure."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self.package is not None:
            self.ensure_font()
        needle = self.search.text.lower()
        self.fill([row for row in self.all_rows if needle in " ".join(row).lower()])
        self.snippet = liga_text(self.rows)
        self.code.setPlainText(
            self.snippet or "No usable underscore recipes in this view."
        )
        self.apply_button.setEnabled(bool(self.snippet))
        self.status.setText(
            f"{len(self.rows)} candidates · {sum(row[2] == 'Ready' for row in self.rows)} usable recipes"
        )
        self._preview_valid = True

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
