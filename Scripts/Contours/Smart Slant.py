# this_file: Scripts/Contours/Smart Slant.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Smart Slant
"""Slant outlines and compensate the change in their horizontal bounds.

What: Apply a slant, then preserve sidebearings or the original ink centre.
How: Measure the actual cubic bounds before and after the shear. Keeping
sidebearings aligns the left ink edge and adjusts advance by the ink-width
change. Centre mode keeps advance and centres the new ink on the old ink.
Why: A plain shear can shift the drawing within its advance. Compensation
gives a controlled starting point for an italic, across selected masters.
Native Tools > Transform > Slant, Slant by Italic Angle and Actions > Oblique
do not provide this spacing compensation. Scripts/Contours/Slant.py keeps
the advance unchanged. This tool keeps both sidebearings by adjusting the
advance, or keeps the original ink centre at unchanged advance.
Use: Select glyphs, run this panel, choose angle and spacing mode, inspect
the preview, then Slant. Positive angles lean right. Reload new selections.
Benefit: Repeat the same optical placement over glyphs of different heights.

Anchors follow the same matrix when enabled. Guides and metric expressions
stay. Components, open contours and locked shapes are kept and listed;
other glyphs can still be edited. Automatic
glyphs and their bases follow the panel's geometry policy. Each Apply is
recorded as one Undo step. FontLab can round the baked coordinates.
Font italic-angle metadata is not changed by this drawing tool.

Independent behaviour-only rewrite after Fernando Díaz, Reset Type Studio,
https://github.com/Reset-Type-Studio/Glyphs-Scripts, Paths/Smart Slant.py.
Apache-2.0 declared in README.md; no separate LICENSE file. No code copied.
"""

import math
from typing import Any

import fly.ap.affine as affine  # noqa: PLR0402
import fly.ap.outline_transform as outline_transform  # noqa: PLR0402
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402
import fly.ap.scripting as scripting  # noqa: PLR0402

TITLE, KEY = "Smart Slant", "contours_smart_slant"


def compensated_matrix(
    angle: float,
    before: tuple[float, float, float, float],
    after: tuple[float, float, float, float],
    sidebearings: bool,
) -> tuple[float, ...]:
    """Return shear plus exact ink placement from measured, unshifted bounds."""
    if (
        not all(math.isfinite(v) for v in (angle, *before, *after))
        or not -80 <= angle <= 80
    ):
        raise ValueError("Use finite bounds and an angle between -80° and 80°.")
    x, y, width, height = before
    pivot = y + height / 3.0
    dx = x - after[0] if sidebearings else x + width / 2 - after[0] - after[2] / 2
    slope = math.tan(math.radians(angle))
    return (1.0, 0.0, slope, 1.0, dx - slope * pivot, 0.0)


def slant_plan(
    layer: Any, angle: float, sidebearings: bool, anchors: bool
) -> list[outline_writer.Change]:
    """Measure curves in glyph space; use the shared transform writer."""
    if not math.isfinite(angle) or not -80 <= angle <= 80:
        raise ValueError("Choose an angle between -80° and 80°.")
    if layer.isLocked:
        return [outline_writer.Change("layer", "", "locked layer, kept")]
    for shape in layer.shapes:
        if shape.isComponent or shape.contentLocked or list(shape.includesList):
            return [
                outline_writer.Change(
                    "layer", "", "component, locked or linked outline, kept"
                )
            ]
        if any(not c.closed for c in shape.contours):
            return [outline_writer.Change("layer", "", "open contour, kept")]
        if any(
            affine.from_qtransform(c.transform) != affine.IDENTITY
            for c in shape.contours
        ):
            return [outline_writer.Change("layer", "", "contour transform, kept")]
    curves = outline_transform.layer_outline(layer)
    if not curves or angle == 0:
        return []
    box = outline_transform.outline_path(curves).boundingRect()
    before = (float(box.x()), float(box.y()), float(box.width()), float(box.height()))
    if before[2] <= 0 or before[3] <= 0:
        return [outline_writer.Change("layer", "", "zero ink width or height, kept")]
    k, pivot = math.tan(math.radians(angle)), before[1] + before[3] / 3.0
    shear = (1.0, 0.0, k, 1.0, -k * pivot, 0.0)
    result = outline_transform.outline_path(
        outline_transform.mapped(curves, shear)
    ).boundingRect()
    after = (
        float(result.x()),
        float(result.y()),
        float(result.width()),
        float(result.height()),
    )
    matrix = compensated_matrix(angle, before, after, sidebearings)
    rows = outline_transform.transform_changes(
        layer, matrix, anchors, f"{angle:g}°; compensated"
    )
    if any(row.problem for row in rows):
        return [
            outline_writer.Change(
                "layer",
                "",
                "; ".join(row.problem for row in rows if row.problem) + "; kept",
            )
        ]
    width = float(layer.advanceWidth)
    new_width = width + after[2] - before[2] if sidebearings else width
    if not math.isfinite(new_width) or new_width < 0:
        return [
            outline_writer.Change("advance", "", "negative or non-finite advance, kept")
        ]
    if new_width != width:
        rows.append(
            outline_writer.Change(
                "advance", f"{width:g}", f"{new_width:g}", ("advance", new_width)
            )
        )
    return rows


