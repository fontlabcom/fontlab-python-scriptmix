# this_file: Scripts/Anchors/Center Horizontally.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Center Horizontally
"""Put named anchors on the horizontal centre of the advance or of the ink box.

What: Moves the named anchors sideways. A slider sets the target between the
left edge (0 %) and the right edge (100 %) of the advance width or of
the ink box. The y value never changes.

How: With an italic angle the target is a slanted line. For the advance it
passes through the baseline point; for the ink box it passes through the
centre of the box. So a top anchor of an italic glyph moves right as its
height grows. FontLab angle convention: a negative angle leans right.
Example: advance 500, centre, angle -10 degrees, y 700: x = 373.

Why: One rule for upright and italic glyphs. The panel starts with the font
italic angle of the current master and lets you override it. Reload
selection keeps your value. With all masters, one angle serves every
master and the panel says so.

Use: Select glyphs. Run the script. Type the anchor names. Choose advance or
ink box. Move the slider. Check the table. Press Centre.

Benefit: Mark anchors sit on the optical centre in every master, in one step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- an existing anchor would move to 0, 0 (FontLab cannot Redo that);
- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- several anchors on a layer share a name (the edit is ambiguous);

After the write, the script reads every value back. It reports any value
that FontLab did not keep, for example under a strong rounding preference.
If FontLab fails part-way, the error says that native changes may remain.
The edit is recorded as one Undo step. The plan, the safety checks, the
one-step
write and the panel base are shared with the other anchor scripts
(fly.ap.anchor_writer, fly.ap.anchor_panel); the planner and the controls
belong to this script.

Source: the author's own FontLab sample
anchors_center_horizontally.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

import math
from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
import fly.ap.scripting as scripting

QtCore, QtGui = qt.QtCore, qt.QtGui
TITLE = "Center Anchors Horizontally"
KEY = "anchors_center_horizontally"

# ---------------------------------------------------------------- centring logic
REFERENCES = [("Advance width", "advance"), ("Ink box", "ink")]


def target_x(
    layer: Any, reference: str, fraction: float, angle: float, y: float
) -> float | None:
    """X on the reference line at height y. None for an empty ink box.

    `fraction` 0 is the left edge, 1 the right edge. `angle` is the FontLab
    italic angle in degrees; the line leans right when it is negative.
    """
    slope = -math.tan(math.radians(angle))
    if reference == "advance":
        return layer.advanceWidth * fraction + slope * y
    box = layer.boundingBox
    if box.width() <= 0 and box.height() <= 0:
        return None
    centre_y = box.y() + box.height() / 2
    return box.x() + box.width() * fraction + slope * (y - centre_y)


def centre_changes(
    layer: Any, names: list[str], reference: str, fraction: float, angle: float
) -> list[anchor_writer.Change]:
    """Rows for the named anchors whose x changes. y stays as stored."""
    changes: list[anchor_writer.Change] = []
    for pin in layer.anchors:
        if pin.name not in names:
            continue
        x, y = anchor_writer.raw_point(pin)
        target = target_x(layer, reference, fraction, angle, y)
        if target is None or anchor_writer.half_up(target) == x:
            continue
        new = anchor_writer.half_up(target)
        changes.append(
            anchor_writer.Change(
                pin.name,
                f"{anchor_writer.fmt(x)}, {anchor_writer.fmt(y)}",
                f"{anchor_writer.fmt(new)}, {anchor_writer.fmt(y)}",
                ("set", pin.name, (new, y)),
            )
        )
    clash = anchor_writer.duplicated(layer, [c.name for c in changes])
    return anchor_writer.refusal(clash) if clash else changes


class CenterHorizontally(anchor_panel.panel_type()):
    """Names, reference, position slider, italic angle, master scope."""

    TITLE, KEY, ACTION = TITLE, KEY, "Centre"

    def build_controls(self) -> None:
        self.names = QtGui.QLineEdit("top, bottom")
        self.names.setPlaceholderText("anchor names, comma-separated")
        self.reference = QtGui.QComboBox()
        for label, _ in REFERENCES:
            self.reference.addItem(label)
        self.position = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.position.setRange(0, 100)
        self.position.setValue(50)
        self.position_label = QtGui.QLabel("50 %")
        self.position_label.setMinimumWidth(48)
        self.angle = QtGui.QDoubleSpinBox()
        self.angle.setStyleSheet(f"color: {anchor_panel.ink().color().name()};")
        self.angle.setRange(-45, 45)
        self.angle.setDecimals(1)
        self.angle.setSuffix("°")
        self.scope = self.scope_box()
        self.angle_source: Any = None  # package id the angle was last read from
        self.warning = QtGui.QLabel()
        self.warning.setWordWrap(True)
        self.warning.setStyleSheet(f"color: {anchor_panel.muted(self)};")
        self.form.addWidget(QtGui.QLabel("Anchors"), 0, 0)
        self.form.addWidget(self.names, 0, 1, 1, 2)
        self.form.addWidget(QtGui.QLabel("Centre of"), 1, 0)
        self.form.addWidget(self.reference, 1, 1, 1, 2)
        self.form.addWidget(QtGui.QLabel("Position"), 2, 0)
        self.form.addWidget(self.position, 2, 1)
        self.form.addWidget(self.position_label, 2, 2)
        self.form.addWidget(QtGui.QLabel("Italic angle"), 3, 0)
        self.form.addWidget(self.angle, 3, 1, 1, 2)
        self.form.addWidget(QtGui.QLabel("Masters"), 4, 0)
        self.form.addWidget(self.scope, 4, 1, 1, 2)
        self.form.addWidget(self.warning, 5, 0, 1, 3)
        for signal in (
            self.names.textChanged,
            self.reference.currentIndexChanged,
            self.position.valueChanged,
            self.angle.valueChanged,
            self.scope.currentIndexChanged,
        ):
            self.watch(signal)

    def on_reload(self) -> None:
        """Read the font italic angle once per font. Later reloads keep the override."""
        if self.package is not None and self.angle_source != self.package_id:
            self.angle_source = self.package_id
            self.angle.setValue(float(self.package.italicAngle_value or 0))

    def chosen_masters(self) -> list[str]:
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def planner(self) -> anchor_writer.Planner:
        several = self.scope.currentIndex == 1 and len(self.masters) > 1
        self.warning.setText(
            "One angle is used for every chosen master. It was read from the "
            "current master; other masters may have another angle."
            if several
            else ""
        )
        names = anchor_writer.parse_names(self.names.text)
        if not names:
            raise ValueError("Type the anchor names to centre.")
        reference = REFERENCES[self.reference.currentIndex][1]
        fraction = self.position.value / 100.0
        angle = float(self.angle.value)
        self.position_label.setText(f"{self.position.value} %")
        return lambda glyph, master, layer: centre_changes(
            layer, names, reference, fraction, angle
        )


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(CenterHorizontally, KEY)


if __name__ == "__main__":
    main()
