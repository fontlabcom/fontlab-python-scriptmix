# this_file: Scripts/Contours/Remove Overlap.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Remove Overlap
"""Remove overlaps in the outline shapes of the selected glyphs.

What: For each selected glyph and master, the table lists every outline
shape whose contours overlap: the contour count now and after the merge.
Remove Overlap merges them. Shapes without overlap stay untouched. Overlaps
between separate shapes are not merged. This tool tests intersections
between contours; a single self-intersecting contour is kept.

How: Each shape goes through FontLab's FontGate engine: a copy is made with
flShape.convertToFgShape, fgShape.removeOverlap merges it (a shape has an
overlap when native contours intersect or same-direction contours nest), and
flShape.assign writes the result back into the same shape object. The start
node of each new contour moves back to an old start point when one survives
the merge, as FontLab's own command does. The preview runs the same merge on
a copy, so the numbers are exact.

Why: Overlapping contours print and render fine in many places, but fonts
for the web, variable fonts and many tools need clean outlines. With "Keep
masters compatible" ticked, a glyph is held back when the masters would get
different contours, or when only some masters are in scope: the merge would
break interpolation.

Use: Select glyphs. Run the script. Choose the masters. Press Remove
Overlap. Press Reload selection after you change the selection.

Benefit: Cleans many glyphs over many masters in one Undo step, and lists
each merge before anything changes.

Safety: A status note reports only a newly introduced final off-curve with
raw Smooth (fl#8517), which FontLab may change on save. Check node types
after VFJ reopen. The merge rebuilds the contours of a merged shape: node
names, node flags, contour names and corner_smooth (fl#8569) in that shape
are not kept. FontGate assign also replaces the shape appearance. No name,
note or appearance preservation is claimed for that round trip. These shapes
are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with a transform (FontGate would merge them in stored coordinates);
- shapes with an open contour (an open contour has no inside).

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
refuses before any history exists when FontLab holds queued glyph updates.
After the write, it reads the contour counts back. If FontLab fails
part-way, the error says that native changes may remain. The change is
recorded as one Undo step. The one-step write, the automatic-layer rule, the
pending-update check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_remove_overlap.py,
Apache-2.0. Adapted for the current FontLab 9 API.
"""

from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import ap

TITLE = "Remove Overlap"
KEY = "outlines_remove_overlap"


# ---------------------------------------------------------------- overlap logic
def fontgate_copy(shape: Any, merge: bool) -> Any:
    """FontGate copy of the shape; with `merge`, overlaps removed. The shape
    stays.
    """
    result = ap.fontgate.fgShape()
    shape.convertToFgShape(result)
    if merge:
        result.removeOverlap()
    return result


def node_counts(shape: Any) -> tuple[int, ...]:
    """Sorted FontGate node counts of the contours of `shape` (a FontGate shape).

    Both sides of the comparison use FontGate's count, so a different node
    convention in FontLab cannot fake a change.
    """
    return tuple(sorted(int(contour.countNodes()) for contour in shape.contours))


def start_points(shape: Any) -> set[tuple[float, float]]:
    """Positions of the on-curve start nodes of the shape's contours."""
    found = set()
    for contour in shape.contours:
        points = outline_writer.node_points(contour)
        if points and points[0][2]:
            found.add((round(points[0][0], 3), round(points[0][1], 3)))
    return found


def overlap_changes(
    layer: Any, cache: dict[int, Any] | None = None
) -> list[outline_writer.Change]:
    """One row per shape whose merge changes its contours; notes for kept shapes.

    Edit: (shape, merged FontGate shape, old start points, contours after).
    Key: (shape index, contours after, node counts after).
    """
    shapes, notes = outline_writer.outline_shapes(layer)
    cache = {} if cache is None else cache
    rows = []
    for index, shape in enumerate(shapes):
        if outline_writer.translation(shape) != (0.0, 0.0):
            notes.append("moved shape, kept")
            continue
        if any(not contour.closed for contour in shape.contours):
            notes.append("open contour, kept")
            continue
        contours = list(shape.contours)
        intersects = any(
            a.hasIntersPoints(b)
            or (a.clockwise == b.clockwise and (a.contains(b) or b.contains(a)))
            for i, a in enumerate(contours)
            for b in contours[i + 1 :]
        )
        if not intersects:
            continue
        before = tuple(sorted(int(c.nodesCount) for c in contours))
        if shape.id not in cache:
            cache[shape.id] = fontgate_copy(shape, merge=True)
        result = cache[shape.id]
        after = node_counts(result)
        edit = (shape, result, start_points(shape), len(after))
        rows.append(
            outline_writer.Change(
                f"shape {index + 1}",
                outline_writer.plural(len(before), "contour"),
                outline_writer.plural(len(after), "contour"),
                edit,
                key=(index, len(after), after),
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


class MergeEditor(outline_writer.Editor):
    """Write the merged contours into the same shape; restore start points."""

    def __init__(self) -> None:
        self.before: dict[int, set[tuple[float, float]]] = {}
        self.advice: list[str] = []

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        """Snapshot existing save-risk conditions before any history starts."""
        for edit in edits:
            shape = edit[0]
            self.before[id(shape)] = final_smooth_points(shape.contours)
        return list(edits)

    def write(self, layer: Any, steps: list[Any]) -> None:
        for shape, result, starts, _ in steps:
            shape.assign(result)
            for contour in shape.contours:
                for index, (x, y, on) in enumerate(outline_writer.node_points(contour)):
                    if index and on and (round(x, 3), round(y, 3)) in starts:
                        contour.setStartPoint(index)
                        break
            shape.changed()

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed: list[str] = []
        for layer, steps in prepared:
            for shape, _, _, count in steps:
                introduced = (
                    final_smooth_points(shape.contours) - self.before[id(shape)]
                )
                if introduced:
                    message = (
                        f"{layer.name}: a final off-curve with raw Smooth was "
                        "introduced; FontLab may change on save (fl#8517). "
                        "Check node types after VFJ reopen."
                    )
                    if message not in self.advice:
                        self.advice.append(message)
                if len(shape.contours) != count:
                    missed.append(
                        f"{layer.name}: {len(shape.contours)} of {count} contours"
                    )
        return missed


class RemoveOverlap(outline_panel.panel_type()):
    """Master scope and compatibility; one row per merged shape."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Remove Overlap", "Merged", "shape"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Shape", "Now", "After")
    STRUCTURAL = True

    def planner(self) -> outline_writer.Planner:
        cache: dict[int, Any] = {}  # fresh for every scan and Apply
        return lambda glyph, master, layer: overlap_changes(layer, cache)

    def editor(self) -> outline_writer.Editor:
        self.risk_editor = MergeEditor()
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
    return scripting.show_script_dialog(RemoveOverlap, KEY)


if __name__ == "__main__":
    main()
