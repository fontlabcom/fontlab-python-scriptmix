# this_file: Scripts/Contours/Add Extremes.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Add Extremes
"""Add on-curve nodes at the horizontal and vertical extremes of curves.

What: For each selected glyph and master, the table lists every contour
whose curves have an extreme without a node: the node count now and the
number of extremes to add. Add Extremes inserts them.

How: For each cubic curve, the script solves the derivative of x and of y
for t; extremes closer than 2 % of the parameter t to an end node are
ignored. FontLab's own split, flContour.insertNodeTo, inserts each node, so
the curve keeps its shape up to FontLab's rounding of the new node. Cuts
within 0.1 Manhattan units of an end or an earlier cut are not offered. The
splits run from the last curve back, so the segment numbers of the earlier
curves stay valid. TrueType (quadratic) contours and open contours are left
alone.

Why: Fonts need nodes at extremes for good hinting and rasterisation, and
font tests flag missing extremes. With "Keep masters compatible" ticked, a
glyph is held back when the masters would get different nodes, or when only
some masters are in scope: different nodes break interpolation.

Use: Select glyphs. Run the script. Choose the masters. Press Add Extremes.
Press Reload selection after you change the selection.

Benefit: Fixes many glyphs over many masters in one Undo step, and keeps the
masters compatible.

Safety: These shapes are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (an extreme in stored coordinates is
  not an extreme on screen).

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
refuses before any history exists when FontLab holds queued glyph updates.
After the write, it reads the node counts back. If FontLab fails part-way,
the error says that native changes may remain. The change is recorded as one
Undo step. The one-step write, the automatic-layer rule, the pending-update
check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_add_extremes.py,
Apache-2.0. Adapted for the current FontLab 9 API.
"""

import math
from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

TITLE = "Add Extremes"
KEY = "outlines_add_extremes"
MARGIN = 0.02  # ignore extremes this close (in t) to a curve end


# ---------------------------------------------------------------- extremes logic
XY = tuple[float, float]
Cubic = tuple[XY, XY, XY, XY]


def segments(points: list[outline_writer.Point]) -> list[tuple[int, Cubic]]:
    """[(segment number, cubic)] of a closed contour whose node 0 is on-curve.

    Segment k runs from the k-th on-curve node to the next one, as FontLab's
    contour parameter t counts them. Lines get a number but no cubic.
    """
    result: list[tuple[int, Cubic]] = []
    start, handles, k = points[0][:2], [], 0
    for x, y, on in points[1:] + points[:1]:
        if not on:
            handles.append((x, y))
            continue
        if len(handles) == 2:
            result.append((k, (start, handles[0], handles[1], (x, y))))
        k += 1
        start, handles = (x, y), []
    return result


def roots(a: float, b: float, c: float) -> list[float]:
    """Real roots of a t² + b t + c inside (MARGIN, 1 - MARGIN), rounded to 6
    places.
    """
    if abs(a) < 1e-9:
        found = [-c / b] if abs(b) > 1e-9 else []
    else:
        disc = b * b - 4 * a * c
        if disc < 0:
            return []
        q = math.sqrt(disc)
        found = [(-b + q) / (2 * a), (-b - q) / (2 * a)]
    return sorted({round(t, 6) for t in found if MARGIN < t < 1 - MARGIN})


def extremes(p0: XY, p1: XY, p2: XY, p3: XY) -> list[float]:
    """Parameters t of the x and y extremes of one cubic, sorted."""
    found: set[float] = set()
    for axis in (0, 1):
        a = -p0[axis] + 3 * p1[axis] - 3 * p2[axis] + p3[axis]
        b = 2 * (p0[axis] - 2 * p1[axis] + p2[axis])
        c = p1[axis] - p0[axis]
        found.update(roots(a, b, c))
    return sorted(found)


def contour_plan(points: list[outline_writer.Point]) -> list[tuple[int, list[float]]]:
    """[(segment number, [t, ...])] of one closed contour; [] when node 0 is off-curve."""
    if not points or not points[0][2]:
        return []
    result = []
    for k, cubic in segments(points):
        cuts, accepted = [], [cubic[0], cubic[3]]
        for t in reversed(extremes(*cubic)):
            u = 1 - t
            point = tuple(
                u**3 * cubic[0][axis]
                + 3 * u * u * t * cubic[1][axis]
                + 3 * u * t * t * cubic[2][axis]
                + t**3 * cubic[3][axis]
                for axis in (0, 1)
            )
            if any(
                abs(point[0] - p[0]) + abs(point[1] - p[1]) < 0.1002 for p in accepted
            ):
                continue
            cuts.append(t)
            accepted.append(point)
        if cuts:
            result.append((k, sorted(cuts)))
    return result


def insert_extremes(contour: Any, plan: list[tuple[int, list[float]]]) -> int:
    """Insert the planned nodes from the last segment back. Return the number
    added.

    After a split at t, the earlier part of the segment is the whole segment
    again, so the next lower parameter becomes t / previous t.
    """
    added = 0
    for k, ts in sorted(plan, reverse=True):
        upper = 1.0
        for t in sorted(ts, reverse=True):
            contour.insertNodeTo(k + t / upper)
            upper = t
            added += 1
    return added


def extreme_changes(layer: Any) -> list[outline_writer.Change]:
    """One row per contour that gets extremes; notes for kept shapes.

    Edit: (contour, plan, node count after). Key: (contour number, plan
    shape).
    """
    shapes, notes = outline_writer.outline_shapes(layer)
    rows, number = [], 0
    for shape in shapes:
        for contour in shape.contours:
            number += 1
            if not contour.closed or contour.isTT:
                continue
            plan = contour_plan(outline_writer.node_points(contour))
            count = sum(len(ts) for _, ts in plan)
            if not count:
                continue
            nodes = int(contour.nodesCount)
            rows.append(
                outline_writer.Change(
                    f"contour {number}",
                    outline_writer.plural(nodes, "node"),
                    f"+{outline_writer.plural(count, 'extreme')}",
                    (contour, plan, nodes + 3 * count),
                    key=(number, tuple((k, len(ts)) for k, ts in plan)),
                )
            )
    return rows + outline_writer.note_rows(notes)


class ExtremesEditor(outline_writer.Editor):
    """Split curves at their extremes with FontLab's own insertNodeTo."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        for contour, plan, _ in steps:
            insert_extremes(contour, plan)

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed: list[str] = []
        for layer, steps in prepared:
            for contour, _, count in steps:
                if int(contour.nodesCount) != count:
                    missed.append(
                        f"{layer.name}: {contour.nodesCount} of {count} nodes"
                    )
        return missed


class AddExtremes(outline_panel.panel_type()):
    """Master scope and compatibility; one row per contour."""

    TITLE, KEY, ACTION, DONE, UNIT = (
        TITLE,
        KEY,
        "Add Extremes",
        "Added extremes to",
        "contour",
    )
    HEADERS: tuple[str, ...] = ("Glyph · master", "Contour", "Now", "Adds")
    STRUCTURAL = True

    def planner(self) -> outline_writer.Planner:
        return lambda glyph, master, layer: extreme_changes(layer)

    def editor(self) -> outline_writer.Editor:
        return ExtremesEditor()


def main() -> Any:
    """Open the panel, or replace the one that is already open."""
    return scripting.show_script_dialog(AddExtremes, KEY)


if __name__ == "__main__":
    main()
