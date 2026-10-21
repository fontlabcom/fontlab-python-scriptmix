# this_file: Scripts/Contours/Transform.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Transform
"""Scale, skew, rotate and move the outlines of the selected glyphs, with a
preview.

What: Set scale (x and y, in %), skew and rotation (in degrees) and a move
(in units), and pick the origin. The preview paints the first selected glyph
of the current master before (faint) and after (accent). The table lists
each glyph and master with its node count and origin. Transform applies it.

How: The script builds one affine matrix: move the origin to 0, 0; scale;
skew; rotate; move back; then move by the offset. The origin is computed per
layer: bounding box centre or bottom-left, the glyph origin, or the advance
centre on the baseline. Each shape gets the matrix the way FontLab's own
layer transform does: a plain own outline gets new node positions (FontLab
may round them); a component, a shared outline or a scaled shape keeps its
nodes and gets the composed transform. Anchors follow when you tick "Move
anchors too". The advance width and the guides stay.

Why: One panel does what otherwise takes several steps, for many glyphs and
masters at once, and shows the result first. For a slant about the x-height
with the font's italic angle, use Contours > Slant.

Use: Select glyphs. Run the script. Set the values, the origin and the
masters. Press Transform. Press Reload selection after you change the
selection.

Benefit: Exact, repeatable transforms over many glyphs and masters in one
Undo step.

Safety: These cases block or limit the edit:

- an anchor that would move onto 0, 0 blocks Apply: FontLab cannot redo that
  move (fl#8527);
- a glyph that has an automatic layer is listed and skipped.

So is a glyph that is a base of an automatic composite, also through other
composites, unless you tick "Also edit bases of automatic composites"
(FontLab then rebuilds those composites; Undo may not restore their
anchors). The script refuses before any history exists when FontLab holds
queued glyph updates. After the write, it reads transforms, a node per baked
shape and the anchors back. If FontLab fails part-way, the error says that
native changes may remain. The change is recorded as one Undo step. The
one-step write, the automatic-layer rule, the pending-update check, the
preview and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_transform); the matrix math is fly.ap.affine; the planner
belongs to this script.

Source: the author's own FontLab sample outlines_transform_dialog.py,
Apache-2.0. Adapted for the current FontLab 9 API.
"""

import math
from typing import Any

import fly.ap.affine as affine  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_transform as outline_transform  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt

QtGui = qt.QtGui
TITLE = "Transform"
KEY = "outlines_transform_dialog"
ORIGINS = (
    "Bounding box centre",
    "Bounding box bottom-left",
    "Glyph origin (0, 0)",
    "Advance centre on baseline",
)
Params = tuple[
    float, float, float, float, float, float
]  # sx %, sy %, skew, turn, mx, my


# ---------------------------------------------------------------- transform logic
def mapper(params: Params, origin: tuple[float, float]) -> outline_transform.Affine:
    """One matrix: scale, then skew, then rotate about `origin`, then move.

    Skew k = tan(angle): x' = x + k y. Rotation turns x towards y.
    """
    sx, sy, skew, angle, mx, my = params
    if not sx or not sy:
        raise ValueError("A scale of 0 % would flatten the outline.")
    ox, oy = origin
    steps = (
        (1.0, 0.0, 0.0, 1.0, -ox, -oy),
        (sx / 100.0, 0.0, 0.0, sy / 100.0, 0.0, 0.0),
        (1.0, 0.0, math.tan(math.radians(skew)), 1.0, 0.0, 0.0),
        affine.rotation(angle),
        (1.0, 0.0, 0.0, 1.0, ox + mx, oy + my),
    )
    matrix = affine.IDENTITY
    for step in steps:
        matrix = affine.concat(matrix, step)
    return matrix


def origin_of(layer: Any, choice: int) -> tuple[float, float]:
    """Origin of the transform for this layer, by the ORIGINS choice."""
    if choice == 2:
        return 0.0, 0.0
    if choice == 3:
        return float(layer.advanceWidth) / 2.0, 0.0
    box = layer.boundingBox
    if choice == 0:
        return box.x() + box.width() / 2.0, box.y() + box.height() / 2.0
    return float(box.x()), float(box.y())


class TransformOutlines(outline_transform.panel_type()):
    """Six values, origin, anchors and master scope; one row per layer."""

    TITLE, KEY, ACTION, DONE, UNIT = (
        TITLE,
        KEY,
        "Transform",
        "Transformed",
        "layer item",
    )
    HEADERS: tuple[str, ...] = ("Glyph · master", "Item", "Now", "Origin")

    def build_controls(self) -> None:
        self.scale_x = self.spin(1, 1000, 100, " %", decimals=1)
        self.scale_y = self.spin(1, 1000, 100, " %", decimals=1)
        self.skew = self.spin(-80, 80, 0, "°", decimals=1)
        self.turn = self.spin(-360, 360, 0, "°", decimals=1)
        self.move_x = self.spin(-5000, 5000, 0, decimals=1)
        self.move_y = self.spin(-5000, 5000, 0, decimals=1)
        self.add_row("Scale x, y", self.scale_x, self.scale_y)
        self.add_row("Skew, rotate", self.skew, self.turn)
        self.add_row("Move x, y", self.move_x, self.move_y)
        self.origin = QtGui.QComboBox()
        for text in ORIGINS:
            self.origin.addItem(text)
        self.add_row("Origin", self.origin)
        self.watch(self.origin.currentIndexChanged)
        self.anchors = QtGui.QCheckBox("Move anchors too")
        self.anchors.setChecked(True)
        self.add_row("", self.anchors)
        self.watch(self.anchors.toggled)

    def params(self) -> Params:
        boxes = (
            self.scale_x,
            self.scale_y,
            self.skew,
            self.turn,
            self.move_x,
            self.move_y,
        )
        return tuple(float(box.value) for box in boxes)  # type: ignore[return-value]

    def preview_matrix(
        self, layer: Any
    ) -> tuple[outline_transform.Affine, float | None]:
        return mapper(self.params(), origin_of(layer, self.origin.currentIndex)), None

    def planner(self) -> outline_writer.Planner:
        params, choice = self.params(), self.origin.currentIndex
        anchors = self.anchors.isChecked()

        def plan(glyph: Any, master: str, layer: Any) -> list[outline_writer.Change]:
            origin = origin_of(layer, choice)
            note = f"{outline_writer.fmt(origin[0])}, {outline_writer.fmt(origin[1])}"
            return outline_transform.transform_changes(
                layer, mapper(params, origin), anchors, note
            )

        return plan

    def editor(self) -> outline_writer.Editor:
        return outline_transform.TransformEditor()


def main() -> Any:
    """Open the panel, or replace the one that is already open."""
    return scripting.show_script_dialog(TransformOutlines, KEY)


if __name__ == "__main__":
    main()