class SlantEditor(outline_transform.TransformEditor):
    """Write the shared shape/anchor plan and the compensated advance."""

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        """Keep all baked-node expectations; a stationary first node proves little."""
        expected = []
        for kind, items in edits:
            if kind != "shapes":
                continue
            for shape, matrix, bake, _ in items:
                if bake:
                    expected.extend(
                        (n, *affine.apply(matrix, float(n.x), float(n.y)))
                        for c in shape.contours
                        for n in c.nodes()
                    )
        return [*edits, ("verify", expected)]

    def write(self, layer: Any, steps: list[Any]) -> None:
        super().write(layer, [s for s in steps if s[0] not in ("advance", "verify")])
        for kind, value in steps:
            if kind == "advance":
                layer.advanceWidth = value

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        geometry = [
            (layer, [s for s in steps if s[0] not in ("advance", "verify")])
            for layer, steps in prepared
        ]
        missed = super().check(geometry)
        for layer, steps in prepared:
            for kind, values in steps:
                if kind == "verify" and any(
                    not math.isfinite(n.x)
                    or not math.isfinite(n.y)
                    or abs(n.x - x) > 0.5
                    or abs(n.y - y) > 0.5
                    for n, x, y in values
                ):
                    missed.append(f"{layer.name}: node coordinates")
        return missed + [
            str(layer.name)
            for layer, steps in prepared
            for kind, value in steps
            if kind == "advance" and abs(float(layer.advanceWidth) - value) > 0.5
        ]


class SmartPanel(outline_transform.panel_type()):
    """Angle, sidebearing choice, anchors, masters and geometry preview."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Slant", "Slanted", "layer item"

    def build_controls(self) -> None:
        from fly import qt

        self.slant_degrees = self.spin(-80, 80, 10, "°", decimals=1)
        self.keep_margins = qt.QtGui.QCheckBox("Keep sidebearings (adjust advance)")
        self.keep_margins.setChecked(True)
        self.move_pins = qt.QtGui.QCheckBox("Slant anchors too")
        self.move_pins.setChecked(True)
        self.add_row("Angle", self.slant_degrees)
        self.add_row("Spacing", self.keep_margins)
        self.add_row("", self.move_pins)
        self.watch(self.keep_margins.toggled)
        self.watch(self.move_pins.toggled)

    def planner(self) -> outline_writer.Planner:
        angle = float(self.slant_degrees.value)
        if not math.isfinite(angle) or not -80 <= angle <= 80:
            raise ValueError("Choose an angle between -80° and 80°.")
        margins, anchors = self.keep_margins.isChecked(), self.move_pins.isChecked()

        def plan(glyph: Any, master: str, layer: Any) -> list[outline_writer.Change]:
            try:
                return slant_plan(layer, angle, margins, anchors)
            except ValueError as error:
                return [outline_writer.Change("layer", "", f"{error}; kept")]

        return plan

    def preview_matrix(self, layer: Any) -> tuple[Any, None]:
        rows = slant_plan(
            layer, float(self.slant_degrees.value), self.keep_margins.isChecked(), False
        )
        # The planner has already composed each original shape transform.
        # Obtain the glyph-space matrix from the same measured bounds.
        if not rows or rows[0].edit is None:
            return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0), None
        shape, composed, _, _ = rows[0].edit[1][0]
        return affine.concat(
            affine.invert(affine.from_qtransform(shape.transform)), composed
        ), None

    def editor(self) -> outline_writer.Editor:
        return SlantEditor()


def main() -> Any:
    """Open the modeless panel and display predictable boundary errors."""
    try:
        return scripting.show_script_dialog(SmartPanel, KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        from fly import fl, qt

        qt.QtGui.QMessageBox.warning(fl.MainWindow(), TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
