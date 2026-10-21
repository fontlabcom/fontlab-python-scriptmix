# this_file: Scripts/Contours/Delete Duplicate Contours.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Delete Duplicate Contours
"""Find contours drawn twice in the same layer and keep only the first copy.

What: For each selected glyph and master, the table lists every contour that
repeats an earlier contour of the same layer. Delete removes the copies.

How: Two contours are duplicates when they have the same nodes in the same
cyclic order, from any start node in the same direction, and each node pair
lies within the tolerance (in glyph coordinates, so moved shapes compare
where you see them). On-curve and off-curve nodes must match. The first
contour of a group stays; FontLab's own flShape.removeContour removes the
others.

Reversed duplicate groups are listed as "reversed duplicate, kept". Every
member stays, including further copies: their winding can cancel. Open
contours are kept; cyclic rotation changes their open endpoints.

Why: Same-direction duplicates are invisible in a filled preview, but they
break overlap removal, double the ink in some renderers and confuse contour
order tools. With "Keep masters compatible" ticked, a glyph is held back
when the masters would lose different contours, or when only some masters
are in scope.

Use: Select glyphs. Run the script. Set the tolerance and the masters. Press
Delete. Press Reload selection after you change the selection.

Benefit: Removes hidden copies over many glyphs and masters in one Undo
step, and names the contour each copy repeats.

Safety: These shapes are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (stored nodes are not visible nodes).

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

Source: the author's own FontLab sample
outlines_delete_duplicate_contours.py, Apache-2.0. Adapted for the current
FontLab 9 API.
"""

from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

TITLE = "Delete Duplicate Contours"
KEY = "outlines_delete_duplicate_contours"


# ---------------------------------------------------------------- duplicate logic
def same_cycle(
    a: list[outline_writer.Point], b: list[outline_writer.Point], tolerance: float
) -> bool:
    """True when `a` and `b` are the same closed node sequence, any start, same
    direction.
    """
    if len(a) != len(b) or not a:
        return False

    def close(p: outline_writer.Point, q: outline_writer.Point) -> bool:
        return (
            p[2] == q[2]
            and abs(p[0] - q[0]) <= tolerance
            and abs(p[1] - q[1]) <= tolerance
        )

    for shift in range(len(b)):
        rotated = b[shift:] + b[:shift]
        if all(close(p, q) for p, q in zip(a, rotated, strict=True)):
            return True
    return False


def duplicate_changes(layer: Any, tolerance: float) -> list[outline_writer.Change]:
    """One row per contour that repeats an earlier one; notes for kept shapes.

    Edit: (shape, contour). Key: the contour number.
    """
    shapes, notes = outline_writer.outline_shapes(layer)
    items = []
    for shape in shapes:
        dx, dy = outline_writer.translation(shape) or (0.0, 0.0)
        for contour in shape.contours:
            if not contour.closed:
                notes.append("open contour, kept")
                continue
            points = [
                (x + dx, y + dy, on) for x, y, on in outline_writer.node_points(contour)
            ]
            items.append((shape, contour, points))
    # Protect both sides before scheduling any deletion, including A/A/reverse(A).
    protected = {
        i
        for i, (_, _, points) in enumerate(items)
        if any(
            i != j and same_cycle(points, other[::-1], tolerance)
            for j, (_, _, other) in enumerate(items)
        )
    }
    rows = []
    seen: list[tuple[int, list[outline_writer.Point]]] = []
    for i, (shape, contour, points) in enumerate(items):
        number = i + 1
        if i in protected:
            rows.append(
                outline_writer.Change(
                    f"contour {number}", "", "reversed duplicate, kept"
                )
            )
            continue
        first = next(
            (n for n, other in seen if same_cycle(other, points, tolerance)), None
        )
        if first is None:
            seen.append((number, points))
        else:
            rows.append(
                outline_writer.Change(
                    f"contour {number}",
                    f"same as contour {first}",
                    "delete",
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


class DeleteDuplicateContours(outline_panel.panel_type()):
    """Tolerance plus master scope; one row per duplicate."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Delete", "Deleted", "contour"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Contour", "Repeats", "Action")
    STRUCTURAL = True

    def build_controls(self) -> None:
        self.tolerance = self.spin(0, 20, 0.5, " units", decimals=1)
        self.add_row("Tolerance", self.tolerance)

    def planner(self) -> outline_writer.Planner:
        tolerance = float(self.tolerance.value)
        return lambda glyph, master, layer: duplicate_changes(layer, tolerance)

    def editor(self) -> outline_writer.Editor:
        return RemoveEditor()


def main() -> Any:
    """Open the panel, or replace the one that is already open."""
    return scripting.show_script_dialog(DeleteDuplicateContours, KEY)


if __name__ == "__main__":
    main()
