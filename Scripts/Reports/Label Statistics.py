# this_file: Scripts/Reports/Label Statistics.py
# SPDX-License-Identifier: Apache-2.0
"""Count glyphs by mark colour and by name suffix (.sc, .ss01, .loclPLK…); click a row to select them.

Two lists side by side give a quick census of a big font's working labels
and alternate sets. Clicking a row selects those glyphs in the Font window
(hold Add to extend the selection). Nothing in the font changes.
"""

import contextlib
import sys
from typing import Any

from fly import ap, qt
from fly.ap.scripting import current_package, select_glyphs

fontlab = ap.fontlab
(QtCore, QtGui) = (qt.QtCore, qt.QtGui)
TITLE = "Label Statistics"
KEY = "report_label_statistics"
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


def selected_names() -> list[str]:
    """Read the current selection for the explicit Add interaction."""
    font = ap.FL.fl.font
    return [font[i].name for i in range(len(font)) if ap.FL.fl.Selected(i)]


def font_labels() -> Any:
    """[(glyph name, mark)] of the current font, in font order."""
    font = fontlab.CurrentFont()
    return [(g.name, int(g.mark or 0)) for g in font.glyphs] if font is not None else []


def suffix_of(name: Any) -> Any:
    """'.ss01.sc' for 'a.ss01.sc'; '' for 'a' and '.notdef'."""
    (_head, dot, tail) = name[1:].partition(".")
    return "." + tail if dot else ""


