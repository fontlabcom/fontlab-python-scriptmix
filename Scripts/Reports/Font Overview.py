# this_file: Scripts/Reports/Font Overview.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Reports · Font Overview
"""A one-screen dashboard of the current font: glyphs, encoding, masters, kerning, composites.

What it does:
    Cards show glyph and code point counts, composites, glyphs without
    outlines on the current master, marks and notes; the table lists each
    master's vertical metrics and kerning pair count. Click Refresh after
    editing. Nothing in the font changes.

How it works:
    Count glyph encodings, composites, empty current-master drawings, marks
    and notes. Read each master's vertical metrics and explicit kerning-pair
    count for the table.

Why this design:
    Cards give a compact census, while the master rows keep family-specific
    metrics visible beside it.

How to use:
    Run Reports > Font Overview with a font open. Inspect the cards and master
    rows; press Refresh after edits or a font change to obtain a new report.

Benefit:
    Review the reported font inventory without modifying outlines, labels,
    metrics or kerning.
"""

from collections.abc import Callable
from typing import Any

from fly import ap, qt
from fly.ap.scripting import current_package

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Font Overview"
KEY = "report_font_overview"


# ---------------------------------------------------------------- font access


def component_names(layer: Any) -> list[str]:
    """Base glyph names of the layer's components."""
    names = []
    for shape in layer.shapes:
        base = shape.shapeData.componentGlyph if shape.shapeData is not None else ""
        if base:
            names.append(base)
    return names


# ---------------------------------------------------------------- core
def overview(package: Any) -> tuple[dict[str, int], list[tuple]]:
    """{card: value} and [(master, ascender, caps, x-height, descender, kerning pairs)]."""
    font = fontlab.CurrentFont()
    glyphs = list(font.glyphs)
    masters = list(package.masters)
    current = package.master
    codes = [code for glyph in glyphs for code in glyph.unicodes]
    composites = empty = marked = notes = 0
    for fg in glyphs:
        glyph = package.findName(fg.name)
        if glyph is None:
            continue
        layers = [glyph.findLayer(m) for m in masters]
        layers = [layer for layer in layers if layer is not None]
        if any(component_names(layer) for layer in layers):
            composites += 1
        layer = glyph.findLayer(current)
        if layer is not None and not layer.getContours() and not component_names(layer):
            empty += 1
        marked += 1 if int(glyph.mark or 0) else 0
        notes += 1 if (glyph.note or "").strip() else 0
    cards = {
        "Glyphs": len(glyphs),
        "Encoded glyphs": sum(1 for g in glyphs if list(g.unicodes)),
        "Code points": len(set(codes)),
        "Masters": len(masters),
        "Composites": composites,
        f"Empty on {current}": empty,
        "Marked": marked,
        "With notes": notes,
    }
    rows = []
    for master in masters:
        metrics = fontlab.FontMetrics(package, master)
        rows.append(
            (
                master,
                metrics.ascender,
                metrics.capsHeight,
                metrics.xHeight,
                metrics.descender,
                len(package.kerning(master)),
            ),
        )
    return cards, rows


# ---------------------------------------------------------------- GUI
def muted(widget: Any) -> str:
    """Return a translucent text colour matching the current native palette."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Overview(QtGui.QDialog):
    def __init__(self, parent: Any = None) -> None:
        """Build the modeless report with native Qt controls and guarded signals."""
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(600)
        self._connections = []
        self.cards, self.rows = {}, []

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

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)
        root.addLayout(self.grid)
        self.card_values = {}

        self.table = QtGui.QTableWidget(0, 6)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setHorizontalHeaderLabels(
            ["Master", "Ascender", "Caps", "x-height", "Descender", "Kern pairs"],
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(140)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.refresh_button = QtGui.QPushButton("Refresh")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.refresh_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        self._connect(self.refresh_button.clicked, lambda *a: self.refresh())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _connect(self, signal: Any, slot: Callable[..., Any]) -> None:
        """Connect through the shared guarded native lifecycle."""
        ap.scripting.connect_guarded(self, signal, slot)

    def card(self, index: int, label: str) -> None:
        """Build a dashboard card for one count in the overview grid."""
        frame = QtGui.QFrame()
        frame.setObjectName("card")
        base = self.palette.color(QtGui.QPalette.Base).name()
        border = self.palette.color(QtGui.QPalette.Mid).name()
        frame.setStyleSheet(
            f"QFrame#card {{ background: {base}; border: 1px solid {border}; border-radius: 8px; }}",
        )
        box = QtGui.QVBoxLayout(frame)
        box.setContentsMargins(12, 10, 12, 10)
        box.setSpacing(2)
        value = QtGui.QLabel("–")
        big = value.font
        big.setPointSizeF(big.pointSizeF() * 1.7)
        big.setBold(True)
        value.setFont(big)
        value.setStyleSheet(
            f"color: {self.palette.color(QtGui.QPalette.Link).name()}; border: none;",
        )
        caption = QtGui.QLabel(label)
        caption.setStyleSheet(f"color: {muted(self)}; border: none;")
        box.addWidget(value)
        box.addWidget(caption)
        self.grid.addWidget(frame, index // 4, index % 4)
        self.card_values[label] = value

    def refresh(self) -> None:
        """Refresh metrics and clear stale results when no font is open."""
        package = current_package()
        if package is None:
            self.rows = []
            self.package_id = None
            self.table.setRowCount(0)
            self.status.setText("No font open.")
            self.cards = {}
            for value in self.card_values.values():
                value.setText("–")
            self.subtitle.setText("Open a font first.")
            return
        self.cards, self.rows = overview(package)
        if set(self.cards) != set(self.card_values):
            while self.grid.count():
                item = self.grid.takeAt(0)
                if item.widget() is not None:
                    item.widget().deleteLater()
            self.card_values = {}
            for index, label in enumerate(self.cards):
                self.card(index, label)
        for label, value in self.cards.items():
            self.card_values[label].setText(f"{value:,}")
        family = package.info.familyName
        self.subtitle.setText(
            f"{family} · {int(package.upm)} units per em · current master {package.master}",
        )
        self.table.setRowCount(len(self.rows))
        for row, values in enumerate(self.rows):
            for column, value in enumerate(values):
                text = value if column == 0 else f"{value:g}"
                item = QtGui.QTableWidgetItem(text)
                if column:
                    item.setTextAlignment(
                        int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter),
                    )
                self.table.setItem(row, column, item)
        self.status.setText(
            "Composites: a component on any master. Empty: no contours and no components.",
        )

    def closeEvent(self, event: Any) -> None:
        """Release the owned report and its connections."""
        ap.scripting.close_script_dialog(self, event, KEY)


def main() -> Overview:
    """Show the persistent modeless report."""
    return ap.scripting.show_script_dialog(Overview, KEY)


if __name__ == "__main__":
    main()
