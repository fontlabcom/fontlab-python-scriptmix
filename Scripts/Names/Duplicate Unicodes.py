# FLM: Names · Duplicate Unicodes
# this_file: Scripts/Names/Duplicate Unicodes.py
# SPDX-License-Identifier: Apache-2.0
"""Find code points assigned to more than one glyph and remove them from the extra glyphs.

Each shared code point is a group; ticked glyphs lose that code point on
Apply. By default the glyph that has it as its first (primary) code point
keeps it, preferring the earliest in font order. Untick to keep. One Undo
step.
"""

from typing import Any

import fly
import fontlab
from fly.ap.scripting import names_editor_api
from PythonQt import QtCore, QtGui

scripting = fly.ap.scripting
api = names_editor_api()
NamesEditDialog = scripting.names_edit_dialog_type()
muted = NamesEditDialog.muted

TITLE = "Duplicate Unicodes"
KEY = "names_duplicate_unicodes"


current_package = scripting.current_package

duplicates = api.duplicates

auto_dependants = api.auto_dependants

rebuild_note = api.rebuild_note

show_rebuilds = api.show_rebuilds

printable = api.printable


def font_unicodes() -> list:
    """Return original ordered name/code rows from the shared complete read."""
    return list(api.font_unicodes().items())


def run(package: Any, removals: list, *, expected: Any = None) -> list:
    """Remove precisely ticked code points after complete preflight."""
    return api.remove_unicodes(package, removals, TITLE, expected=expected)


class DuplicateUnicodes(NamesEditDialog):
    """Retain the original Duplicate Unicodes controls, defaults and editing actions."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control before any fallible font read."""
        super().__init__(parent, TITLE, KEY, "unicodes")
        root = self.root
        self.setMinimumWidth(480)
        self.resize(520, 480)
        self.tree = QtGui.QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Code point · glyph", "Action"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        header = self.tree.header()
        header.setSectionResizeMode(0, QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        root.addWidget(self.tree, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)  # the auto-composite note can be long
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Rescan")
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Remove ticked")
        self.apply_button.setDefault(True)
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.tree.itemChanged, lambda *a: self.update_actions())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh(self.reload)

    @scripting.names_editor_reload
    def reload(self) -> None:
        """Explicitly reread the current font and selection for this tool."""
        glyphs = font_unicodes()
        self.groups = duplicates(glyphs)
        self.items = {}  # (name, code) -> QTreeWidgetItem
        with self.block_signals(self.tree):
            self.tree.clear()
            accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
            for code, keeper, names in self.groups:
                top = QtGui.QTreeWidgetItem(
                    [f"U+{code:04X}  {printable(code)}   {len(names)} glyphs", ""],
                )
                bold = top.font(0)
                bold.setBold(True)
                top.setFont(0, bold)
                self.tree.addTopLevelItem(top)
                for name in names:
                    child = QtGui.QTreeWidgetItem([name, ""])
                    child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
                    child.setCheckState(
                        0,
                        QtCore.Qt.Unchecked if name == keeper else QtCore.Qt.Checked,
                    )
                    top.addChild(child)
                    self.items[name, code] = child
                top.setExpanded(True)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not self.groups:
            self.subtitle.setText(f"No shared code points among {len(glyphs)} glyphs.")
        else:
            self.subtitle.setText(
                f"{len(self.groups)} code point{'s are' if len(self.groups) != 1 else ' is'} "
                "shared. Ticked glyphs lose that code point; unticked ones keep it.",
            )
        self.accent = accent
        self.update_actions()

    def removals(self) -> list:
        """Return only manually ticked glyph/codepoint removals."""
        return [
            key
            for key, item in self.items.items()
            if item.checkState(0) == QtCore.Qt.Checked
        ]

    def update_actions(self) -> None:
        """Update ticked actions and retain the original auto-layer warning."""
        self.update_actions_listing()
        show_rebuilds(self, sorted({name for name, _ in self.removals()}))

    def update_actions_listing(self) -> None:
        """Show exact tick counts and keep/remove descriptions."""
        with self.block_signals(self.tree):
            alert = QtGui.QColor("#d33")
            for (_name, code), item in self.items.items():
                checked = item.checkState(0) == QtCore.Qt.Checked
                item.setText(1, f"remove U+{code:04X}" if checked else "keeps it")
                item.setForeground(1, QtGui.QBrush(alert if checked else self.accent))
        count = len(self.removals())
        self.apply_button.setEnabled(count > 0)
        self.status.setText(f"{count} removal{'s' if count != 1 else ''} ticked")

    @scripting.names_editor_apply
    def apply(self) -> None:
        """Write exactly the staged batch and refresh its visible outcome."""
        changed = run(self.package, self.removals(), expected=self._names_snapshot)
        self._batch_written = bool(changed)
        self._last_applied = changed
        self.last_result = {"changed": changed}
        fontlab.UpdateAll()
        self.check_binding()
        self.reload()
        self.status.setText(
            f"Updated {len(changed)} glyph{'s' if len(changed) != 1 else ''}",
        )

    def load_initial(self) -> None:
        """Read the original selection and references after safe UI construction."""


def main() -> Any:
    """Replace only this owned tool and share guarded native Close disposal."""
    return scripting.show_script_dialog(DuplicateUnicodes, KEY)


if __name__ == "__main__":
    main()
