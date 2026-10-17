# FLM: Names · Mark Color Palette
# this_file: Scripts/Names/Mark Color Palette.py
# SPDX-License-Identifier: Apache-2.0
"""Click a colour swatch to mark the selected glyphs with it (or clear the mark).

Each swatch shows how many glyphs in the font, and in the selection, carry
that mark. FontLab stores a mark as hue + 1 (1-360), grey as 1000 + level,
and 0 for none. One click is one Undo step.
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

TITLE = "Mark Color Palette"
KEY = "names_mark_color_palette"
PRESETS = [
    ("None", 0),
    ("Red", 1),
    ("Orange", 31),
    ("Yellow", 56),
    ("Green", 121),
    ("Teal", 171),
    ("Blue", 211),
    ("Purple", 271),
    ("Pink", 321),
    ("Grey", 1128),
]


current_package = scripting.current_package

selected_glyphs = api.selected_glyphs

font_marks = api.font_marks

counts = api.counts

auto_dependants = api.auto_dependants

rebuild_note = api.rebuild_note

show_rebuilds = api.show_rebuilds


def run(package: Any, glyphs: list, mark: int, *, expected: Any = None) -> list:
    """Set or clear every differing selected glyph mark."""
    return api.set_marks(package, glyphs, mark, TITLE, expected=expected)


def mark_color(mark: Any, lightness: Any = 150) -> Any:
    """The QColor FontLab shows for a mark value, or None for no mark."""
    if mark <= 0:
        return None
    if mark <= 360:
        return QtGui.QColor.fromHsl(mark - 1, 200, lightness)
    grey = min(255, lightness // 2 + max(0, mark - 1000) // 2)
    return QtGui.QColor(grey, grey, grey)


def swatch_style(mark: Any, widget: Any) -> str:
    color = mark_color(mark)
    border = widget.palette.color(QtGui.QPalette.Mid).name()
    if color is None:
        text = widget.palette.color(QtGui.QPalette.ButtonText).name()
        return (
            f"QPushButton {{ color: {text}; border: 1px dashed {border}; border-radius: 8px; padding: 8px; "
            f"text-align: left; }}"
        )
    text = "#111111" if color.lightness() > 140 else "#ffffff"
    pressed = color.darker(115).name()
    return (
        f"QPushButton {{ background: {color.name()}; color: {text}; border: 1px solid {color.darker(120).name()};"
        f" border-radius: 8px; padding: 8px; text-align: left; }}"
        f" QPushButton:pressed {{ background: {pressed}; }}"
    )


def dot_icon(mark: Any, size: Any = 12) -> Any:
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtGui.QColor(0, 0, 0, 0))
    color = mark_color(mark)
    painter = QtGui.QPainter(pixmap)
    try:
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if color is None:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(128, 128, 128)), 1.0))
            painter.drawEllipse(1, 1, size - 2, size - 2)
        else:
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(color))
            painter.drawEllipse(0, 0, size, size)
    finally:
        painter.end()
    return QtGui.QIcon(pixmap)


class Palette(NamesEditDialog):
    """Retain the original Mark Color Palette controls, defaults and editing actions."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control before any fallible font read."""
        super().__init__(parent, TITLE, KEY, "mark")
        root = self.root
        self.setMinimumWidth(500)
        self.resize(560, 420)
        grid = QtGui.QGridLayout()
        grid.setSpacing(8)
        self.swatches = {}
        for index, (label, mark) in enumerate(PRESETS):
            button = QtGui.QPushButton(label)
            button.setMinimumHeight(48)
            button.setStyleSheet(swatch_style(mark, self))
            button.setToolTip(f"Mark value {mark}")
            grid.addWidget(button, index // 5, index % 5)
            self.swatches[mark] = button
            self._connect(button.clicked, lambda *a, m=mark: self.apply(m))
        root.addLayout(grid)

        caption = QtGui.QLabel("Selection")
        bold = caption.font
        bold.setBold(True)
        caption.setFont(bold)
        root.addWidget(caption)
        self.list = QtGui.QListWidget()
        self.list.setViewMode(QtGui.QListView.IconMode)
        self.list.setFlow(QtGui.QListView.LeftToRight)
        self.list.setWrapping(True)
        self.list.setResizeMode(QtGui.QListView.Adjust)
        self.list.setSpacing(4)
        self.list.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.list.setMinimumHeight(90)
        self.list.setIconSize(QtCore.QSize(14, 14))
        root.addWidget(self.list, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)  # the auto-composite note can be long
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Reload selection")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh(self.refresh)

    @scripting.names_editor_reload
    def reload(self) -> None:
        """Explicitly reread the current font and selection for this tool."""
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.refresh()

    @scripting.names_editor_read
    def refresh(self) -> None:
        """Render the complete original preview and enable only actionable results."""
        self.refresh_listing()
        show_rebuilds(self, [g.name for g in self.glyphs])

    def refresh_listing(self) -> None:
        """Populate original counts and result cells without changing the font."""
        self.check_binding()
        marks = font_marks()
        names = {g.name for g in self.glyphs}
        in_font, in_selection = counts(marks), counts(marks, names)
        for label, mark in PRESETS:
            button = self.swatches[mark]
            button.setText(
                f"{label}\n{in_font.get(mark, 0)} · {in_selection.get(mark, 0)} sel",
            )
            button.setEnabled(bool(self.glyphs))
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText(
                "Select glyphs in the Font window, then click Reload selection.",
            )
        else:
            self.subtitle.setText(
                f"Click a swatch to mark the {count} selected glyph{'s' if count != 1 else ''}. "
                "Numbers: glyphs in the font · in the selection.",
            )
        self.list.clear()
        for glyph in self.glyphs:
            item = QtGui.QListWidgetItem(dot_icon(marks.get(glyph.name, 0)), glyph.name)
            self.list.addItem(item)
        other = sorted(m for m in in_font if m not in self.swatches)
        extra = (
            f" · other marks in font: {', '.join(str(m) for m in other)}"
            if other
            else ""
        )
        self.status.setText(f"{len(marks)} glyphs in font{extra}")

    @scripting.names_editor_apply
    def apply(self, mark: Any) -> None:
        """Write exactly the staged batch and refresh its visible outcome."""
        changed = (
            run(self.package, self.glyphs, mark, expected=self._names_snapshot)
            if self.package
            else []
        )
        self._batch_written = bool(changed)
        self._last_applied = changed
        self.last_result = {"mark": mark, "changed": changed}
        fontlab.UpdateAll()
        self.refresh()
        label = {m: l for l, m in PRESETS}.get(mark, str(mark))
        self.status.setText(
            f"{label}: changed {len(changed)} glyph{'s' if len(changed) != 1 else ''}",
        )

    def load_initial(self) -> None:
        """Read the original selection and references after safe UI construction."""
        self.glyphs = selected_glyphs(self.package)


def main() -> Any:
    """Replace only this owned tool and share guarded native Close disposal."""
    return scripting.show_script_dialog(Palette, KEY)


if __name__ == "__main__":
    main()
