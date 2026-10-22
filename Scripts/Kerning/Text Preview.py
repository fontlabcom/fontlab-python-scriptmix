# this_file: Scripts/Kerning/Text Preview.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Text Preview
"""Set text from the font's outlines with its kerning applied, per master, at any size.

What it does:
    Type text or /glyphname tokens, pick a master and drag the size slider; lines wrap to the
    window. Kerned gaps can be labelled with their values, and kerning can be switched off to see
    the raw spacing. FontLab resolves each pair, including class kerning. Nothing is edited.

How it works:
    Resolve text tokens to glyphs, cache transformed paths and ask FontLab for
    effective pair kerning on the chosen master. Wrap lines inside the proof
    window.

Why this design:
    Effective pair lookup includes class kerning, so the proof can compare
    resolved spacing with raw advances.

How to use:
    Run Kerning > Text Preview. Enter characters or slash-name tokens, choose
    a master and size, then toggle kerning and value labels to compare the
    spacing.

Benefit:
    Inspect the current outlines with effective kerning without exporting or
    editing the font.
"""

from typing import Any

from fly import ap, qt

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui
# The tiny facade stays lazy until a native menu script asks for its panel.
from fly.ap.scripting import (
    kerning_dialog_type,
)
from fly.ap.scripting import (
    kerning_layout as layout,
)
from fly.ap.scripting import (
    kerning_snapshot_refresh as snapshot_refresh,
)
from fly.ap.scripting import (
    names_muted as muted,
)

KerningDialog = kerning_dialog_type()

TITLE = "Kerning Text Preview"
KEY = "kerning_text_preview"
DEFAULT_TEXT = "AVATAR LTAVA Tyre WAVE /Aacute/V"
MARGIN = 18


# ---------------------------------------------------------------- core
def parse_text(text: str, package: Any) -> list[str]:
    """Glyph names for the text: characters by Unicode, '/name' tokens by name (ended by space or '/')."""
    names, i = [], 0
    while i < len(text):
        char = text[i]
        if char == "/":
            j = i + 1
            while j < len(text) and text[j] not in " /":
                j += 1
            token = text[i + 1 : j]
            if token and package.findName(token) is not None:
                names.append(token)
            i = j + (1 if j < len(text) and text[j] == " " else 0)
            continue
        glyph = package.findUnicode(ord(char))
        if glyph is not None:
            names.append(glyph.name)
        i += 1
    return names


def outline(layer: Any) -> Any:
    """The layer's outline as one QPainterPath, components placed by their transforms."""
    path = QtGui.QPainterPath()
    path.setFillRule(QtCore.Qt.WindingFill)
    for shape in layer.shapes:
        part = QtGui.QPainterPath()
        for contour in shape.getContours():
            part.addPath(contour.path())
        path.addPath(shape.transform.map(part))
    return path


# ---------------------------------------------------------------- GUI


class Canvas(QtGui.QWidget):
    """Paints the laid-out glyphs at the chosen size, wrapping lines to the widget width."""

    def __init__(self, owner: Any) -> None:
        """Initialize owned controls without changing the font."""
        QtGui.QWidget.__init__(self)
        self.paint_error = None
        self.owner = owner
        self.setMinimumSize(560, 260)

    def paintEvent(self, event: Any) -> None:
        """Contain every painter failure and always release the painter."""
        painter = None
        try:
            painter = QtGui.QPainter(self)
            self.draw(painter)
            self.paint_error = None
        except Exception as error:  # noqa: BLE001 - native paint boundary
            self.fail(error)
        finally:
            if painter is not None:
                try:
                    painter.end()
                except Exception as error:  # noqa: BLE001 - native cleanup boundary
                    self.fail(error)

    def fail(self, error: Exception) -> None:
        """Contain failures even when invalidating the owner or its status fails."""
        self.paint_error = repr(error)
        try:
            self.owner.invalidate()
            self.owner.status.setText("Proof error: " + self.paint_error)
        except Exception:  # noqa: BLE001 - error hooks cannot escape PythonQt
            self.error_hook_failed = True

    def draw(self, painter: Any) -> None:
        """Draw every fitted font outline and optional effective-kerning label."""
        owner = self.owner
        palette = self.palette
        painter.fillRect(self.rect, palette.color(QtGui.QPalette.Base))
        if owner.rows:
            owner.ensure_snapshot()
        rows = owner.rows
        if not rows:
            painter.setPen(QtGui.QColor(muted(self)))
            painter.drawText(
                self.rect,
                int(QtCore.Qt.AlignCenter),
                owner.empty_message(),
            )
            return
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        scale = owner.size_slider.value / owner.upm
        values = owner.show_values.isChecked()
        ink = QtGui.QColor(palette.color(QtGui.QPalette.WindowText))
        accent = QtGui.QColor(palette.color(QtGui.QPalette.Link))
        small = painter.font()
        small.setPointSizeF(max(small.pointSizeF() * 0.8, 8))
        painter.setFont(small)
        bounds = {}
        for name, *_ in rows:
            box = owner.path(name).boundingRect()
            bounds[name] = (box.left(), box.top(), box.right(), box.bottom())
        scale, positions = ap.scripting.kerning_proof_geometry(
            rows,
            bounds,
            self.width - 2 * MARGIN,
            self.height - 2 * MARGIN,
            scale,
            owner.ascender,
            owner.descender,
            values,
        )
        label_scale = scale / (owner.size_slider.value / owner.upm)
        small.setPointSizeF(max(0.1, small.pointSizeF() * label_scale))
        painter.setFont(small)
        for name, left, baseline, kern in positions:
            left, baseline = left + MARGIN, baseline + MARGIN
            if kern and values:
                painter.setPen(accent)
                painter.drawText(
                    QtCore.QRectF(
                        left - 20 * label_scale,
                        baseline - owner.descender * scale + 2 * label_scale,
                        40 * label_scale,
                        16 * label_scale,
                    ),
                    int(QtCore.Qt.AlignCenter),
                    f"{kern:g}",
                )
            painter.save()
            painter.translate(left, baseline)
            painter.scale(scale, -scale)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(ink))
            painter.drawPath(owner.path(name))
            painter.restore()


