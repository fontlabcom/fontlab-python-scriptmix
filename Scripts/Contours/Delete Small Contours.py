# this_file: Scripts/Contours/Delete Small Contours.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Delete Small Contours
"""Delete contours whose area is below a threshold: specks from drawing or
tracing.

What: For each selected glyph and master, the table lists every contour
smaller than the threshold, with its area and position. Delete removes them.

How: The area is the exact area of the curves in square font units, measured
by fly.ap.contour_selection.unsigned_area (FontTools' area pen). Open
contours are listed as "open contour, kept" and are never deleted. A contour
counts as small when its area is strictly below the threshold. This is the
same rule as Contours > Select Small Contours, so you can select first and
look, then delete with the same number. FontLab's own flShape.removeContour
removes each contour.

Why: Specks are hard to see in a filled preview but end up in the font. With
"Keep masters compatible" ticked, a glyph is held back when the masters
would lose different contours, or when only some masters are in scope:
different contour counts break interpolation.

Use: Select glyphs. Run the script. Set the threshold and the masters. Press
Delete. Press Reload selection after you change the selection.

Benefit: Removes specks over many glyphs and masters in one Undo step, and
shows each one first.

Safety: These shapes are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (stored areas are not visible areas).

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
keeps the compatibility check; writes disclose queued ids and possible date
changes.
The area needs FontTools (fontlab-fontlabapp[fontui]); without it the status
line says so and nothing changes. After the write, the script reads the
contour counts back. If FontLab fails part-way, the error says that native
changes may remain. The change is recorded as one Undo step. The one-step
write, the automatic-layer rule, the pending-update check and the panel are
shared (fly.ap.outline_writer, fly.ap.outline_panel); the planner belongs to
this script.

Source: the author's own FontLab sample outlines_delete_small_contours.py,
Apache-2.0. Adapted for the current FontLab 9 API.
"""

from itertools import pairwise
from typing import Any

import fly.ap.contour_selection as contour_selection  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

TITLE = "Delete Small Contours"
KEY = "outlines_delete_small_contours"


# ---------------------------------------------------------------- area logic
XY = tuple[float, float]


def segments_of(
    points: list[outline_writer.Point], truetype: bool
) -> tuple[tuple[XY, ...], ...]:
    """Continuous line and Bezier segments of a contour, closed for measurement.

    PostScript: two controls make a cubic. TrueType: a run of controls is a
    quadratic spline; the implied on-curve points lie half-way between two
    controls. Return () when the contour has no on-curve node.
    """
    start = next((i for i, p in enumerate(points) if p[2]), None)
    if start is None:
        return ()
    ring = points[start + 1 :] + points[: start + 1]
    current: XY = points[start][:2]
    result: list[tuple[XY, ...]] = []
    controls: list[XY] = []
    for x, y, on in ring:
        if not on:
            controls.append((x, y))
            continue
        end = (x, y)
        if not controls:
            result.append((current, end))
        elif not truetype and len(controls) == 2:
            result.append((current, controls[0], controls[1], end))
        else:
            for a, b in pairwise(controls):
                middle = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                result.append((current, a, middle))
                current = middle
            result.append((current, controls[-1], end))
        current, controls = end, []
    return tuple(result)


def small_changes(layer: Any, threshold: float) -> list[outline_writer.Change]:
    """One row per contour with area below `threshold`; notes for kept shapes.

    Edit: (shape, contour). Key: the contour number.
    """
    shapes, notes = outline_writer.outline_shapes(layer)
    rows, number = [], 0
    for shape in shapes:
        dx, dy = outline_writer.translation(shape) or (0.0, 0.0)
        for contour in shape.contours:
            number += 1
            if not contour.closed:
                notes.append("open contour, kept")
                continue
            points = outline_writer.node_points(contour)
            parts = segments_of(points, bool(contour.isTT))
            if not parts:
                continue
            area = contour_selection.unsigned_area(parts)
            if area >= threshold:
                continue
            x = min(p[0] for p in points) + dx
            y = min(p[1] for p in points) + dy
            rows.append(
                outline_writer.Change(
                    f"contour {number}",
                    f"area {area:.0f}",
                    f"delete at {outline_writer.fmt(x)}, {outline_writer.fmt(y)}",
                    (shape, contour),
                    key=number,
                )
            )
    return rows + outline_writer.note_rows(notes)


class RemoveEditor(outline_writer.Editor):
    """Remove contours with FontLab's own flShape.removeContour."""

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        counts: dict[int, int] = {}
        for shape, _ in edits:
            counts[id(shape)] = counts.get(id(shape), len(shape.contours)) - 1
        return [(shape, contour, counts[id(shape)]) for shape, contour in edits]

    def write(self, layer: Any, steps: list[Any]) -> None:
        for shape, contour, _ in steps:
            shape.removeContour(contour)
            shape.changed()

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed: list[str] = []
        for layer, steps in prepared:
            for shape, _, count in steps:
                if len(shape.contours) != count:
                    missed.append(
                        f"{layer.name}: {len(shape.contours)} of {count} contours"
                    )
        return sorted(set(missed))


class DeleteSmallContours(outline_panel.panel_type()):
    """Area threshold plus master scope; one row per small contour."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Delete", "Deleted", "contour"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Contour", "Area", "Action")
    STRUCTURAL = True

    def build_controls(self) -> None:
        self.threshold = self.spin(1, 1000000, 400, " units²")
        self.threshold.setSingleStep(100)
        self.add_row("Smaller than", self.threshold)

    def planner(self) -> outline_writer.Planner:
        limit = float(self.threshold.value)
        return lambda glyph, master, layer: small_changes(layer, limit)

    def editor(self) -> outline_writer.Editor:
        return RemoveEditor()


def main() -> Any:
    """Open the panel, or replace the one that is already open."""
    return scripting.show_script_dialog(DeleteSmallContours, KEY)


if __name__ == "__main__":
    main()
