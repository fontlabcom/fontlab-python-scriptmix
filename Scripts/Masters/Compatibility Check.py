# this_file: Scripts/Masters/Compatibility Check.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Masters · Compatibility Check
"""Check that every master of each glyph can interpolate: same contours, nodes, anchors, components.

The tree lists each glyph with ✓ or ✗; expand it to see the counts per master, with the values
that differ from the other masters highlighted. Contour structure is compared node by node
(on-curve / handle pattern), anchors by name and components by base glyph. Select the failing
glyphs in the Font window with one click. Read-only.
"""

from typing import Any, ClassVar

from fly import ap, qt
from fly.ap.scripting import (
    current_package,  # noqa: F401 - original public interface
    masters_api,
    masters_dialog_type,
    masters_snapshot_refresh,
    show_script_dialog,
)
from fly.ap.scripting import (
    masters_make_table as make_table,  # noqa: F401 - original helper interface
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = masters_api()
muted = _api.muted
selected_names = _api.selected_names
master_layers = _api.master_layers
own_contours = _api.own_contours
node_points = _api.node_points
signature = _api.signature
summary = _api.summary
check_glyph = _api.check_glyph
all_names = _api.all_names
TITLE = "Master Compatibility"
KEY = "masters_compatibility_check"


class SampleDialog(masters_dialog_type()):
    """Keep the original per-menu shell interface on the shared owned panel."""

    def __init__(self, parent: Any = None) -> None:
        """Build every control before initial binding or native reads."""
        super().__init__(parent, TITLE, KEY)


def select_in_font_window(names: list[str]) -> None:
    """Preserve the public original selector, guarded by the active dialog snapshot."""
    import sys

    dialog = getattr(sys, "_fontlab_samples", {}).get(KEY)
    if dialog is None:
        raise ValueError("Open the compatibility panel before selecting results.")
    dialog.select_names(names)


class Compatibility(SampleDialog):
    """Complete original read-only Masters tool with guarded native actions."""

    ACTION = "Select ✗ Glyphs"
    COLUMNS: ClassVar[list[str]] = [
        "Glyph · master",
        "Contours",
        "Nodes",
        "Anchors",
        "Components",
        "Status",
    ]

    def build(self) -> None:
        """Build every original chart/table/tree control and guarded action connection."""
        self.setMinimumWidth(600)
        grid = self.form()
        self.source = QtGui.QComboBox()
        self.source.addItem(f"Selected glyphs ({len(self.names)})")
        self.source.addItem("Whole font")
        self._connect(self.source.currentIndexChanged, lambda *a: self.refresh())
        grid.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
        grid.addWidget(self.source, 0, 1)
        grid.setColumnStretch(1, 1)
        self.tree = QtGui.QTreeWidget()
        self.tree.setColumnCount(len(self.COLUMNS))
        self.tree.setHeaderLabels(self.COLUMNS)
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setUniformRowHeights(True)
        header = self.tree.header()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtGui.QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)
        self.tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tree.setMinimumHeight(300)
        self.root.addWidget(self.tree, 1)

    @masters_snapshot_refresh
    def refresh(self) -> None:
        """Read and render complete results from the original bound font and selection."""
        (self.results, self.failing) = ({}, [])
        self._structures = {}
        self.tree.clear()
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.apply_button.setEnabled(False)
            return
        self._scope_whole = self.source.currentIndex == 1
        names = all_names() if self._scope_whole else self.names
        self._scope_names = tuple(names)
        self.subtitle.setText(
            f"{len(names)} glyphs across {len(self.masters)} masters: {', '.join(self.masters)}"
        )
        accent = QtGui.QColor(
            self.palette.color(QtGui.QPalette.Active, QtGui.QPalette.Link)
        )
        bad = QtGui.QColor("#d33")
        ink = QtGui.QBrush(
            self.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText)
        )
        muted_color = QtGui.QColor(
            self.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText)
        )
        muted_color.setAlpha(130)
        right = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        for name in names:
            glyph = self.package.findName(name)
            if glyph is None:
                continue
            (sigs, ok, problems) = check_glyph(glyph, self.masters)
            self._structures[name] = sigs
            self.results[name] = ok
            if not ok:
                self.failing.append(name)
            top = QtGui.QTreeWidgetItem(self.tree)
            top.setText(0, name)
            top.setForeground(0, ink)
            top.setText(5, "✓" if ok else "✗ " + ", ".join(problems))
            top.setTextAlignment(5, right)
            top.setForeground(5, QtGui.QBrush(muted_color if ok else bad))
            values = {m: summary(s) for (m, s) in sigs.items() if s is not None}
            for master, sig in sigs.items():
                child = QtGui.QTreeWidgetItem(top)
                child.setText(0, master)
                for column in range(5):
                    child.setForeground(column, ink)
                if sig is None:
                    child.setText(1, "auto layer · not compared")
                    child.setForeground(1, QtGui.QBrush(muted_color))
                    continue
                for column, value in enumerate(summary(sig), start=1):
                    child.setText(column, str(value))
                    child.setTextAlignment(column, right)
                    others = [v[column - 1] for (m, v) in values.items() if m != master]
                    if others and value != max(set(others), key=others.count):
                        font = child.font(column)
                        font.setBold(True)
                        child.setFont(column, font)
                        child.setForeground(column, QtGui.QBrush(accent))
            top.setExpanded(not ok)
        self.apply_button.setEnabled(bool(self.failing))
        self.status.setText(
            f"{len(self.failing)} of {len(self.results)} glyphs incompatible"
        )

    def apply(self) -> None:
        """Refuse changed displayed source before the original explicit UI action."""
        self.ensure_snapshot()
        self.select_names(self.failing)
        self.last_result = {"selected": list(self.failing)}
        fontlab.UpdateAll()
        self.status.setText(
            f"Selected {len(self.failing)} incompatible glyphs in the Font window"
        )


def main() -> Any:
    """Replace and show this owned original Masters tool."""
    return show_script_dialog(Compatibility, KEY)


if __name__ == "__main__":
    main()
