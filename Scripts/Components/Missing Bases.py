# this_file: Scripts/Components/Missing Bases.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Missing Bases
"""Find components that point to glyphs which do not exist, or to a base glyph without that master.

Such components draw nothing and break exports. The tree groups the problems by
the missing base glyph; expand a group to see the composites and masters affected.
Select affected glyphs puts them in the Font window selection. Nothing is changed."""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    components_action,
    components_api,
    components_dialog_type,
    components_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = components_api()
current_package = _api.current_package
font_glyph_names = _api.font_glyph_names
has_layer = _api.has_layer
missing = _api.missing
item_ink = _api.item_ink
muted = _api.muted
frame = _api.frame

TITLE = "Missing Component Bases"
KEY = "components_missing_bases"
ERROR = "#d33"


class MissingBases(components_dialog_type()):
    """Complete original component inspector with owned read-only source guards."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control and Close before reading native sources."""
        super().__init__(parent, TITLE, KEY)
        root = self.root
        self.setMinimumWidth(540)
        self.tree = QtGui.QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Missing base / composite", "Master", "Problem"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        header = self.tree.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        self.tree.setMinimumHeight(280)
        root.addWidget(self.tree, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select affected glyphs")
        self.select_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)
        self._connect(self.select_button.clicked, lambda *a: self.select_affected())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    def affected(self) -> Any:
        """Preserve the original affected calculation and native interface."""
        return sorted(
            {glyph for rows in self.groups.values() for (glyph, _, _) in rows}
        )

    @components_snapshot_refresh
    def rescan(self, exists: Any = None) -> None:
        """Preserve the original rescan calculation and native interface."""
        self.groups = (
            missing(self.package, font_glyph_names(), self.masters, exists)
            if self.package
            else {}
        )
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            self.subtitle.setText(
                f"Every component on all {len(self.masters)} masters checked against the glyphs and master layers of this font."
            )
        error = QtGui.QColor(ERROR)
        dim = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        dim.setAlpha(140)
        self.tree.clear()
        for base, rows in sorted(self.groups.items()):
            top = QtGui.QTreeWidgetItem(
                [base, "", f"{len(rows)} component{('s' if len(rows) != 1 else '')}"]
            )
            for column in range(self.tree.columnCount):
                top.setForeground(column, item_ink())
            top.setForeground(0, QtGui.QBrush(error))
            bold = top.font(0)
            bold.setBold(True)
            top.setFont(0, bold)
            for glyph, master, reason in rows:
                child = QtGui.QTreeWidgetItem([glyph, master, reason])
                for column in range(self.tree.columnCount):
                    child.setForeground(column, item_ink())
                child.setForeground(2, QtGui.QBrush(dim))
                top.addChild(child)
            self.tree.addTopLevelItem(top)
            top.setExpanded(True)
        self.select_button.setEnabled(bool(self.groups))
        self.status.setText(
            f"{len(self.groups)} missing base{('s' if len(self.groups) != 1 else '')} in {len(self.affected())} glyphs"
            if self.groups
            else "Every component has its base glyph"
        )

    @components_action
    def select_affected(self) -> None:
        """Preserve the original select affected calculation and native interface."""
        self.select_names(self.affected())
        self.status.setText(
            f"Selected {len(self.affected())} glyphs in the Font window"
        )


def select_in_font(names: list[str]) -> None:
    """Route the original helper alias through the active panel's source guard."""
    import sys

    dialog = getattr(sys, "_fontlab_samples", {}).get(KEY)
    if dialog is None:
        raise ValueError("Open this panel before selecting its results.")
    dialog.select_names(names)


def main() -> Any:
    """Replace and display the complete original owned component inspector."""
    return show_script_dialog(MissingBases, KEY)


if __name__ == "__main__":
    main()
