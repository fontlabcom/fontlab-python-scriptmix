# this_file: Scripts/Contours/Slant.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Slant
"""Slant the selected glyphs by an angle, optionally the font's italic angle.

What: Set an angle, or press the italic-angle button, and choose the pivot:
the baseline, or half the x-height of each master. The preview paints the
first selected glyph of the current master with the pivot line. The table
lists each glyph and master with its node count and pivot. Slant applies it.

How: x' = x + tan(angle) × (y − pivot); y stays. Each shape gets the matrix
the way FontLab's own layer transform does: a plain own outline gets new
node positions (FontLab may round them); a component, a shared outline or a
scaled shape keeps its nodes and gets the composed transform. Anchors follow
when you tick "Slant anchors too". The advance width and the guides stay.

Why: A slant about the baseline pushes tall glyphs to the right. A slant
about half the x-height keeps the glyph centred in its advance: this is the
usual first step of an oblique or italic. Contours > Transform has a skew
too, but no italic angle and no per-master x-height pivot. Compared with
Tools > Actions > Slant, this panel offers a half-x-height pivot per master.
The italic button copies the current master’s angle into the shared angle
field; that same angle is then applied to every chosen master.

Use: Select glyphs. Run the script. Set the angle, the pivot and the
masters. Press Slant. Press Reload selection after you change the selection.

Benefit: A consistent oblique over many glyphs and masters in one Undo step.

Safety: These cases block or limit the edit:

- an anchor that would move onto 0, 0 blocks Apply: FontLab cannot redo that
  move (fl#8527);
- a glyph that has an automatic layer is listed and skipped.

So is a glyph that is a base of an automatic composite, also through other
composites, unless you tick "Also edit bases of automatic composites"
(FontLab then rebuilds those composites; Undo may not restore their
anchors). The script discloses queued ids and their possible date changes.
After the write, it reads transforms, a node per baked
shape and the anchors back. If FontLab fails part-way, the error says that
native changes may remain. The change is recorded as one Undo step. The
one-step write, the automatic-layer rule, the pending-update check, the
preview and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_transform); the matrix math is fly.ap.affine; the planner
belongs to this script.

Source: the author's own FontLab sample outlines_slant.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

import math
from typing import Any

import fly.ap.outline_transform as outline_transform  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import ap, qt

QtGui = qt.QtGui
fontlab = ap.fontlab
TITLE = "Slant"
KEY = "outlines_slant"
PIVOTS = ("Baseline", "Half x-height (keeps the glyph centred)")


# ---------------------------------------------------------------- slant logic
def slant_matrix(angle: float, pivot_y: float) -> outline_transform.Affine:
    """x' = x + tan(angle) (y - pivot_y); y' = y. Positive angles lean right."""
    if not -89 < angle < 89:
        raise ValueError("The angle must be between -89° and 89°.")
    k = math.tan(math.radians(angle))
    return (1.0, 0.0, k, 1.0, -k * pivot_y, 0.0)


def pivot(package: Any, master: str, choice: int) -> float:
    """Y of the slant pivot: the baseline (0), or half the master's x-height."""
    if choice == 0:
        return 0.0
    return float(fontlab.FontMetrics(package, master).xHeight) / 2.0


def italic_angle(package: Any) -> float:
    """The current master’s italic angle in degrees (FontLab: negative leans
    right).
    """
    return float(package.italicAngle_value)


class SlantOutlines(outline_transform.panel_type()):
    """Angle, italic button, pivot, anchors and master scope; one row per layer."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Slant", "Slanted", "layer item"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Item", "Now", "Pivot y")

    def build_controls(self) -> None:
        self.angle = self.spin(-45, 45, 10, "°", decimals=1)
        self.italic = QtGui.QPushButton("Current master’s italic angle")
        self.add_row("Angle", self.angle, self.italic)
        self.watch(self.italic.clicked, self.use_italic)
        self.pivots = QtGui.QComboBox()
        for text in PIVOTS:
            self.pivots.addItem(text)
        self.pivots.setCurrentIndex(1)
        self.add_row("About", self.pivots)
        self.watch(self.pivots.currentIndexChanged)
        self.anchors = QtGui.QCheckBox("Slant anchors too")
        self.anchors.setChecked(True)
        self.add_row("", self.anchors)
        self.watch(self.anchors.toggled)

    def on_reload(self) -> None:
        """Show the font's italic angle on the button; off when it is 0."""
        angle = italic_angle(self.package) if self.package is not None else 0.0
        self.italic.setText(f"Current master’s italic angle ({angle:g}°)")
        self.italic.setEnabled(bool(angle))

    def use_italic(self) -> None:
        """Set the angle from the font: FontLab's negative angle leans right."""
        if self.package is None:
            raise ValueError("Open a font first.")
        self.angle.setValue(-italic_angle(self.package))

    def preview_matrix(
        self, layer: Any
    ) -> tuple[outline_transform.Affine, float | None]:
        y = pivot(self.package, self.current_master, self.pivots.currentIndex)
        return slant_matrix(float(self.angle.value), y), y

    def planner(self) -> outline_writer.Planner:
        angle, choice = float(self.angle.value), self.pivots.currentIndex
        anchors, package = self.anchors.isChecked(), self.package
        slant_matrix(angle, 0.0)  # refuse a bad angle before the table fills

        def plan(glyph: Any, master: str, layer: Any) -> list[outline_writer.Change]:
            y = pivot(package, master, choice)
            return outline_transform.transform_changes(
                layer, slant_matrix(angle, y), anchors, outline_writer.fmt(y)
            )

        return plan

    def editor(self) -> outline_writer.Editor:
        return outline_transform.TransformEditor()


def main() -> Any:
    """Open the panel, or replace the one that is already open."""
    return scripting.show_script_dialog(SlantOutlines, KEY)


if __name__ == "__main__":
    main()
