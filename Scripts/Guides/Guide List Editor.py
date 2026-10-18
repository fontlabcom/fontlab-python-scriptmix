# this_file: Scripts/Guides/Guide List Editor.py
# SPDX-License-Identifier: Apache-2.0
"""Edit glyph-guide coordinates, angles and names of the first selected glyph.

Choose current or all masters. Edit X, Y, angle in degrees and name; Add guide,
Delete selected and Revert change the proposal. Apply makes each editable master
match its rows in one Undo step. Unchanged guides retain their native properties;
hints are kept. Bad/non-finite cells and unknown masters refuse the whole write.
Unsafe automatic dependants are refused. Close releases signals and glyphs.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    components_action,
    guide_editor_dialog_type,
    guide_rewrite_api,
    guides_api,
    masters_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
TITLE, KEY = "Guide List Editor", "guides_list_editor"
_api, _guide = guide_rewrite_api(), guides_api()
master_layers, guide_record, glyph_guides = (
    _guide.master_layers,
    _guide.guide_record,
    _guide.glyph_guides,
)
COLUMNS = ["Master", "X", "Y", "Angle °", "Name"]
parse_row = _api.parse_row


class ListEditor(guide_editor_dialog_type()):
    """Complete original guide controls on the shared owned lifecycle."""

    ACTION = "Apply"

    def __init__(self, parent: Any = None) -> None:
        """Finish controls before any native source read."""
        super().__init__(parent, TITLE, KEY)

    def build(self) -> None:
        """Retain every original control and callback."""
        self.setMinimumWidth(560)
        self.last_result = None
        self.glyphs = []
        self.glyph = None
        self.pending_targets = set()
        root = self.root
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Masters"), 0, 0)
        form.addWidget(self.scope, 0, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)
        self.table = QtGui.QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(220)
        root.addWidget(self.table, 1)
        rows = QtGui.QHBoxLayout()
        self.add_button = QtGui.QPushButton("Add guide")
        self.delete_button = QtGui.QPushButton("Delete selected")
        self.reload_button = QtGui.QPushButton("Revert")
        rows.addWidget(self.add_button)
        rows.addWidget(self.delete_button)
        rows.addStretch(1)
        rows.addWidget(self.reload_button)
        root.addLayout(rows)
        self._connect(self.scope.currentIndexChanged, lambda *a: self.reload())
        self._connect(self.add_button.clicked, lambda *a: self.add_row())
        self._connect(self.delete_button.clicked, lambda *a: self.delete_row())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())

    @masters_snapshot_refresh
    def reload(self) -> Any:
        """Fill the table from the font (discards unapplied edits)."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif self.glyph is None:
            self.subtitle.setText(
                "Select a glyph in the Font window, then run this script again."
            )
        else:
            skipped = [m for m, layer in self.layers() if layer.autoLayer]
            note = (
                f" · auto layer{('s' if len(skipped) != 1 else '')} not editable: {', '.join(skipped)}"
                if skipped
                else ""
            )
            self.subtitle.setText(
                f"Glyph guides of {self.glyph.name}; Apply makes each master match its rows{note}"
            )
        rows = [
            (m, guide_record(g))
            for m, layer in self.layers()
            if not layer.autoLayer
            for g in glyph_guides(layer)
        ]
        self.table.setRowCount(len(rows))
        for row, (master, values) in enumerate(rows):
            self.set_row(row, master, values)
        self.apply_button.setEnabled(bool(self.editable_masters()))
        self.status.setText(f"{len(rows)} guide{('s' if len(rows) != 1 else '')}")
        self.table.setEnabled(self.glyph is not None)
        self.add_button.setEnabled(bool(self.editable_masters()))
        self.delete_button.setEnabled(bool(self.editable_masters()))
        self.pending_targets = {self.glyph.name} if self.glyph is not None else set()
        self.guard_apply(len(self.editable_masters()))

    @components_action
    def apply(self) -> Any:
        wanted = self.table_records()
        jobs = []
        for master, layer in self.layers():
            if (
                master in wanted
                and [guide_record(g) for g in glyph_guides(layer)] != wanted[master]
            ):
                jobs.append((self.glyph, layer, wanted[master]))
        self.last_result = _api.replace_guides(self.package, jobs, TITLE)
        self.reload()
        self.status.setText(
            f"Updated guides on {self.last_result['layers']} master{('s' if self.last_result['layers'] != 1 else '')}"
        )

    refresh = reload


def main() -> Any:
    """Replace and show the complete owned guide editor."""
    return show_script_dialog(ListEditor, KEY)


if __name__ == "__main__":
    main()
