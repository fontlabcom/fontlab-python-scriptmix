# this_file: Scripts/Masters/Transform Background.py
# SPDX-License-Identifier: Apache-2.0
"""Scale or shift the background of the selected glyph layers.

What it does:
    Open a small floating panel with two actions. "Scale" multiplies the
    background of every selected glyph layer by a percentage, around the origin
    (0, 0). "Shift" moves the background horizontally by a number of units.
    Positive units move right, negative units move left.

How it works:
    The background of a FontLab layer is its mask layer. The script finds it
    with getMaskLayer(False), so it never creates a background. Layers without
    one are skipped. It then applies one transform to the mask layer: contours,
    components and anchors move together. Metrics and guides of the mask stay.
    FontLab rounds the result as set in the preferences. One notification covers
    all backgrounds: one Undo step per click.

Why this design:
    - One panel replaces the two Glyphs scripts. It stays open, so you can
      scale, shift and repeat while you compare with the foreground.
    - The Glyphs scripts read a number from a text box once per run and close.
      They break on invalid input. This panel checks the number and shows the
      reason in the status line.
    - The Glyphs scale script ignores components. This script moves them too.
    - A glyph that has an automatic layer, or is a base of one (also through
      manual composites), is refused: FontLab cannot undo an edit that reaches
      an automatic layer. So is a click while FontLab has pending glyph
      updates. The shared module fly.ap.history does these checks and the
      one-step write.
    - Zero, negative, empty and non-finite scale values are refused. A scale of
      0 would destroy the background; a negative scale would mirror it.

How to use:
    Select glyphs in the Font window, or open a Glyph window. Type a number.
    Press Return or click the button. Use Edit > Undo to revert.

Benefit:
    Fit a traced or imported background to your drawing without redrawing it.

Credit:
    Behaviour after Pedro Arilla's Glyphs scripts "Scale background in selected
    glyphs" and "Shift background in selected glyphs" (Apache-2.0). Independent
    rewrite. No source code was copied.
"""

import math
from collections.abc import Sequence
from time import monotonic
from typing import Any

TITLE = "Transform Background"
KEY = "masters_transform_background"
DEADLINE_SECONDS = 2.0

Matrix = tuple[float, float, float, float, float, float]  # Qt: m11 m12 m21 m22 dx dy


def parse_number(text: str) -> float:
    """Read a finite number. Accept "," as decimal mark. Raise ValueError."""
    clean = text.strip().replace(",", ".")
    if not clean:
        raise ValueError("Enter a number.")
    try:
        value = float(clean)
    except ValueError:
        raise ValueError(f"'{text.strip()}' is not a number.") from None
    if not math.isfinite(value):
        raise ValueError("The number must be finite.")
    return value


def scale_matrix(percent: float) -> Matrix:
    """Uniform scale about the origin. Percent must be above zero."""
    if percent <= 0:
        raise ValueError("The scale must be above 0%.")
    factor = percent / 100.0
    return (factor, 0.0, 0.0, factor, 0.0, 0.0)


def shift_matrix(units: float) -> Matrix:
    """Horizontal move by `units`."""
    return (1.0, 0.0, 0.0, 1.0, units, 0.0)


def transform_backgrounds(action: str, matrix: Matrix) -> str:
    """Apply `matrix` to the background of every selected glyph layer.

    Return a status message. Raise ValueError when nothing can be done.
    """
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    from fly import qt
    from fly.ap.layer_selection import capture
    from fly.ap.scripting import current_package

    selection = capture(monotonic() + DEADLINE_SECONDS)
    package = current_package()
    if package is None or not selection.occurrences:
        raise ValueError("Select a glyph first.")
    masks: dict[int, Any] = {}
    owners: dict[int, Any] = {}
    for item in selection.occurrences:
        layer = item.layer
        if layer.isMaskLayer or layer.isService or layer.autoLayer:
            raise ValueError(
                f"Layer '{item.layer_name}' of '{item.glyph_name}' is not a body layer."
            )
        mask = layer.getMaskLayer(False)
        if mask is None or mask.isNull or not mask.isValid:
            continue
        masks.setdefault(int(mask.id), mask)
        owners.setdefault(item.glyph_id, item.glyph)
    if not masks:
        raise ValueError("None of the selected layers has a background.")
    transform = qt.QtGui.QTransform(*matrix)

    def mutate() -> Sequence[Any]:
        for mask in masks.values():
            mask.applyTransform(transform, True, False, False, True)
            mask.changed()
            if mask.update() is False:
                raise RuntimeError("FontLab could not update a background.")
        return ()

    history.commit(
        f"{action} background",
        list(masks.values()),
        list(owners.values()),
        mutate,
        operation="geometry",
        facts=history.scan_auto_facts(package),
    )
    return f"{action}: {len(masks)} background(s) in {len(owners)} glyph(s)."


