# this_file: Scripts/Contours/Correct Contour Direction.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Correct Contour Direction
"""Set the contour direction of the selected glyphs: outer and inner contours.

What: For each selected glyph and master, the table lists every closed
contour that runs the wrong way, with its current direction. Correct
reverses them.

How: Native flContour.clockwise gives the direction; contains tests all
segment start and mid points, as FontLab's own direction command does.
Nesting within the same shape decides each edit. If layer-wide nesting would
give a different answer, the contour is listed as "inside another shape,
direction left" and kept. Overlapping outer contours stay outer. Native
segments include TrueType implied on-curve points. PostScript outer contours
run counter-clockwise; TrueType uses the opposite convention. Native
flContour.reverse reverses in place.

Why: The result depends only on the shape, not on how the font was drawn, so
imports and pasted outlines get the right direction. A wrong direction makes
holes fill in some renderers and spoils overlap removal.

Use: Select glyphs. Run the script. Choose the masters. Press Correct. Press
Reload selection after you change the selection.

Benefit: Fixes many glyphs over many masters in one Undo step, and lists
each wrong contour before anything changes.

Safety: Open contours have no direction and are not counted. These shapes
are listed and kept, but count for the cross-shape safety check:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (a mirror in the transform turns the
  visible direction round).

After writing, a status note reports a newly introduced final off-curve with
raw Smooth (fl#8517), which FontLab may change on save. Existing conditions
are not reported as new. Check node types after VFJ reopen. A reversal
renumbers the nodes of that contour. The panel opens with All masters
chosen. When only one master has a wrong contour, check master compatibility
after the change: the other masters keep their node order.

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
keeps the compatibility check; writes disclose queued ids and possible date
changes.
After the write, it reads every direction back. If FontLab fails part-way,
the error says that native changes may remain. The change is recorded as one
Undo step. The one-step write, the automatic-layer rule, the pending-update
check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_correct_direction.py,
Apache-2.0. Adapted for the current FontLab 9 API.
"""

from typing import Any

import fly.ap.affine as affine  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt

TITLE = "Correct Contour Direction"
KEY = "outlines_correct_direction"
# Native segments handle quadratic implied on-curves as well as cubics.


def wrong_contours(contours: list[tuple[Any, Any]]) -> list[int]:
    """Use FontLab's start-and-midpoint nesting rule, in glyph coordinates.

    Each item is (contour, owning shape transform). All closed contours,
    including kept shapes, contribute to depth. Only callers choose edits.
    Native calculate(k + 0.5) evaluates the midpoint of segment k.
    """
    tests = [
        [
            transform.map(point)
            for k, segment in enumerate(contour.segments())
            for point in (segment.p0, contour.calculate(k + 0.5))
        ]
        for contour, transform in contours
    ]
    inverses = [affine.invert(affine.from_qtransform(tx)) for _, tx in contours]
    wrong = []
    for i, (contour, transform) in enumerate(contours):
        if not tests[i] or abs(float(contour.getSquare())) < 1e-9:
            continue
        depth = 0
        for j, (other, other_transform) in enumerate(contours):
            if i == j:
                continue
            inverse = inverses[j]
            if all(
                other.contains(
                    qt.QtCore.QPointF(*affine.apply(inverse, point.x(), point.y()))
                )
                for point in tests[i]
            ):
                depth += 1
        want_ccw = (depth % 2 == 0) != bool(contour.isTT)
        # Editable shapes only translate; kept mirrors still affect containment.
        if (not bool(contour.clockwise)) != want_ccw:
            wrong.append(i)
    return wrong


def direction_changes(layer: Any) -> list[outline_writer.Change]:
    """Use same-shape direction; keep cross-shape parity conflicts with a note."""
    shapes, notes = outline_writer.outline_shapes(layer)
    editable = {shape.id for shape in shapes}
    found = [
        (contour, shape)
        for shape in layer.shapes
        for contour in shape.contours
        if contour.closed
    ]
    layer_wrong = set(wrong_contours([(c, s.transform) for c, s in found]))
    shape_wrong = set()
    for shape in layer.shapes:
        indices = [i for i, (_, owner) in enumerate(found) if owner.id == shape.id]
        own = [(found[i][0], shape.transform) for i in indices]
        shape_wrong.update(indices[i] for i in wrong_contours(own))
    rows = []
    for index, (contour, shape) in enumerate(found):
        if shape.id not in editable:
            continue
        if (index in layer_wrong) != (index in shape_wrong):
            rows.append(
                outline_writer.Change(
                    f"contour {index + 1}", "", "inside another shape, direction left"
                )
            )
            continue
        if index not in shape_wrong:
            continue
        ccw = not bool(contour.clockwise)
        rows.append(
            outline_writer.Change(
                f"contour {index + 1}",
                "counter-clockwise" if ccw else "clockwise",
                "clockwise" if ccw else "counter-clockwise",
                (contour, not ccw),
            )
        )
    return rows + outline_writer.note_rows(notes)


def final_smooth_points(contours: list[Any]) -> set[tuple[float, float]]:
    """Coordinates of existing final off-curves with raw Smooth; read only."""
    result = set()
    for contour in contours:
        nodes = contour.nodes()
        if contour.closed and nodes and not nodes[-1].isOn() and nodes[-1].smooth:
            result.add((float(nodes[-1].x), float(nodes[-1].y)))
    return result


class ReverseEditor(outline_writer.Editor):
    """Reverse contours with FontLab's own flContour.reverse."""

    def __init__(self) -> None:
        self.before: dict[int, set[tuple[float, float]]] = {}
        self.advice: list[str] = []

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        """Snapshot existing save-risk conditions before any history starts."""
        for edit in edits:
            contour = edit[0]
            self.before[id(contour)] = final_smooth_points([contour])
        return list(edits)

    def write(self, layer: Any, steps: list[Any]) -> None:
        for contour, _ in steps:
            contour.reverse()

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed: list[str] = []
        for layer, steps in prepared:
            for contour, ccw in steps:
                introduced = final_smooth_points([contour]) - self.before[id(contour)]
                if introduced:
                    message = (
                        f"{layer.name}: a final off-curve with raw Smooth was "
                        "introduced; FontLab may change on save (fl#8517). "
                        "Check node types after VFJ reopen."
                    )
                    if message not in self.advice:
                        self.advice.append(message)
                if (not bool(contour.clockwise)) != ccw:
                    missed.append(f"{layer.name}: a contour kept its direction")
        return missed


class CorrectContourDirection(outline_panel.panel_type()):
    """Master scope only; one row per wrong contour."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Correct", "Reversed", "contour"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Contour", "Now", "After")
    SCOPE = 1  # a reversal renumbers the nodes: start with all masters

    def planner(self) -> outline_writer.Planner:
        return lambda glyph, master, layer: direction_changes(layer)

    def editor(self) -> outline_writer.Editor:
        self.risk_editor = ReverseEditor()
        return self.risk_editor

    def apply(self) -> None:
        """Append save-risk advice to the result without calling it a failed
        store.
        """
        self.risk_editor = None
        super().apply()
        if self.risk_editor is not None and self.risk_editor.advice:
            note = "; ".join(self.risk_editor.advice)
            self.status.setText(f"{self.status.text} · {note}")


def main() -> Any:
    """Open the panel, or replace the one that is already open."""
    return scripting.show_script_dialog(CorrectContourDirection, KEY)


if __name__ == "__main__":
    main()