def mark_color(mark: Any, lightness: Any = 150) -> Any:
    """Resolve a FontLab colour flag to its native swatch colour."""
    if mark <= 0:
        return None
    if mark <= 360:
        return QtGui.QColor.fromHsl(mark - 1, 200, lightness)
    grey = min(255, lightness // 2 + max(0, mark - 1000) // 2)
    return QtGui.QColor(grey, grey, grey)


def mark_label(mark: Any) -> Any:
    """Describe FontLab colour marks using the original hue buckets."""
    if mark <= 0:
        return "Unmarked"
    if mark > 360:
        return f"Grey {mark - 1000}"
    hue = mark - 1
    return (
        next(name for (limit, name) in HUES if hue < limit).capitalize()
        + f" (hue {hue}°)"
    )


def statistics(labels: Any) -> Any:
    """([(mark, [names])], [(suffix, [names])]) sorted by count, largest first."""
    (marks, suffixes) = ({}, {})
    for name, mark in labels:
        marks.setdefault(mark, []).append(name)
        suffixes.setdefault(suffix_of(name), []).append(name)

    def order(item: Any) -> Any:
        """Order."""
        return (-len(item[1]), str(item[0]))

    return (sorted(marks.items(), key=order), sorted(suffixes.items(), key=order))


def muted(widget: Any) -> Any:
    """Muted."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


def swatch(mark: Any, size: Any = 14) -> Any:
    """Draw a small mark icon and always release the native painter."""
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtGui.QColor(0, 0, 0, 0))
    painter = QtGui.QPainter(pixmap)
    try:
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        color = mark_color(mark)
        if color is None:
            painter.setPen(
                QtGui.QPen(
                    QtGui.QBrush(QtGui.QColor(128, 128, 128)), 1.0, QtCore.Qt.DashLine
                )
            )
            painter.drawRoundedRect(QtCore.QRectF(1, 1, size - 2, size - 2), 3, 3)
        else:
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(color))
            painter.drawRoundedRect(QtCore.QRectF(0, 0, size, size), 3, 3)
    finally:
        painter.end()
    return QtGui.QIcon(pixmap)


def make_table(first: Any) -> Any:
    """Build a read-only statistics table with a stretched label column."""
    table = QtGui.QTableWidget(0, 2)
    table.setHorizontalHeaderLabels([first, "Glyphs"])
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
    table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    header = table.horizontalHeader()
    header.setSectionResizeMode(QtGui.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(0, QtGui.QHeaderView.Stretch)
    table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    return table


class LabelStatistics(QtGui.QDialog):
    def __init__(self, parent: Any = None) -> None:
        """Build the original modeless report controls and connect owned signals."""
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(620)
        self.resize(680, 520)
        self._connections = []
        (self.marks, self.suffixes) = ([], [])
        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)
        columns = QtGui.QHBoxLayout()
        columns.setSpacing(12)
        self.mark_table = make_table("Mark colour")
        self.mark_table.setIconSize(QtCore.QSize(14, 14))
        self.suffix_table = make_table("Name suffix")
        columns.addWidget(self.mark_table, 1)
        columns.addWidget(self.suffix_table, 1)
        root.addLayout(columns, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.add = QtGui.QCheckBox("Add to selection")
        self.refresh_button = QtGui.QPushButton("Refresh")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.add)
        footer.addWidget(self.refresh_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)
        self._connect(
            self.mark_table.cellClicked,
            lambda row, *a: self.select_group(self.marks, row),
        )
        self._connect(
            self.suffix_table.cellClicked,
            lambda row, *a: self.select_group(self.suffixes, row),
        )
        self._connect(self.refresh_button.clicked, lambda *a: self.refresh())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _connect(self, signal: Any, slot: Any) -> None:
        """Guard and retain a signal connection for deterministic teardown."""

        def guarded(*args) -> None:
            """Guarded."""
            try:
                slot(*args)
            except Exception as error:  # noqa: BLE001 - PythonQt slots must contain all errors
                self.slot_error = repr(error)
                label = getattr(self, "status", None)
                if label is not None:
                    label.setText("Error: " + self.slot_error)

        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def fill(self, table: Any, groups: Any, label_of: Any, icon_of: Any = None) -> None:
        """Populate one statistics table with group labels, counts and swatches."""
        table.setRowCount(len(groups))
        for row, (key, names) in enumerate(groups):
            label = QtGui.QTableWidgetItem(label_of(key))
            if icon_of is not None:
                label.setIcon(icon_of(key))
            count = QtGui.QTableWidgetItem(str(len(names)))
            count.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
            table.setItem(row, 0, label)
            table.setItem(row, 1, count)

    def refresh(self) -> None:
        """Rebuild the current snapshot and publish it only after display succeeds."""
        self.package_id = None
        self.marks = []
        self.suffixes = []
        self.mark_table.setRowCount(0)
        self.suffix_table.setRowCount(0)
        try:
            package = current_package()
            if package is None:
                self.subtitle.setText("Open a font first.")
                return
            labels = font_labels()
            (result_marks, result_suffixes) = statistics(labels)
            if not labels:
                self.subtitle.setText("Open a font first.")
            else:
                marked = sum(len(n) for (m, n) in result_marks if m)
                suffixed = sum(len(n) for (s, n) in result_suffixes if s)
                self.subtitle.setText(
                    f"{len(labels)} glyphs: {marked} marked in {sum(1 for (m, _) in result_marks if m)} colours, {suffixed} with a suffix in {sum(1 for (s, _) in result_suffixes if s)} sets. Click a row to select those glyphs."
                )
            self.fill(self.mark_table, result_marks, mark_label, swatch)
            self.fill(self.suffix_table, result_suffixes, lambda s: s or "(no suffix)")
            self.status.setText("")
            self.marks = result_marks
            self.suffixes = result_suffixes
            self.package_id = package.id
        except Exception:
            self.package_id = None
            self.marks = []
            self.suffixes = []
            self.mark_table.setRowCount(0)
            self.suffix_table.setRowCount(0)
            raise

    def select_group(self, groups: Any, row: Any) -> None:
        """Select a mark or suffix group, optionally preserving current selection."""
        if self.package_id is None:
            raise ValueError("Refresh the report before selecting glyphs.")
        package = current_package()
        if package is None or package.id != self.package_id:
            raise ValueError("stale font: Refresh the report.")
        if not 0 <= row < len(groups):
            return
        (key, names) = groups[row]
        selected = select_glyphs(
            list(
                dict.fromkeys(
                    (selected_names() if self.add.isChecked() else []) + list(names)
                )
            ),
            package_id=self.package_id,
        )
        self.last_result = {"group": key, "selected": selected}
        self.status.setText(
            f"Selected {len(selected)} glyph{('s' if len(selected) != 1 else '')}"
        )

    def closeEvent(self, event: Any) -> None:
        """Disconnect owned signals and release this modeless window."""
        for signal, slot in self._connections:
            with contextlib.suppress(Exception):
                signal.disconnect(slot)
        self._connections = []
        getattr(sys, "_fontlab_samples", {}).pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)


def main() -> Any:
    """Replace the previous owned report window and show a modeless instance."""
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = LabelStatistics(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
