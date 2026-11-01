# this_file: Scripts/Contours/Straighten Short Curves.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Straighten Short Curves
"""Turn short, flat curves into straight lines.

What: For each selected glyph and master, the table lists every contour with
curves that are short and flat: the number of curves now, how many become
lines, and the largest handle deviation. Straighten converts them.

How: A cubic curve qualifies when its chord is no longer than "Chord up to"
and both handles lie within "Handles within" of the chord, between its ends.
FontLab's own flNode.convertToLine, called on the end node of the curve,
removes the two handles and recomputes the smooth flags at both ends.
TrueType (quadratic) contours are left alone.

Why: Autotracing and format conversion leave tiny curves that are really
lines. As lines they hint better, interpolate more safely and take less
space. With "Keep masters compatible" ticked, a glyph is held back when the
masters would get different curves, or when only some masters are in scope.

Use: Select glyphs. Run the script. Set the two limits and the masters.
Press Straighten. Press Reload selection after you change the selection.

Benefit: Cleans many glyphs over many masters in one Undo step, with the
worst deviation shown before anything changes.

Safety: These shapes are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (stored lengths are not visible
  lengths).

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
keeps the compatibility check; writes disclose queued ids and possible date
changes.
After the write, it reads the node counts back. If FontLab fails part-way,
the error says that native changes may remain. The change is recorded as one
Undo step. The one-step write, the automatic-layer rule, the pending-update
check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_straighten_short_curves.py,
Apache-2.0. Adapted for the current FontLab 9 API.
"""

import math
from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

TITLE = "Straighten Short Curves"
KEY = "outlines_straighten_short_curves"


# ---------------------------------------------------------------- straighten logic
XY = tuple[float, float]


def cubic_segments(
    points: list[outline_writer.Point],
) -> list[tuple[int, int, int, int]]:
    """(i0, i1, i2, i3) node indices of every cubic curve of a closed contour."""
    on = [i for i, p in enumerate(points) if p[2]]
    result = []
    for k, start in enumerate(on):
        end = on[(k + 1) % len(on)]
        span = (end - start) % len(points) or len(points)
        between = [(start + j) % len(points) for j in range(1, span)]
        if len(between) == 2:
            result.append((start, between[0], between[1], end))
    return result


def chord_offset(point: XY, a: XY, b: XY) -> tuple[float, float]:
    """(distance from the line ab, position along ab as a fraction of its
    length).
    """
    (px, py), (ax, ay), (bx, by) = point, a, b
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length == 0:
        return math.hypot(px - ax, py - ay), 0.0
    distance = abs((px - ax) * dy - (py - ay) * dx) / length
    return distance, ((px - ax) * dx + (py - ay) * dy) / (length * length)


def straight_segments(
    points: list[outline_writer.Point], max_length: float, tolerance: float
) -> list[tuple[int, int, float]]:
    """[(start index, end index, deviation)] of curves short and flat enough."""
    found = []
    for i0, i1, i2, i3 in cubic_segments(points):
        a, b = points[i0][:2], points[i3][:2]
        length = math.dist(a, b)
        if length == 0 or length > max_length:
            continue
        d1, t1 = chord_offset(points[i1][:2], a, b)
        d2, t2 = chord_offset(points[i2][:2], a, b)
        if max(d1, d2) <= tolerance and 0 <= t1 <= 1 and 0 <= t2 <= 1:
            found.append((i0, i3, max(d1, d2)))
    return found


def straighten_changes(
    layer: Any, max_length: float, tolerance: float
) -> list[outline_writer.Change]:
    """One row per contour with curves to straighten; notes for kept shapes.

    Edit: (contour, end nodes of the curves, node count after).
    Key: (contour number, start indices of the curves).
    """
    shapes, notes = outline_writer.outline_shapes(layer)
    rows, number = [], 0
    for shape in shapes:
        for contour in shape.contours:
            number += 1
            if contour.isTT:
                continue
            points = outline_writer.node_points(contour)
            curves = cubic_segments(points)
            found = straight_segments(points, max_length, tolerance)
            if not found:
                continue
            nodes = contour.nodes()
            ends = [nodes[i3] for _, i3, _ in found]
            worst = max(deviation for _, _, deviation in found)
            rows.append(
                outline_writer.Change(
                    f"contour {number}",
                    outline_writer.plural(len(curves), "curve"),
                    f"{len(found)} to lines (max {worst:.1f})",
                    (contour, ends, len(points) - 2 * len(found)),
                    key=(number, tuple(i0 for i0, _, _ in found)),
                )
            )
    return rows + outline_writer.note_rows(notes)


class LineEditor(outline_writer.Editor):
    """Convert curves to lines with FontLab's own flNode.convertToLine."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        for _, ends, _ in steps:
            for node in ends:  # node objects stay valid while indices shift
                if node.convertToLine() is False:
                    raise RuntimeError(
                        f"FontLab did not straighten a curve in {layer.name}."
                    )

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed: list[str] = []
        for layer, steps in prepared:
            for contour, _, count in steps:
                if int(contour.nodesCount) != count:
                    missed.append(
                        f"{layer.name}: {contour.nodesCount} of {count} nodes"
                    )
        return missed


class StraightenShortCurves(outline_panel.panel_type()):
    """Length and tolerance limits plus master scope; one row per contour."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Straighten", "Straightened", "contour"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Contour", "Curves", "Change")
    STRUCTURAL = True

    def build_controls(self) -> None:
        self.max_length = self.spin(1, 2000, 60, " units")
        self.tolerance = self.spin(0, 50, 2, " units", decimals=1)
        self.add_row("Chord up to", self.max_length)
        self.add_row("Handles within", self.tolerance)

    def planner(self) -> outline_writer.Planner:
        limit, tolerance = float(self.max_length.value), float(self.tolerance.value)
        return lambda glyph, master, layer: straighten_changes(layer, limit, tolerance)

    def editor(self) -> outline_writer.Editor:
        return LineEditor()


def main() -> Any:
    """Open the panel, or replace the one that is already open."""
    return scripting.show_script_dialog(StraightenShortCurves, KEY)


if __name__ == "__main__":
    main()
