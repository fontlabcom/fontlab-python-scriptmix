# FLM: Names · Glyph Tags
# this_file: Scripts/Names/Glyph Tags.py
# SPDX-License-Identifier: Apache-2.0
"""View, add and remove glyph tags across the selected glyphs.

The table lists every tag used in the selection with how many selected
glyphs carry it. Type a tag (completion offers the font's tags) and Add,
or tick tags and Remove. Each Add or Remove is one Undo step.
"""

import re
from typing import Any

import fly
import fontlab
from fly.ap.scripting import names_editor_api
from PythonQt import QtCore, QtGui

scripting = fly.ap.scripting
api = names_editor_api()
NamesEditDialog = scripting.names_edit_dialog_type()
muted = NamesEditDialog.muted

TITLE = "Glyph Tags"
KEY = "names_glyph_tags"
VALID = re.compile(r"^[^\s,]{1,64}$")


current_package = scripting.current_package

selected_glyphs = api.selected_glyphs

font_tags = api.font_tags

tag_counts = api.tag_counts

auto_dependants = api.auto_dependants

rebuild_note = api.rebuild_note

show_rebuilds = api.show_rebuilds


def run(
    package: Any,
    glyphs: list,
    add: tuple = (),
    remove: tuple = (),
    *,
    expected: Any = None,
) -> list:
    """Apply original tag add/remove semantics across the complete selection."""
    return api.set_tags(package, glyphs, TITLE, add, remove, expected=expected)


class GlyphTags(NamesEditDialog):
    """Retain the original Glyph Tags controls, defaults and editing actions."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control before any fallible font read."""
        super().__init__(parent, TITLE, KEY, "tags")
        root = self.root
        self.setMinimumWidth(600)
        self.resize(620, 460)
        row = QtGui.QHBoxLayout()
        row.setSpacing(8)
        self.tag = QtGui.QLineEdit()
        self.tag.setPlaceholderText("tag, e.g. review, spacing, done")
        self.completer_model = QtGui.QStringListModel()
        self.completer = QtGui.QCompleter()
        self.completer.setModel(self.completer_model)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.tag.setCompleter(self.completer)
        self.add_button = QtGui.QPushButton("Add to selection")
        row.addWidget(QtGui.QLabel("Tag"))
        row.addWidget(self.tag, 1)
        row.addWidget(self.add_button)
        root.addLayout(row)

        self.table = self.make_table(["Tag (tick to remove)", "Selected glyphs"])
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)  # the auto-composite note can be long
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Reload selection")
        self.close_button = QtGui.QPushButton("Close")
        self.remove_button = QtGui.QPushButton("Remove ticked")
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.remove_button)
        root.addLayout(footer)

        self._connect(self.tag.textChanged, lambda *a: self.update_buttons())
        self._connect(self.tag.returnPressed, lambda *a: self.add_tag())
        self._connect(self.add_button.clicked, lambda *a: self.add_tag())
        self._connect(self.remove_button.clicked, lambda *a: self.remove_ticked())
        self._connect(self.table.itemChanged, lambda *a: self.update_buttons())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh(self.reload)

    @scripting.names_editor_reload
    def reload(self) -> None:
        """Explicitly reread the current font and selection for this tool."""
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.completer_model.setStringList(
            font_tags(self.package) if self.package else [],
        )
        self.refresh()

    @scripting.names_editor_read
    def refresh(self) -> None:
        """Render the complete original preview and enable only actionable results."""
        self.refresh_listing()
        show_rebuilds(self, [g.name for g in self.glyphs])

    def refresh_listing(self) -> None:
        """Populate original counts and result cells without changing the font."""
        self.check_binding()
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText(
                "Select glyphs in the Font window, then click Reload selection.",
            )
        else:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (
                " …" if count > 8 else ""
            )
            self.subtitle.setText(f"{count} glyph{'s' if count != 1 else ''}: {names}")
        self.counts = tag_counts(self.glyphs)
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        with self.block_signals(self.table):
            self.table.setRowCount(len(self.counts))
            for row, (tag, used) in enumerate(self.counts):
                item = QtGui.QTableWidgetItem(tag)
                item.setFlags(
                    int(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                )
                item.setCheckState(QtCore.Qt.Unchecked)
                share = QtGui.QTableWidgetItem(f"{used} of {count}")
                share.setTextAlignment(
                    int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                )
                if used == count:
                    share.setForeground(QtGui.QBrush(accent))
                self.table.setItem(row, 0, item)
                self.table.setItem(row, 1, share)
        self.update_buttons()
        self.status.setText(
            f"{len(self.counts)} tag{'s' if len(self.counts) != 1 else ''} in the selection",
        )

    def ticked(self) -> list[str]:
        """Return precisely the tags currently checked for removal."""
        return [
            self.counts[row][0]
            for row in range(self.table.rowCount)
            if self.table.item(row, 0).checkState() == QtCore.Qt.Checked
        ]

    def update_buttons(self) -> None:
        """Retain tag validation and tick-dependent button enablement."""
        self.add_button.setEnabled(
            bool(self.glyphs) and bool(VALID.match(self.tag.text.strip())),
        )
        self.remove_button.setEnabled(bool(self.ticked()))

    @scripting.names_editor_apply
    def add_tag(self) -> None:
        """Add the entered valid tag to the captured selection."""
        tag = self.tag.text.strip()
        if not self.glyphs or not VALID.match(tag):
            return
        changed = run(
            self.package, self.glyphs, add=[tag], expected=self._names_snapshot
        )
        self._batch_written = bool(changed)
        self._last_applied = changed
        self.last_result = {"added": tag, "changed": changed}
        self.after_edit(
            f"Added '{tag}' to {len(changed)} glyph{'s' if len(changed) != 1 else ''}",
        )
        self.tag.clear()

    @scripting.names_editor_apply
    def remove_ticked(self) -> None:
        """Remove precisely the tags checked in the selection table."""
        tags = self.ticked()
        changed = run(
            self.package, self.glyphs, remove=tags, expected=self._names_snapshot
        )
        self._batch_written = bool(changed)
        self._last_applied = changed
        self.last_result = {"removed": tags, "changed": changed}
        self.after_edit(
            f"Removed {', '.join(tags)} from {len(changed)} glyph{'s' if len(changed) != 1 else ''}",
        )

    def after_edit(self, message: Any) -> None:
        """Refresh font-wide completion and selection counts after a successful edit."""
        fontlab.UpdateAll()
        self.check_binding()
        self.completer_model.setStringList(font_tags(self.package))
        self.refresh()
        self.status.setText(message)

    def load_initial(self) -> None:
        """Read the original selection and references after safe UI construction."""


def main() -> Any:
    """Replace only this owned tool and share guarded native Close disposal."""
    return scripting.show_script_dialog(GlyphTags, KEY)


if __name__ == "__main__":
    main()
