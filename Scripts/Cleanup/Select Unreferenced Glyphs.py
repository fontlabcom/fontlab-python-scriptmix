# this_file: Scripts/Cleanup/Select Unreferenced Glyphs.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Cleanup · Select Unreferenced Glyphs
"""List unencoded glyphs that nothing references, and select them in the Font window for review.

A glyph counts as referenced when it has a code point, is used as a component or in an
auto recipe on any layer, is named in the OpenType feature source, or belongs to a feature
class that the source uses. Candidates are often alternates waiting for a feature, so the
script only selects them; it never deletes. Feature files pulled in with include() cannot
be read and stop the scan."""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package,  # noqa: F401 - Original public helper re-export.
    review_action,
    review_dialog_type,
    review_snapshot_refresh,
    show_script_dialog,
    unreferenced_api,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = unreferenced_api()
feature_source, tokens, class_members = (
    _api.feature_source,
    _api.tokens,
    _api.class_members,
)
font_names, unreferenced, RESERVED = (
    _api.font_glyph_names,
    _api.unreferenced,
    _api.RESERVED,
)
TITLE = "Select Unreferenced Glyphs"
KEY = "cleanup_unused_glyphs_report"


def muted(widget: Any) -> str:
    """Copy the original WindowText colour before applying the 160 alpha value."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(160)
    return color.name(QtGui.QColor.HexArgb)


class Dialog(review_dialog_type()):
    """Review every original candidate; selection is the only intended action."""

    def __init__(self, parent: Any = None) -> None:
        """Build all original controls and Close before reading native references."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(560)
        self.last_result = None
        root = self.root
        self.subtitle.setText(
            "Unencoded glyphs not used as components, in auto recipes, in the feature code or in its classes. Many are alternates waiting for a feature: review before deleting anything."
        )
        self.table = QtGui.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Glyph", "Hint"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setMinimumHeight(250)
        root.addWidget(self.table, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setAutoDefault(False)
        self.apply_button = QtGui.QPushButton("Select in Font window")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self.initial_refresh()

    @review_snapshot_refresh
    def refresh(self) -> None:
        """Publish all original ordered candidates after complete source/domain checks."""
        if self.package is None:
            self.subtitle.setText("Open a font, then run this script again.")
            self.apply_button.setEnabled(False)
            return
        self.rows = unreferenced(self.package)
        self.table.setRowCount(len(self.rows))
        for row, cells in enumerate(self.rows):
            for column, text in enumerate(cells):
                self.table.setItem(row, column, QtGui.QTableWidgetItem(text))
        self.apply_button.setEnabled(bool(self.rows))
        count = len(self.rows)
        self.status.setText(
            f"{count} unreferenced glyph{('s' if count != 1 else '')}"
            if count
            else "Every glyph is encoded or referenced"
        )

    @review_action
    def apply(self) -> None:
        """Select the exact candidates only while their captured source is unchanged."""
        names = [name for name, note in self.rows]
        self.select_names(names)
        self.last_result = {"selected": len(set(names))}
        self.status.setText(
            f"Selected {self.last_result['selected']} glyphs in the Font window for review"
        )


def select(names: list[str]) -> dict[str, int]:
    """Keep the original helper behind the currently owned panel's source guard."""
    import sys

    dialog = getattr(sys, "_fontlab_samples", {}).get(KEY)
    if dialog is None:
        raise ValueError("Open this panel before selecting its results.")
    dialog.select_names(names)
    return {"selected": len(set(names))}


def main() -> Any:
    """Show the complete original non-modal owned review panel."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
