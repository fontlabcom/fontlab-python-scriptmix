# this_file: Scripts/Contours/Fix Zero Handles.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Fix Zero Handles
"""Find curve handles that sit on their own node, and clean them up.

What: For each selected glyph and master, the table lists every contour with
retracted handles: curves whose two handles both sit on their nodes, and
curves with one such handle. Fix turns the first kind into lines and, when
you ask for it, pulls single handles out.

How: A handle counts as retracted when it is closer than half a unit to its
own node. A curve with two retracted handles is a straight line in disguise:
FontLab's own flNode.convertToLine, called on the end node, removes the
handles and resets the smooth flags. With "Pull single handles out to ⅓", a
lone retracted handle moves a third of the way towards the other handle: the
curve then has a real tangent at that node, but its shape changes slightly.
TrueType (quadratic) contours are left alone.

Why: Retracted handles give a zero tangent: hinting, offsetting, stroke
expansion and some rasterisers handle them badly. With "Keep masters
compatible" ticked, a glyph is held back when the masters would get
different curves, or when only some masters are in scope.

Use: Select glyphs. Run the script. Choose the option and the masters. Press
Fix. Press Reload selection after you change the selection.

Benefit: Finds and fixes a common outline fault over many glyphs and masters
in one Undo step.

Safety: Pulling a single handle on a Smooth base can leave the handles
non-collinear. FontLab may later align them again. Converting a curve to a
line recomputes the smooth flags at both ends. These shapes are listed and
kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (stored distances are not visible
  distances).

A pulled handle lands on a whole unit, a third of the way to the other
handle, so FontLab's rounding preference cannot move it again.

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
keeps the compatibility check; writes disclose queued ids and possible date
changes.
After the write, it reads node counts and handle positions back. If FontLab
fails part-way, the error says that native changes may remain. The change is
recorded as one Undo step. The one-step write, the automatic-layer rule, the
pending-update check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_fix_zero_handles.py,
Apache-2.0. Adapted for the current FontLab 9 API.
"""

import math
from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt

QtGui = qt.QtGui
TITLE = "Fix Zero Handles"
KEY = "outlines_fix_zero_handles"
ZERO = 0.5  # a handle closer than this to its node counts as retracted
PULL_LABEL = "Pull single handles out to ⅓ (changes the curve slightly)"


# ---------------------------------------------------------------- handle logic
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


def zero_handles(
    points: list[outline_writer.Point],
) -> tuple[list[tuple[int, int]], list[tuple[int, int, int]]]:
    """(curves to make lines, single retracted handles).

    Lines: (start index, end index). Singles: (handle, its node, other
    handle).
    """
    lines, singles = [], []
    for i0, i1, i2, i3 in cubic_segments(points):
        first = math.dist(points[i0][:2], points[i1][:2]) < ZERO
        second = math.dist(points[i3][:2], points[i2][:2]) < ZERO
        if first and second:
            lines.append((i0, i3))
        elif first:
            singles.append((i1, i0, i2))
        elif second:
            singles.append((i2, i3, i1))
    return lines, singles


def third(base: float, other: float) -> float:
    """A third of the way from `base` to `other`, rounded half up to a whole
    unit.

    A whole unit survives FontLab's strong rounding, so the preview, the
    stored value and the read-back agree.
    """
    return float(math.floor(base + (other - base) / 3.0 + 0.5)) + 0.0


def zero_changes(layer: Any, pull: bool) -> list[outline_writer.Change]:
    """One row per contour with retracted handles; notes for kept shapes.

    Edit: (contour, end nodes of the lines, [(handle node, x, y)], node count
    after). Key: (contour number, start indices of the lines), or None when
    only handles move.
    """
    shapes, notes = outline_writer.outline_shapes(layer)
    rows, number = [], 0
    for shape in shapes:
        for contour in shape.contours:
            number += 1
            if contour.isTT:
                continue
            points = outline_writer.node_points(contour)
            lines, singles = zero_handles(points)
            if not lines and not singles:
                continue
            nodes = contour.nodes()
            moves = []
            for handle, base, other in singles if pull else ():
                (bx, by), (ox, oy) = points[base][:2], points[other][:2]
                x, y = third(bx, ox), third(by, oy)
                if (
                    math.hypot(x - bx, y - by) >= 0.5
                ):  # else it rounds back onto its node
                    moves.append((nodes[handle], x, y))
            found = f"{outline_writer.plural(len(lines), 'line')}, {outline_writer.plural(len(singles), 'single')}"
            if not lines and not moves:
                rows.append(
                    outline_writer.Change(
                        f"contour {number}", found, "single handles kept"
                    )
                )
                continue
            done = [f"{len(lines)} to lines"] if lines else []
            done += [f"{len(moves)} pulled"] if moves else []
            key = (number, tuple(i0 for i0, _ in lines)) if lines else None
            ends = [nodes[i3] for _, i3 in lines]
            edit = (contour, ends, moves, len(points) - 2 * len(lines))
            rows.append(
                outline_writer.Change(
                    f"contour {number}", found, ", ".join(done), edit, key=key
                )
            )
    return rows + outline_writer.note_rows(notes)


class HandleEditor(outline_writer.Editor):
    """Pull single handles, then convert double-zero curves to lines.

    The node objects come from the plan, so the order is safe: pulls do not
    move indices, and convertToLine finds its curve from its own node.
    """

    def write(self, layer: Any, steps: list[Any]) -> None:
        for _, ends, moves, _ in steps:
            for node, x, y in moves:
                node.x, node.y = x, y
            for node in ends:
                if node.convertToLine() is False:
                    raise RuntimeError(
                        f"FontLab did not straighten a curve in {layer.name}."
                    )

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed: list[str] = []
        for layer, steps in prepared:
            for contour, _, moves, count in steps:
                if int(contour.nodesCount) != count:
                    missed.append(
                        f"{layer.name}: {contour.nodesCount} of {count} nodes"
                    )
                if any(abs(n.x - x) > 0.01 or abs(n.y - y) > 0.01 for n, x, y in moves):
                    missed.append(f"{layer.name}: a handle did not move")
        return missed


class FixZeroHandles(outline_panel.panel_type()):
    """Pull option plus master scope; one row per contour."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Fix", "Fixed", "contour"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Contour", "Found", "Fix")
    STRUCTURAL = True

    def build_controls(self) -> None:
        self.pull = QtGui.QCheckBox(PULL_LABEL)
        self.add_row("", self.pull)
        self.watch(self.pull.toggled)

    def planner(self) -> outline_writer.Planner:
        pull = self.pull.isChecked()
        return lambda glyph, master, layer: zero_changes(layer, pull)

    def editor(self) -> outline_writer.Editor:
        return HandleEditor()


def main() -> Any:
    """Open the panel, or replace the one that is already open."""
    return scripting.show_script_dialog(FixZeroHandles, KEY)


if __name__ == "__main__":
    main()
