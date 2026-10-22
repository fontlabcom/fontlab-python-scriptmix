# this_file: Scripts/Names/Character Info.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from Apache-2.0 FontLab samples; provenance in migration.json.
# FLM: Names · Character Info
"""A live panel describing the character of the glyph selected in the Font window.

What it does:
    Shows the outline next to the system font's rendering, the code point, the
    Unicode name and category (Python's unicodedata), case counterpart,
    decomposition and the UTF-8/UTF-16 encodings. It follows the selection
    twice a second; nothing in the font changes.

How it works:
    Describe the selected glyph's encoded character with Python Unicode data.
    Draw its current outline beside a system-font character and refresh from
    the live selection.

Why this design:
    The separate renderings distinguish character identity from the font's own
    drawing without treating the system glyph as a design target.

How to use:
    Run Names > Character Info. Select an encoded glyph in the Font window,
    inspect its code point and encodings and use Copy to copy the current
    character.

Benefit:
    Check Unicode identity, case and decomposition while leaving the glyph's
    encoding unchanged.
"""

import unicodedata
from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    names_dialog_type,
    names_muted,
    names_selected_names,
    names_snapshot_refresh,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Character Info"
KEY = "names_character_info"
POLL_MS = 500
CATEGORIES = {
    "Lu": "Letter, uppercase",
    "Ll": "Letter, lowercase",
    "Lt": "Letter, titlecase",
    "Lm": "Letter, modifier",
    "Lo": "Letter, other",
    "Mn": "Mark, nonspacing",
    "Mc": "Mark, spacing",
    "Me": "Mark, enclosing",
    "Nd": "Number, decimal",
    "Nl": "Number, letter",
    "No": "Number, other",
    "Pc": "Punctuation, connector",
    "Pd": "Punctuation, dash",
    "Ps": "Punctuation, open",
    "Pe": "Punctuation, close",
    "Pi": "Punctuation, initial",
    "Pf": "Punctuation, final",
    "Po": "Punctuation, other",
    "Sm": "Symbol, math",
    "Sc": "Symbol, currency",
    "Sk": "Symbol, modifier",
    "So": "Symbol, other",
    "Zs": "Separator, space",
    "Cc": "Control",
    "Cf": "Format",
    "Co": "Private use",
    "Cn": "Unassigned",
}
FIELDS = [
    "Glyph",
    "Code point",
    "Unicode name",
    "Category",
    "Case pair",
    "Decomposition",
    "UTF-8",
    "UTF-16",
    "Escape",
]


# ---------------------------------------------------------------- font access
def current_package() -> Any | None:
    """Read current native font state without changing font data."""
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def focused_name() -> str | None:
    """Read current font state through the shared Names access helper."""
    return next(iter(names_selected_names()), None)


def layer_path(layer: Any) -> Any:
    """The layer's outline as one QPainterPath in font units (y up), components placed."""
    path = QtGui.QPainterPath()
    path.setFillRule(QtCore.Qt.WindingFill)
    for shape in layer.shapes:
        for part in (shape.closedPath, shape.openedPath):
            if part is not None and not part.isEmpty():
                path.addPath(shape.transform.map(part))
    return path


# ---------------------------------------------------------------- core
def describe(code: int) -> dict[str, str]:
    """{field: text} for one code point (pure Python, no font access)."""
    char = chr(code)
    category = unicodedata.category(char)
    upper, lower = char.upper(), char.lower()
    pair = lower if char != lower else upper if char != upper else ""
    utf16 = char.encode("utf-16-be")
    return {
        "Code point": f"U+{code:04X}",
        "Unicode name": unicodedata.name(char, "(no name)"),
        "Category": f"{category} · {CATEGORIES.get(category, '')}",
        "Case pair": " ".join(f"{c} U+{ord(c):04X}" for c in pair) if pair else "–",
        "Decomposition": unicodedata.decomposition(char) or "–",
        "UTF-8": " ".join(f"{b:02X}" for b in char.encode("utf-8")),
        "UTF-16": " ".join(
            utf16[i : i + 2].hex().upper() for i in range(0, len(utf16), 2)
        ),
        "Escape": f"\\u{code:04x}" if code <= 0xFFFF else f"\\U{code:08x}",
    }


