# this_file: Scripts/Features/Alternate Preview.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Features · Alternate Preview
"""Compare a base glyph and its suffixed alternates in each master. Read-only; outlines share one scale per row.

What it does:
    Run with a font active. All original controls use the shared fly panel lifecycle.
    Feature data is font-wide; reopen after switching fonts or changing source.

How it works:
    Match the complete base-plus-dot prefix, then draw existing alternates
    with their transformed outlines. Each master row uses a common scale for
    comparison.

Why this design:
    Naming identifies candidate alternates without claiming that a feature
    rule selects them during shaping.

How to use:
    Run Features > Alternate Preview. Enter an existing base name, choose the
    master scope and scroll through all displayed rows. Reopen after changing
    the bound font.

Benefit:
    Compare alternate proportions and master differences without generating a
    font or changing glyphs.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    features_dialog_type,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = (qt.QtCore, qt.QtGui)
FeaturesDialog = features_dialog_type()
TITLE = "Alternate Glyph Proof"
KEY = "features_alternate_preview"
SUBTITLE = "Compare a base glyph and its suffixed alternates in each master. Read-only; outlines share one scale per row."
ACTION = "Refresh proof"


def layer_path(layer: Any) -> Any:
    """The layer's outline as one QPainterPath in font units (y up), components placed."""
    path = QtGui.QPainterPath()
    path.setFillRule(QtCore.Qt.WindingFill)
    for shape in layer.shapes:
        for part in (shape.closedPath, shape.openedPath):
            if part is not None and (not part.isEmpty()):
                path.addPath(shape.transform.map(part))
    return path


def run(names: list[str], base: str) -> list[str]:
    """Return the existing base first, followed by sorted dot-suffixed alternates.

    Match complete base-plus-dot prefixes so a and a-cy remain distinct.
    Input names come from the active font; this does not inspect feature rules
    or imply the alternates participate in shaping.
    """
    return ([base] if base in names else []) + sorted(
        name for name in names if name.startswith(base + ".")
    )


class Proof(QtGui.QWidget):
    def __init__(self, owner: Any) -> None:
        """Initialize this owned tool and preserve its original controls."""
        QtGui.QWidget.__init__(self, owner)
        self.owner = owner
        self._error = ""

    def paintEvent(self, event: Any) -> None:
        """Contain painting errors and always release the active painter."""
        painter = QtGui.QPainter(self)
        try:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            self.draw_proof(painter)
        except Exception as error:  # noqa: BLE001 - contain native painter failures
            self._error = str(error)
            self.owner.status.setText("Proof error: " + self._error)
        finally:
            painter.end()

    def draw_proof(self, painter: Any) -> None:
        """Paint each master row with one scale and wrapped alternate columns."""
        owner = self.owner
        names = getattr(owner, "preview_names", [])
        masters = getattr(owner, "chosen_masters", [])
        text_color = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        painter.setPen(text_color)
        if not names:
            painter.drawText(
                20, 45, "Enter an existing base glyph name to see its alternates."
            )
            return
        owner.ensure_font()
        columns = max(1, int(self.width / 150))
        strips = (len(names) + columns - 1) // columns
        cell_width = self.width / min(columns, len(names))
        for master_index, master in enumerate(masters):
            layers = []
            for name in names:
                glyph = owner.package.findName(name)
                layer = glyph.findLayer(master) if glyph is not None else None
                layers.append(
                    layer if layer is not None and (not layer.isNull) else None
                )
            boxes = [layer.boundingBox for layer in layers if layer is not None]
            low = min([box.y() for box in boxes] + [0])
            high = max([box.y() + box.height() for box in boxes] + [1])
            widest = max([box.width() for box in boxes] + [1])
            scale = min((cell_width - 24) / max(1, widest), 130 / max(1, high - low))
            for index, (name, layer) in enumerate(zip(names, layers, strict=False)):
                x = index % columns * cell_width
                y = (master_index * strips + index // columns) * 200
                painter.setPen(text_color)
                painter.drawText(int(x + 10), int(y + 18), master)
                label = QtGui.QFontMetrics(self.font).elidedText(
                    name, QtCore.Qt.ElideRight, int(cell_width - 20)
                )
                painter.drawText(int(x + 10), int(y + 190), label)
                if layer is None:
                    painter.drawText(int(x + 10), int(y + 90), "Missing layer")
                    continue
                path = layer_path(layer)
                box = layer.boundingBox
                transform = QtGui.QTransform(
                    scale,
                    0,
                    0,
                    -scale,
                    x + (cell_width - box.width() * scale) / 2 - box.x() * scale,
                    y + 35 + high * scale,
                )
                painter.fillPath(transform.map(path), QtGui.QBrush(text_color))


class Dialog(FeaturesDialog):
    def __init__(self, parent: Any = None) -> None:
        """Initialize this owned tool and preserve its original controls."""
        super().__init__(parent, title=TITLE, subtitle=SUBTITLE, key=KEY)

    def setup(self) -> None:
        """Build the original controls inside the shared owned panel."""
        root = self.prepare()
        self.apply_button.setText(ACTION)
        form = QtGui.QGridLayout()
        self.base = QtGui.QLineEdit("a")
        glyph = fontlab.CurrentGlyph() if self.package else None
        if glyph is not None:
            self.base.setText(glyph.name.split(".", 1)[0])
        self.scope = QtGui.QComboBox()
        self.masters = list(self.package.masters) if self.package else []
        self.scope.addItem(
            "Current master (" + (self.package.master if self.package else "none") + ")"
        )
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Base glyph"), 0, 0)
        form.addWidget(self.base, 0, 1)
        form.addWidget(QtGui.QLabel("Masters"), 1, 0)
        form.addWidget(self.scope, 1, 1)
        root.addLayout(form)
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.canvas = Proof(self)
        self.scroll_area.setWidget(self.canvas)
        root.addWidget(self.scroll_area, 1)
        self._connect(self.base.textChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())

    def refresh(self) -> None:
        """Rebuild the complete visible preview; invalidate it on failure."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self.package is not None:
            self.ensure_font()
        self.preview_names = (
            run(self.names, self.base.text.strip()) if self.base.text.strip() else []
        )
        self.chosen_masters = (
            ([self.package.master] if self.scope.currentIndex == 0 else self.masters)
            if self.package
            else []
        )
        columns = max(1, int(self.scroll_area.viewport().width / 150))
        strips = max(1, (len(self.preview_names) + columns - 1) // columns)
        self.canvas.setMinimumHeight(max(260, len(self.chosen_masters) * strips * 200))
        self.canvas._error = ""
        self.canvas.update()
        self.apply_button.setEnabled(bool(self.preview_names))
        self.status.setText(
            f"{len(self.preview_names)} glyphs × {len(self.chosen_masters)} masters · scroll to see every row"
        )
        self._preview_valid = True

    def apply(self) -> None:
        """Perform the selected original tool action on its valid preview."""
        self.ensure_preview()
        self.refresh()
        self.last_result = {"names": self.preview_names, "masters": self.chosen_masters}


def main() -> Any:
    """Replace this tool through the shared owned-window registry."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