def muted(widget: Any, QtGui: Any) -> str:
    """CSS colour for secondary text in the current palette."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


def panel_type(QtGui: Any) -> Any:
    """Build the panel class once Qt is available (keeps import host-free)."""
    from fly import ap

    class Panel(QtGui.QDialog):
        """Floating panel: two number fields, two buttons, one status line."""

        def __init__(self, parent: Any = None) -> None:
            QtGui.QDialog.__init__(self, parent)
            self._connections: list[Any] = []
            self.setWindowTitle(TITLE)
            self.setMinimumWidth(380)
            root = QtGui.QVBoxLayout(self)
            root.setContentsMargins(20, 18, 20, 16)
            root.setSpacing(12)
            heading = QtGui.QLabel(TITLE)
            font = heading.font
            font.setPointSizeF(font.pointSizeF() * 1.35)
            font.setBold(True)
            heading.setFont(font)
            root.addWidget(heading)
            hint = QtGui.QLabel(
                "Acts on the backgrounds of the selected glyph layers. "
                "Scale works about the origin (0, 0)."
            )
            hint.setWordWrap(True)
            hint.setStyleSheet(f"color: {muted(self, QtGui)};")
            root.addWidget(hint)
            grid = QtGui.QGridLayout()
            grid.setHorizontalSpacing(8)
            grid.setVerticalSpacing(8)
            self.scale_edit = QtGui.QLineEdit("100")
            self.shift_edit = QtGui.QLineEdit("0")
            self.scale_button = QtGui.QPushButton("Scale")
            self.shift_button = QtGui.QPushButton("Shift")
            for row, (label, edit, unit, button) in enumerate(
                (
                    ("Scale to", self.scale_edit, "%", self.scale_button),
                    ("Shift by", self.shift_edit, "units (+ right, - left)", self.shift_button),
                )
            ):
                grid.addWidget(QtGui.QLabel(label), row, 0)
                grid.addWidget(edit, row, 1)
                grid.addWidget(QtGui.QLabel(unit), row, 2)
                grid.addWidget(button, row, 3)
            root.addLayout(grid)
            footer = QtGui.QHBoxLayout()
            self.status = QtGui.QLabel("")
            self.status.setStyleSheet(f"color: {muted(self, QtGui)};")
            self.close_button = QtGui.QPushButton("Close")
            footer.addWidget(self.status, 1)
            footer.addWidget(self.close_button)
            root.addLayout(footer)
            for signal, action in (
                (self.scale_button.clicked, "scale"),
                (self.scale_edit.returnPressed, "scale"),
                (self.shift_button.clicked, "shift"),
                (self.shift_edit.returnPressed, "shift"),
            ):
                ap.scripting.connect_guarded(self, signal, lambda *a, act=action: self.apply(act))
            ap.scripting.connect_guarded(self, self.close_button.clicked, lambda *a: self.close())

        def apply(self, action: str) -> None:
            """Run one action and show its result or its refusal."""
            try:
                if action == "scale":
                    message = transform_backgrounds(
                        "Scale", scale_matrix(parse_number(self.scale_edit.text))
                    )
                else:
                    message = transform_backgrounds(
                        "Shift", shift_matrix(parse_number(self.shift_edit.text))
                    )
            except (ValueError, RuntimeError, TimeoutError) as error:
                message = str(error)
            self.status.setText(message)

        def closeEvent(self, event: Any) -> None:
            """Release owned signals and delete the panel."""
            ap.scripting.close_script_dialog(self, event, KEY)

    return Panel


def main() -> Any:
    """Open the panel (one instance, reused through the shared registry)."""
    from fly import ap, qt

    return ap.scripting.show_script_dialog(panel_type(qt.QtGui), KEY)


if __name__ == "__main__":
    main()
