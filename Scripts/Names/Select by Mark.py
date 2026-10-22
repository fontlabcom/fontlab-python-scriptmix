# this_file: Scripts/Names/Select by Mark.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from Apache-2.0 FontLab samples; provenance in migration.json.
# FLM: Names · Select by Mark
"""Select glyphs in the Font window by their mark colour.

What it does:
    Lists every mark colour used in the font (and unmarked glyphs) with a
    swatch and a count. Pick one or more rows and click Select, or double-click
    a row. Optionally add to the current selection. Nothing in the font changes.

How it works:
    Group the current font's glyphs by native mark value, then draw swatches
    and counts. Selection goes through the shared Names panel source guard.

Why this design:
    Colour groups can identify a work batch without requiring a persistent
    naming convention.

How to use:
    Run Names > Select by Mark. Pick one or more rows and press Select, or
    double-click a row. Enable Add to the current selection when the old
    selection must remain.

Benefit:
    Turn existing mark colours into a Font-window selection while keeping the
    stored marks unchanged.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    names_dialog_type,
    names_font_window_selection,
    names_muted,
    names_snapshot_refresh,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Select by Mark"
KEY = "names_select_by_mark"
HUES = [
    (15, "red"),
    (45, "orange"),
    (70, "yellow"),
    (160, "green"),
    (200, "teal"),
    (255, "blue"),
    (290, "purple"),
    (335, "pink"),
    (361, "red"),
]


# ---------------------------------------------------------------- font access
def font_marks() -> list[tuple[str, int]]:
    """[(glyph name, mark)] for the current font, in font order."""
    font = fontlab.CurrentFont()
    return [(g.name, int(g.mark or 0)) for g in font.glyphs] if font is not None else []


def font_window_selection() -> list[str]:
    """Read exact Font window selection through the shared helper, no fallback."""
    return names_font_window_selection()


# ---------------------------------------------------------------- core
def mark_color(mark: int, lightness: int = 150) -> Any | None:
    """The QColor FontLab shows for a mark value, or None for no mark."""
    if mark <= 0:
        return None
    if mark <= 360:
        return QtGui.QColor.fromHsl(mark - 1, 200, lightness)
    grey = min(255, lightness // 2 + max(0, mark - 1000) // 2)
    return QtGui.QColor(grey, grey, grey)


def mark_label(mark: int) -> str:
    """Describe native mark hue or grey value; zero means unmarked."""
    if mark <= 0:
        return "Unmarked"
    if mark > 360:
        return f"Grey {mark - 1000}"
    hue = mark - 1
    return (
        next(name for limit, name in HUES if hue < limit).capitalize()
        + f" (hue {hue}°)"
    )


def groups(marks: list[tuple[str, int]]) -> list[tuple[int, list[str]]]:
    """[(mark, [names])], marked colours by hue first, unmarked last."""
    out = {}
    for name, mark in marks:
        out.setdefault(mark, []).append(name)
    return sorted(out.items(), key=lambda item: (item[0] == 0, item[0]))


# ---------------------------------------------------------------- GUI
muted = names_muted


def swatch(mark: int, size: int = 16) -> Any:
    """Paint a native mark icon; always release the owned painter."""
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtGui.QColor(0, 0, 0, 0))
    painter = QtGui.QPainter(pixmap)
    try:
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        color = mark_color(mark)
        if color is None:
            painter.setPen(
                QtGui.QPen(
                    QtGui.QBrush(QtGui.QColor(128, 128, 128)),
                    1.0,
                    QtCore.Qt.DashLine,
                ),
            )
            painter.drawRoundedRect(QtCore.QRectF(1, 1, size - 2, size - 2), 4, 4)
        else:
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(color))
            painter.drawRoundedRect(QtCore.QRectF(0, 0, size, size), 4, 4)
    finally:
        painter.end()
    return QtGui.QIcon(pixmap)


class SelectByMark(names_dialog_type()):
    def __init__(self, parent: Any = None) -> None:
        """Build original controls; refresh once and retain only owned resources."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(520)
        self.resize(540, 460)
        self.groups = []
        root = self.root

        self.table = self.make_table(["Mark", "Glyphs", "Examples"])
        self.table.setIconSize(QtCore.QSize(16, 16))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        root.addWidget(self.table, 1)

        self.add = QtGui.QCheckBox("Add to the current selection")
        root.addWidget(self.add)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Reload")
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select")
        self.select_button.setDefault(True)
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(
            self.table.cellDoubleClicked,
            lambda row, *a: self.select_rows([row]),
        )
        self._connect(self.select_button.clicked, lambda *a: self.select_rows())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.reload()

    @names_snapshot_refresh
    def reload(self) -> None:
        """Rescan the current font; render complete rows before enabling selection."""
        marks = font_marks()
        self.groups = groups(marks)
        if not marks:
            self.subtitle.setText("Open a font first.")
        else:
            marked = sum(len(names) for mark, names in self.groups if mark)
            self.subtitle.setText(
                f"{marked} of {len(marks)} glyphs carry a mark. Pick colours and click Select "
                "(or double-click a row).",
            )
        self.table.setRowCount(len(self.groups))
        for row, (mark, names) in enumerate(self.groups):
            label = QtGui.QTableWidgetItem(swatch(mark), mark_label(mark))
            count = QtGui.QTableWidgetItem(str(len(names)))
            count.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
            sample = QtGui.QTableWidgetItem(
                " ".join(names[:6]) + (" …" if len(names) > 6 else ""),
            )
            sample.setForeground(QtGui.QBrush(self.palette.color(QtGui.QPalette.Link)))
            for column, item in enumerate((label, count, sample)):
                self.table.setItem(row, column, item)
        self.select_button.setEnabled(bool(self.groups))
        self.status.setText(
            f"{len(self.groups)} mark value{'s' if len(self.groups) != 1 else ''}",
        )

    def select_rows(self, rows: list[int] | None = None) -> None:
        """Select requested mark groups; optionally add current selection."""
        self.ensure_snapshot()
        if rows is None:
            rows = sorted(
                {index.row() for index in self.table.selectionModel().selectedRows()},
            )
        names = [
            name
            for row in rows
            if 0 <= row < len(self.groups)
            for name in self.groups[row][1]
        ]
        if not names:
            self.status.setText("Pick at least one row first.")
            return
        count = len(self.select_names(names, add=self.add.isChecked()))
        self.last_result = {
            "marks": [self.groups[r][0] for r in rows],
            "names": names,
            "selected": count,
        }
        self.status.setText(f"Selected {count} glyph{'s' if count != 1 else ''}")


def main() -> Any:
    """Open or replace this owned modeless Names panel."""
    return show_script_dialog(SelectByMark, KEY)


if __name__ == "__main__":
    main()
