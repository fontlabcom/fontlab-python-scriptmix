# this_file: Scripts/Features/Feature Code Viewer.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Features · Feature Code Viewer
"""Read-only feature source for the whole font. Choose a feature and search its code.

What it does:
    Run with a font active. All original controls use the shared fly panel lifecycle.
    Feature data is font-wide; reopen after switching fonts or changing source.

How it works:
    Read ordered prefix and feature blocks through Fontport. Keep empty blocks
    and exact source; highlight literal search matches without compiling the
    font.

Why this design:
    Direct source inspection avoids confusing generated classes with the code
    that is actually stored.

How to use:
    Run Features > Feature Code Viewer with a font open. Choose the prefix or
    a feature, enter search text and use the search action to move through its
    matches.

Benefit:
    Locate a rule or language declaration while leaving feature source and
    glyph data unchanged.
"""

import html
import re
from collections.abc import Iterable
from typing import Any

from fly import ap, qt
from fly.ap.scripting import features_dialog_type, show_script_dialog
from fly.fp.feature_blocks import read_feature_blocks

fontlab = ap.fontlab
QtCore, QtGui = (qt.QtCore, qt.QtGui)
FeaturesDialog = features_dialog_type()

TITLE = "Feature Code Inspector"
KEY = "features_code_viewer"
SUBTITLE = (
    "Read-only feature source for the whole font. Choose a feature and search its code."
)
ACTION = "Find next"


def run(features: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    """Copy ordered (tag, exact source) pairs from a VFJ-equivalent snapshot.

    Native feature iteration can yield positions rather than tags; raw prefix
    access can synthesize class declarations. The caller must use Fontport's exact
    read_feature_blocks snapshot so displayed source matches persisted source.
    Empty sources are retained, order is unchanged, and nothing is compiled.
    """
    return list(features)


class Dialog(FeaturesDialog):
    def __init__(self, parent: Any = None) -> None:
        """Initialize this owned tool and preserve its original controls."""
        super().__init__(parent, title=TITLE, subtitle=SUBTITLE, key=KEY)

    def setup(self) -> None:
        """Build the original controls inside the shared owned panel."""
        root = self.prepare()
        self.apply_button.setText(ACTION)
        self.feature = QtGui.QComboBox()
        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText("Search in the selected feature…")
        root.addWidget(self.feature)
        root.addWidget(self.search)
        self.code = QtGui.QTextEdit()
        self.code.setReadOnly(True)
        self.code.setAcceptRichText(False)
        root.addWidget(self.code, 1)
        self.sources = [("Prefix / languagesystems", "")]
        if self.package is not None:
            blocks = read_feature_blocks(self.package)
            self.sources = [("Prefix / languagesystems", blocks["prefix"])]
            self.sources += run(blocks["features"])
        for tag, _ in self.sources:
            self.feature.addItem(tag)
        self._connect(self.feature.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.search.textChanged, lambda *a: self.highlight())

    def refresh(self) -> None:
        """Rebuild the complete visible preview; invalidate it on failure."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self.package is not None:
            self.ensure_font()
        self.code.setPlainText(self.sources[self.feature.currentIndex][1])
        self.highlight()
        self.apply_button.setEnabled(bool(self.package and self.search.text))
        self._preview_valid = True

    def highlight(self) -> None:
        """Highlight every case-insensitive literal search match safely."""
        text = self.sources[self.feature.currentIndex][1]
        needle = self.search.text
        self.match_count = 0
        chunks = []
        position = 0
        if needle:
            background = self.palette.color(QtGui.QPalette.Highlight).name()
            foreground = self.palette.color(QtGui.QPalette.HighlightedText).name()
            for match in re.finditer(re.escape(needle), text, re.IGNORECASE):
                chunks.extend(
                    (
                        html.escape(text[position : match.start()]),
                        '<span style="background-color:'
                        + background
                        + ";color:"
                        + foreground
                        + '">'
                        + html.escape(match.group())
                        + "</span>",
                    )
                )
                position = match.end()
                self.match_count += 1
        chunks.append(html.escape(text[position:]))
        self.code.setHtml(
            '<pre style="white-space:pre-wrap">' + "".join(chunks) + "</pre>"
        )
        self.status.setText(
            f"{len(self.sources) - 1} features · {self.match_count} search matches"
        )
        self.apply_button.setEnabled(bool(needle and self.package))

    def apply(self) -> None:
        """Perform the selected original tool action on its valid preview."""
        self.ensure_preview()
        if not self.search.text:
            return
        if not self.code.find(self.search.text):
            cursor = self.code.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            self.code.setTextCursor(cursor)
            self.code.find(self.search.text)
        self.last_result = {"matches": self.match_count}


def main() -> Any:
    """Replace this tool through the shared owned-window registry."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
