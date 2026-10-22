# this_file: Scripts/Metrics/Italic Sidebearings.py
# SPDX-License-Identifier: Apache-2.0
"""Report and set sidebearings along the italic angle.

What it does: shows two pairs of sidebearings for each layer. The plain pair
is the distance from the advance edge to the ink, measured sideways. The
italic pair is measured after the outline is de-slanted by the italic angle.
You can add to the italic values or set them.

How it works: the script maps the outline through a shear around the height
"measured at" (half of the x-height by default). The sheared outline gives
the italic edges. A change moves the real outline sideways and changes the
advance. Anchors move with the outline. All values are whole units.

Why: in a slanted design the plain sidebearings depend on the overhang of the
slant. The italic sidebearings let you compare and space an italic "n" and
"o" as if they were upright.

How to use: select glyphs in the Font window. Check the angle and the height.
Choose "Add" or "Set". Tick LSB and RSB and enter the values. Choose the
current master or all masters. Check the table. Press Apply. The panel stays
open. Press "Use selection" to read the Font window selection again.

Safety: each Apply is recorded as one Undo step. Auto layers are listed and never edited. A
glyph that owns an auto layer is listed and skipped as a whole. Layers with a
metrics link or expression are listed and skipped. A base of auto glyphs is
refused, because FontLab rebuilds the auto glyphs and may lose their anchors
and locks (FontLab issue 8512). This includes a base that reaches an auto
glyph through other composites. Tick "Edit bases of auto glyphs anyway" to go
on. Apply is refused while FontLab has pending glyph updates. After the write
the script reads advance and outline back and reports any mismatch. A failure
after the write started says so and asks you to use Edit > Undo. It does not
call UpdateAll (FontLab issue 8537).

Shared parts: the panel, the plan model, the one-step write and the read-back
come from the App module fly.ap.metrics_panel. This script holds its own
maths, its planner and its controls.

Benefit: you space italics with the same method as upright designs.

Credit: adapted from the author's own rescued FontLab sample
metrics_italic_sidebearings.py (Apache-2.0).
"""

import math
from typing import Any

import fly.ap.metrics_panel as metrics_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap.scripting import current_package, show_script_dialog

QtCore, QtGui = qt.QtCore, qt.QtGui
MetricsPanel = metrics_panel.panel_type()

MODES = [("Add to italic sidebearings", "add"), ("Set italic sidebearings to", "set")]
X_HEIGHT_FALLBACK = 500  # Used when the font has no x-height value.


# ---------------------------------------------------------------- core
def outline(layer: Any) -> Any:
    """The layer outline as one QPainterPath, with component transforms applied."""
    path = QtGui.QPainterPath()
    for shape in layer.shapes:
        part = QtGui.QPainterPath()
        for contour in shape.getContours():
            part.addPath(contour.path())
        path.addPath(shape.transform.map(part))
    return path


def deslant(angle: float, pivot: float) -> Any:
    """QTransform that removes a slant of angle degrees around the height pivot.

    The sign follows FontLab: a right-leaning design has a negative angle.
    """
    slope = math.tan(math.radians(angle))
    return QtGui.QTransform(1, 0, slope, 1, -pivot * slope, 0)


def italic_edges(layer: Any, angle: float, pivot: float) -> tuple[float, float] | None:
    """Italic left and right edge of the ink, or None for an empty layer."""
    path = outline(layer)
    if path.isEmpty():
        return None
    box = deslant(angle, pivot).map(path).boundingRect()
    return box.x(), box.x() + box.width()


def italic_planner(
    angle: float,
    pivot: float,
    mode: str,
    lsb_value: int | None,
    rsb_value: int | None,
) -> metrics_panel.Planner:
    """Return the planner. A value of None leaves that side as it is."""

    def plan(layer: Any, master: str) -> metrics_panel.LayerPlan | str:
        edges = italic_edges(layer, angle, pivot)
        if edges is None:
            return "empty (no outline)"
        width = layer.advanceWidth
        ilsb, irsb = edges[0], width - edges[1]
        new_ilsb, new_irsb = ilsb, irsb
        if lsb_value is not None:
            new_ilsb = ilsb + lsb_value if mode == "add" else lsb_value
        if rsb_value is not None:
            new_irsb = irsb + rsb_value if mode == "add" else rsb_value
        dx = metrics_panel.unit(new_ilsb - ilsb)
        new_width = metrics_panel.unit(width + dx + (new_irsb - irsb))
        if new_width < 0:
            return "negative width (skipped)"
        plain = metrics_panel.ink_edges(layer)
        shown_irsb = irsb + (new_width - width - dx)
        cells = (
            f"{metrics_panel.unit(plain[0])}",
            f"{metrics_panel.unit(width - plain[1])}",
            f"{metrics_panel.unit(ilsb)}",
            f"{metrics_panel.unit(irsb)}",
            f"{metrics_panel.unit(ilsb + dx)}",
            f"{metrics_panel.unit(shown_irsb)}",
        )
        return metrics_panel.make_plan(layer, dx, new_width, cells)

    return plan