class TextPreview(KerningDialog):
    """Retain the original Text Preview controls on the shared owned panel."""

    def __init__(self, parent: Any = None) -> None:
        """Initialize owned controls without changing the font."""
        KerningDialog.__init__(self, parent, TITLE, KEY)

        self.upm = self.package.upm if self.package else 1000
        self.ascender = self.package.ascender_value if self.package else 800
        self.descender = self.package.descender_value if self.package else -200
        self.rows, self.paths = [], {}
        root = self.root

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.text = QtGui.QLineEdit(DEFAULT_TEXT)
        self.text.setPlaceholderText("Text, or /glyphname tokens")
        self.master = QtGui.QComboBox()
        for name in self.masters:
            self.master.addItem(name)
        if self.current_master in self.masters:
            self.master.setCurrentIndex(self.masters.index(self.current_master))
        self.size_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.size_slider.setRange(16, 240)
        self.size_slider.setValue(72)
        self.size_label = QtGui.QLabel()
        self.kerned = QtGui.QCheckBox("Kerning")
        self.kerned.setChecked(True)
        self.show_values = QtGui.QCheckBox("Show values")
        self.show_values.setChecked(True)
        form.addWidget(QtGui.QLabel("Text"), 0, 0)
        form.addWidget(self.text, 0, 1, 1, 4)
        form.addWidget(QtGui.QLabel("Master"), 1, 0)
        form.addWidget(self.master, 1, 1)
        form.addWidget(self.kerned, 1, 2)
        form.addWidget(self.show_values, 1, 3)
        form.addWidget(QtGui.QLabel("Size"), 2, 0)
        form.addWidget(self.size_slider, 2, 1, 1, 3)
        form.addWidget(self.size_label, 2, 4)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.canvas = Canvas(self)
        root.addWidget(self.canvas, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setDefault(True)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        self._connect(self.text.textChanged, lambda *a: self.refresh())
        self._connect(self.master.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.kerned.toggled, lambda *a: self.refresh())
        self._connect(self.show_values.toggled, lambda *a: self.canvas.update())
        self._connect(self.size_slider.valueChanged, lambda *a: self.resized())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.resized()
        self.refresh()

    def chosen_master(self) -> str:
        """Return the master named by the original combo box."""
        return self.masters[self.master.currentIndex] if self.masters else ""

    def path(self, name: str) -> Any:
        """Cache the actual transformed outline on the requested master."""
        key = (name, self.chosen_master())
        if key not in self.paths:
            self.paths[key] = outline(self.package.findName(name).findLayer(key[1]))
        return self.paths[key]

    def empty_message(self) -> str:
        """Prompt for a font or text when the outline proof has no glyph rows."""
        return "Open a font first." if self.package is None else "Type some text above."

    def resized(self) -> None:
        """Update the size label and request a proof repaint."""
        self.size_label.setText(f"{self.size_slider.value} px")
        self.canvas.update()

    @snapshot_refresh
    def refresh(self) -> None:
        """Read and render a complete native snapshot for the chosen controls."""
        self.paths = {}
        if self.package is None:
            self.rows = []
            self.subtitle.setText("Open a font first.")
        else:
            names = parse_text(self.text.text, self.package)
            self.rows = layout(
                self.package,
                names,
                self.chosen_master(),
                self.kerned.isChecked(),
            )
            self.subtitle.setText(
                f"{self.chosen_master()} master · glyph outlines with "
                f"{'kerning applied' if self.kerned.isChecked() else 'kerning off'}",
            )
        for name, *_ in self.rows:
            self.path(name)  # Materialize every outline before publishing the snapshot.
        kerned = [r for r in self.rows if r[3]]
        total = sum(r[3] for r in kerned)
        self.status.setText(
            f"{len(self.rows)} glyphs · {len(kerned)} kerned gaps, {total:g} units in total",
        )
        self.canvas.update()


def main() -> Any:
    """Replace the original registry window and show this owned modeless panel."""
    return ap.scripting.show_script_dialog(TextPreview, KEY)


if __name__ == "__main__":
    main()