# ---------------------------------------------------------------- GUI
muted = names_muted


class Specimen(QtGui.QWidget):
    """Custom painter: the glyph outline (left) and the system font's character (right)."""

    def __init__(self, parent: Any = None) -> None:
        """Build original controls; refresh once and retain only owned resources."""
        QtGui.QWidget.__init__(self, parent)
        self.paint_error = ""
        self.on_error = None  # dialog hook: show drawing errors in the status label
        self.setMinimumHeight(150)
        self.path, self.advance, self.char = None, 0, ""
        self.frame = (-250, 750)

    def set_content(
        self, path: Any, advance: float, char: str, frame: tuple[float, float]
    ) -> None:
        """Replace proof outline, advance, character and vertical frame."""
        self.path, self.advance, self.char, self.frame = path, advance, char, frame
        self.update()

    def paintEvent(self, event: Any) -> None:
        """Draw the proof; contain native painter errors and always end painting."""
        painter = QtGui.QPainter(self)
        try:
            self.draw(painter)
            self.paint_error = ""
        except Exception as error:  # noqa: BLE001 - contain native painter failures
            self.paint_error = repr(error)
            if self.on_error is not None:
                try:
                    self.on_error(self.paint_error)
                except Exception as hook_error:  # noqa: BLE001 - contain error hook
                    self.paint_error += f"; error hook: {hook_error!r}"
        finally:
            painter.end()

    def draw(self, painter: Any) -> None:
        """Fit the full outline and metric frame inside the padded left proof.

        Include overhangs and tall accents in both-axis fitting; retain the
        baseline, labels and independent system-font proof on the right.
        """
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        text = QtGui.QColor(self.palette.color(QtGui.QPalette.Text))
        faint = QtGui.QColor(text)
        faint.setAlpha(35)
        soft = QtGui.QColor(text)
        soft.setAlpha(120)
        half = self.width / 2.0
        height = self.height
        painter.setPen(QtGui.QPen(QtGui.QBrush(faint), 1.0))
        painter.drawRoundedRect(QtCore.QRectF(0.5, 0.5, half - 6, height - 1), 8, 8)
        painter.drawRoundedRect(
            QtCore.QRectF(half + 6, 0.5, half - 6.5, height - 1),
            8,
            8,
        )
        small = QtGui.QFont(painter.font())
        small.setPointSizeF(max(8.0, small.pointSizeF() * 0.85))
        painter.setFont(small)
        painter.setPen(soft)
        painter.drawText(
            QtCore.QRectF(8, height - 22, half - 20, 18),
            int(QtCore.Qt.AlignLeft),
            "Font outline",
        )
        painter.drawText(
            QtCore.QRectF(half + 14, height - 22, half - 20, 18),
            int(QtCore.Qt.AlignLeft),
            "System font",
        )
        descender, ascender = self.frame
        if self.path is not None:
            bounds = self.path.boundingRect()
            left = min(0.0, self.advance, bounds.left())
            right = max(0.0, self.advance, bounds.right())
            bottom = min(0.0, descender, bounds.top())
            top = max(0.0, ascender, bounds.bottom())
            proof_width, proof_height = half - 22, height - 38
            scale = min(
                proof_width / max(1.0, right - left),
                proof_height / max(1.0, top - bottom),
            )
            origin = 8 + (proof_width - (right - left) * scale) / 2 - left * scale
            baseline = 8 + (proof_height - (top - bottom) * scale) / 2 + top * scale
            painter.setPen(QtGui.QPen(QtGui.QBrush(faint), 1.0))
            painter.drawLine(
                QtCore.QPointF(8, baseline),
                QtCore.QPointF(half - 14, baseline),
            )
            painter.save()
            painter.translate(origin, baseline)
            painter.scale(scale, 0 - scale)
            painter.fillPath(self.path, QtGui.QBrush(text))
            painter.restore()
        if self.char:
            big = QtGui.QFont(painter.font())
            big.setPixelSize(int(height * 0.55))
            painter.setFont(big)
            painter.setPen(text)
            painter.drawText(
                QtCore.QRectF(half + 6, 0, half - 6, height - 18),
                int(QtCore.Qt.AlignCenter),
                self.char,
            )


