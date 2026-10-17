# FLM: Names · Suffix Tool
# this_file: Scripts/Names/Suffix Tool.py
# SPDX-License-Identifier: Apache-2.0
"""Add, remove or replace a glyph-name suffix (.ss01, .sc, .alt…) on the selected glyphs.

The preview shows every new name and refuses names that already exist or
collide, so no glyph is ever replaced. Suffixed alternates are usually not
encoded: optionally move their Unicode off. Components follow the rename.
One Apply is one Undo step.
"""

from typing import Any

import fly
import fontlab
from fly.ap.scripting import names_editor_api
from PythonQt import QtGui

scripting = fly.ap.scripting
api = names_editor_api()
NamesEditDialog = scripting.names_edit_dialog_type()
muted = NamesEditDialog.muted

TITLE = "Suffix Tool"
KEY = "names_suffix_tool"
PRESETS = api.PRESETS
VALID = api.VALID
MODES = api.MODES


current_package = scripting.current_package

selected_names = api.selected_names

font_names = api.font_names

text_of = api.text_of

dotted = api.dotted

suffixed = api.suffixed

auto_links = api.auto_links

auto_refusal = api.auto_refusal

plan = api.suffix_plan


def run(package: Any, rows: list, clear_unicode: bool, *, expected: Any = None) -> list:
    """Rename accepted alternates and optionally remove their encoding."""
    return api.rename(package, rows, TITLE, clear_unicode, expected=expected)


class SuffixTool(NamesEditDialog):
    """Retain the original Suffix Tool controls, defaults and editing actions."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control before any fallible font read."""
        super().__init__(parent, TITLE, KEY, "name")
        root = self.root
        self.setMinimumWidth(520)
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.mode = QtGui.QComboBox()
        for label, _ in MODES:
            self.mode.addItem(label)
        self.suffix = QtGui.QComboBox()
        self.suffix.setEditable(True)
        for preset in PRESETS:
            self.suffix.addItem(preset)
        self.replacement = QtGui.QComboBox()
        self.replacement.setEditable(True)
        for preset in PRESETS:
            self.replacement.addItem(preset)
        self.replacement_label = QtGui.QLabel("With")
        self.clear_unicode = QtGui.QCheckBox(
            "Remove Unicode from renamed glyphs (alternates are unencoded)",
        )
        self.clear_unicode.setChecked(True)
        form.addWidget(QtGui.QLabel("Operation"), 0, 0)
        form.addWidget(self.mode, 0, 1, 1, 3)
        form.addWidget(QtGui.QLabel("Suffix"), 1, 0)
        form.addWidget(self.suffix, 1, 1)
        form.addWidget(self.replacement_label, 1, 2)
        form.addWidget(self.replacement, 1, 3)
        form.addWidget(self.clear_unicode, 2, 1, 1, 3)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        root.addLayout(form)

        self.table = self.make_table(["Glyph", "New name", "Check"])
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setMinimumHeight(200)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.mode.currentIndexChanged, lambda *a: self.mode_changed())
        for combo in (self.suffix, self.replacement):
            self._connect(combo.editTextChanged, lambda *a: self.refresh())
        self._connect(self.clear_unicode.toggled, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh(self.mode_changed)

    def mode_key(self) -> str:
        """Return the original add/remove/replace identifier."""
        return MODES[self.mode.currentIndex][1]

    def mode_changed(self) -> None:
        """Retain replacement and Unicode-control visibility for the chosen mode."""
        replace = self.mode_key() == "replace"
        self.replacement.setVisible(replace)
        self.replacement_label.setVisible(replace)
        self.clear_unicode.setVisible(self.mode_key() != "remove")
        self.refresh()

    @scripting.names_editor_read
    def refresh(self) -> None:
        """Render the complete original preview and enable only actionable results."""
        count = len(self.selection)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText(
                "Select glyphs in the Font window, then run this script again.",
            )
        else:
            names = ", ".join(self.selection[:8]) + (" …" if count > 8 else "")
            self.subtitle.setText(
                f"{count} glyph{'s' if count != 1 else ''}: {names}. "
                "Components follow; kerning and features keep the old names.",
            )
        self.links = (
            auto_links(self.package, font_names()) if self.package else ((), {})
        )
        self.rows = (
            plan(
                self.selection,
                font_names(),
                self.mode_key(),
                text_of(self.suffix),
                text_of(self.replacement),
                self.links,
            )
            if self.package
            else []
        )
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        alert = QtGui.QColor("#d33")
        self.table.setRowCount(len(self.rows))
        for row, (old, new, status) in enumerate(self.rows):
            cells = [old, new, "✓" if status == "ok" else status]
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column == 1 and status == "ok":
                    item.setForeground(QtGui.QBrush(accent))
                if column == 2:
                    item.setForeground(
                        QtGui.QBrush(accent if status == "ok" else alert),
                    )
                self.table.setItem(row, column, item)
        ok = sum(1 for r in self.rows if r[2] == "ok")
        refused = len(self.rows) - ok
        self.apply_button.setEnabled(ok > 0)
        untouched = count - len(self.rows)
        parts = (
            [f"{ok} to rename"]
            + ([f"{refused} refused"] if refused else [])
            + ([f"{untouched} not affected"] if untouched else [])
        )
        self.status.setText(" · ".join(parts))

    @scripting.names_editor_apply
    def apply(self) -> None:
        """Write exactly the staged batch and refresh its visible outcome."""
        clear = self.clear_unicode.isChecked() and self.mode_key() != "remove"
        renamed = run(self.package, self.rows, clear, expected=self._names_snapshot)
        self._batch_written = bool(renamed)
        self._last_applied = renamed
        self.last_result = {"renamed": renamed, "cleared_unicode": clear}
        self.links = auto_links(self.package, font_names())
        fontlab.UpdateAll()
        mapping = dict(renamed)
        self.selection = [mapping.get(n, n) for n in self.selection]
        self.refresh()
        self.status.setText(
            f"Renamed {len(renamed)} glyph{'s' if len(renamed) != 1 else ''}",
        )

    def load_initial(self) -> None:
        """Read the original selection and references after safe UI construction."""
        self.selection = selected_names()
        self.links = auto_links(self.package, font_names())


def main() -> Any:
    """Replace only this owned tool and share guarded native Close disposal."""
    return scripting.show_script_dialog(SuffixTool, KEY)


if __name__ == "__main__":
    main()