# ---------------------------------------------------------------- panel
class ItalicSidebearings(MetricsPanel):
    """Italic sidebearings: angle, height, operation, values, masters."""

    TITLE = "Italic Sidebearings"
    KEY = "metrics_italic_sidebearings"
    HEADERS = ("LSB", "RSB", "Italic LSB", "Italic RSB", "New it. LSB", "New it. RSB")
    ACCENT = (5, 6)
    MIN_WIDTH = 660

    def build(self) -> None:
        """Create angle, height, operation and value controls."""
        package = current_package()
        angle = (
            float(getattr(package, "italicAngle_value", 0.0) or 0.0) if package else 0.0
        )
        x_height = (
            getattr(package, "xHeight_value", X_HEIGHT_FALLBACK) if package else 0
        )
        self.font_angle = angle
        self.angle = QtGui.QDoubleSpinBox()
        self.angle.setRange(-45.0, 45.0)
        self.angle.setDecimals(1)
        self.angle.setSuffix(" °")
        self.angle.setValue(angle)
        self.angle.setAlignment(QtCore.Qt.AlignRight)
        self.watch(self.angle.valueChanged)
        self.pivot = self.spin(
            -2000, 4000, metrics_panel.unit((x_height or X_HEIGHT_FALLBACK) / 2)
        )
        self.mode = QtGui.QComboBox()
        for label, _ in MODES:
            self.mode.addItem(label)
        self.watch(self.mode.currentIndexChanged)
        self.lsb_check = QtGui.QCheckBox("LSB")
        self.lsb_check.setChecked(True)
        self.rsb_check = QtGui.QCheckBox("RSB")
        self.rsb_check.setChecked(True)
        self.watch(self.lsb_check.toggled)
        self.watch(self.rsb_check.toggled)
        self.lsb = self.spin(-2000, 2000, 0)
        self.rsb = self.spin(-2000, 2000, 0)
        self.form.addWidget(QtGui.QLabel("Italic angle"), 1, 0)
        self.form.addWidget(self.angle, 1, 1)
        self.form.addWidget(QtGui.QLabel("Measured at y ="), 1, 2)
        self.form.addWidget(self.pivot, 1, 3)
        self.form.addWidget(QtGui.QLabel("Operation"), 2, 0)
        self.form.addWidget(self.mode, 2, 1, 1, 3)
        self.form.addWidget(self.lsb_check, 3, 0)
        self.form.addWidget(self.lsb, 3, 1)
        self.form.addWidget(self.rsb_check, 3, 2)
        self.form.addWidget(self.rsb, 3, 3)
        self.form.setColumnStretch(3, 1)

    def sync_controls(self) -> None:
        """Enable a value only when its box is ticked."""
        self.lsb.setEnabled(self.lsb_check.isChecked())
        self.rsb.setEnabled(self.rsb_check.isChecked())

    def subtitle_hint(self) -> str:
        """Describe the current settings."""
        count = len({e.glyph.name for e in self.entries})
        upright = (
            " The font angle is 0: italic values equal plain values."
            if not self.font_angle
            else ""
        )
        return (
            f"{count} glyph{'s' if count != 1 else ''} de-slanted at {self.angle.value:g} °"
            f" around y = {self.pivot.value}.{upright}"
        )

    def planner(self, package: Any, glyphs: list[Any]) -> metrics_panel.Planner:
        """Planner for the chosen angle, height, operation and values."""
        return italic_planner(
            self.angle.value,
            self.pivot.value,
            MODES[self.mode.currentIndex][1],
            self.lsb.value if self.lsb_check.isChecked() else None,
            self.rsb.value if self.rsb_check.isChecked() else None,
        )


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(ItalicSidebearings, ItalicSidebearings.KEY)


if __name__ == "__main__":
    main()