class CharacterInfo(names_dialog_type()):
    def __init__(self, parent: Any = None) -> None:
        """Build original controls; refresh once and retain only owned resources."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(480)
        self.shown_name = None
        root = self.root

        self.specimen = Specimen()
        root.addWidget(self.specimen)

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(6)
        self.fields = {}
        for row, label in enumerate(FIELDS):
            caption = QtGui.QLabel(label)
            caption.setStyleSheet(f"color: {muted(self)};")
            value = QtGui.QLabel("–")
            value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            value.setWordWrap(True)
            caption.setAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop))
            form.addWidget(caption, row, 0)
            form.addWidget(value, row, 1)
            self.fields[label] = value
        form.setColumnStretch(1, 1)
        root.addLayout(form)
        self.others = QtGui.QLabel()
        self.others.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.others)
        root.addStretch(1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.specimen.on_error = lambda text: self.status.setText(
            "Drawing failed: " + text,
        )
        self.copy_button = QtGui.QPushButton("Copy character")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.copy_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(POLL_MS)
        self._connect(self.timer.timeout, lambda *a: self.poll())
        self._connect(self.copy_button.clicked, lambda *a: self.copy())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()
        self.timer.start()

    def poll(self) -> None:
        """Refresh at each timer tick, including font and master switches."""
        self.refresh()

    @names_snapshot_refresh
    def refresh(self, name: str | None = None) -> None:
        """Read current font data; update original fields and action availability."""
        package = current_package()
        name = name or (focused_name() if package else None)
        self.shown_name = name
        glyph = package.findName(name) if package and name else None
        self.current = {}
        if glyph is None:
            self.subtitle.setText(
                "Open a font and select a glyph in the Font window."
                if package is None
                else "Select a glyph in the Font window.",
            )
            for value in self.fields.values():
                value.setText("–")
            self.specimen.set_content(None, 0, "", (-250, 750))
            self.copy_button.setEnabled(False)
            return
        codes = list(glyph.fgGlyph.unicodes)
        layer = glyph.findLayer(package.master)
        path = layer_path(layer) if layer is not None else None
        char = chr(codes[0]) if codes else ""
        frame = (package.descender_value, package.ascender_value)
        self.specimen.set_content(
            path,
            layer.advanceWidth if layer is not None else 0,
            char,
            frame,
        )
        self.subtitle.setText(
            f"Follows the Font window selection · master {package.master}",
        )
        self.current = describe(codes[0]) if codes else {}
        self.current["Glyph"] = name
        for label, value in self.fields.items():
            value.setText(
                self.current.get(
                    label,
                    "– (unencoded)" if label == "Code point" else "–",
                ),
            )
        self.others.setText(
            "Also encoded: " + ", ".join(f"U+{c:04X}" for c in codes[1:])
            if len(codes) > 1
            else "",
        )
        self.copy_button.setEnabled(bool(char))
        self.status.setText(
            f"{name} · {len(codes)} code point{'s' if len(codes) != 1 else ''}",
        )

    def copy(self) -> None:
        """Copy the current encoded character from a valid live snapshot."""
        self.ensure_snapshot()
        if self.specimen.char:
            QtGui.QApplication.clipboard().setText(self.specimen.char)
            self.status.setText(f"Copied {self.specimen.char}")


def main() -> Any:
    """Open or replace this owned modeless Names panel."""
    return show_script_dialog(CharacterInfo, KEY)


if __name__ == "__main__":
    main()
