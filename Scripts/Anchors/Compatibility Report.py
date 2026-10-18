# this_file: Scripts/Anchors/Compatibility Report.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Compatibility Report
"""Compare anchor names across masters: a glyph whose masters carry different anchors cannot interpolate them.

The tree lists each glyph with its anchor count per master; expand a glyph to see
which master lacks which anchor. Mismatches are flagged and listed first.
Auto layers show "auto" and are not compared: FontLab rebuilds their anchors.
Double-click a glyph to select it in the Font window. Nothing is changed."""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    anchors_action,
    anchors_api,
    anchors_dialog_type,
    anchors_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = anchors_api()
current_package = _api.current_package
font_glyph_names = _api.font_glyph_names
anchor_sets = _api.anchor_sets
is_mismatch = _api.is_mismatch
item_ink = _api.item_ink
muted = _api.muted
frame = _api.frame
selected_names = _api.exact_selected_names

TITLE = "Anchor Compatibility"
KEY = "anchors_compatibility_report"
ERROR = "#d33"


class AnchorCompatibility(anchors_dialog_type()):
    def __init__(self, parent: Any = None) -> None:
        """Build all original controls before reading native font or anchor values."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(600)
        root = self.root
        bar = QtGui.QHBoxLayout()
        bar.setSpacing(10)
        self.scope = QtGui.QComboBox()
        self.scope.addItem("Whole font")
        self.scope.addItem(f"Selected glyphs ({len(self.selection)})")
        self.only_bad = QtGui.QCheckBox("Only mismatches")
        bar.addWidget(QtGui.QLabel("Glyphs"))
        bar.addWidget(self.scope)
        bar.addStretch(1)
        bar.addWidget(self.only_bad)
        root.addLayout(bar)
        self.tree = QtGui.QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Glyph / anchor", ""])
        self.tree.setAlternatingRowColors(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tree.setMinimumHeight(320)
        root.addWidget(self.tree, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select mismatches")
        self.select_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)
        self._connect(self.scope.currentIndexChanged, lambda *a: self.rescan())
        self._connect(self.only_bad.toggled, lambda *a: self.refresh())
        self._connect(
            self.tree.itemDoubleClicked, lambda item, column: self.open_item(item)
        )
        self._connect(
            self.select_button.clicked, lambda *a: self.select_names(self.mismatches())
        )
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    @anchors_snapshot_refresh
    def rescan(self) -> None:
        """Scan captured names and masters into the complete anchor compatibility tree."""
        names = font_glyph_names() if self.scope.currentIndex == 0 else self.selection
        self.rows = (
            anchor_sets(self.package, names, self.masters) if self.package else []
        )
        self.refresh()

    def mismatches(self) -> Any:
        """List glyphs whose non-auto master anchor-name sets differ."""
        return [name for (name, sets) in self.rows if is_mismatch(sets)]

    @anchors_action
    def refresh(self) -> None:
        """Rebuild all original display data for the current source and selectors."""
        bad = set(self.mismatches())
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            self.subtitle.setText(
                f"Anchor names per master for {len(self.rows)} glyphs with anchors. Expand a glyph for details; double-click to select it in the Font window."
            )
        text = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        dim = QtGui.QColor(text)
        dim.setAlpha(120)
        error = QtGui.QColor(ERROR)
        self.tree.clear()
        # Controls exist before binding; configure the actual master columns now.
        self.tree.setColumnCount(len(self.masters) + 2)
        self.tree.setHeaderLabels(["Glyph / anchor", *self.masters, ""])
        header = self.tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(
            len(self.masters) + 1, QtGui.QHeaderView.ResizeToContents
        )
        ordered = sorted(self.rows, key=lambda r: (r[0] not in bad,))
        for name, sets in ordered:
            if self.only_bad.isChecked() and name not in bad:
                continue
            counts = [
                "auto" if m in sets and sets[m] is None else str(len(sets.get(m) or []))
                for m in self.masters
            ]
            top = QtGui.QTreeWidgetItem([name, *counts, "✗" if name in bad else "✓"])
            for column in range(self.tree.columnCount):
                top.setForeground(column, item_ink())
            top.setData(0, QtCore.Qt.UserRole, name)
            mark = len(self.masters) + 1
            top.setForeground(mark, QtGui.QBrush(error if name in bad else dim))
            if name in bad:
                bold = top.font(0)
                bold.setBold(True)
                top.setFont(0, bold)
            every = sorted({a for names in sets.values() if names for a in names})
            for anchor in every:
                cells = [
                    "auto"
                    if m in sets and sets[m] is None
                    else "✓"
                    if anchor in (sets.get(m) or [])
                    else "missing"
                    for m in self.masters
                ]
                child = QtGui.QTreeWidgetItem([anchor, *cells, ""])
                for column in range(self.tree.columnCount):
                    child.setForeground(column, item_ink())
                child.setData(0, QtCore.Qt.UserRole, name)
                for column, cell in enumerate(cells, 1):
                    child.setForeground(
                        column, QtGui.QBrush(error if cell == "missing" else dim)
                    )
                top.addChild(child)
            for column in range(1, len(self.masters) + 2):
                top.setTextAlignment(column, int(QtCore.Qt.AlignCenter))
            self.tree.addTopLevelItem(top)
            for index in range(top.childCount()):
                for column in range(1, len(self.masters) + 2):
                    top.child(index).setTextAlignment(
                        column, int(QtCore.Qt.AlignCenter)
                    )
            if name in bad:
                top.setExpanded(True)
        self.select_button.setEnabled(bool(bad))
        self.status.setText(
            f"{len(bad)} glyph{('s' if len(bad) != 1 else '')} with different anchors across masters"
            if bad
            else "All masters carry the same anchor names"
        )

    @anchors_action
    def open_item(self, item: Any) -> None:
        """Select the tree item glyph after validating the captured font source."""
        name = item.data(0, QtCore.Qt.UserRole)
        if name:
            self.select_names([name])
            self.status.setText(f"Selected {name} in the Font window")


def select_in_font(names: list[str]) -> None:
    """Route the original helper through the active panel's source guard."""
    import sys

    dialog = getattr(sys, "_fontlab_samples", {}).get(KEY)
    if dialog is None:
        raise ValueError("Open this panel before selecting its results.")
    dialog.select_names(names)


def main() -> Any:
    """Replace and show the complete original owned anchor panel."""
    return show_script_dialog(AnchorCompatibility, KEY)


if __name__ == "__main__":
    main()
