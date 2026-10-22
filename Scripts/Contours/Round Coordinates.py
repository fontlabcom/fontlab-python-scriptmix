# this_file: Scripts/Contours/Round Coordinates.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Round Coordinates
"""Round node coordinates, anchors and component offsets to a grid.

What: For each selected glyph and master, the table shows how many nodes are
off the grid and which component offsets change. Round snaps them to the
nearest multiple of the grid (1 unit by default).

How: A node is rounded in glyph coordinates. When its shape is moved (a
plain shape offset), the script rounds the visible position and stores the
matching local value, so the node lands on the grid where you see it. Halves
round up (2.5 -> 3, -2.5 -> -2), as Qt's qRound and Anchors > Round To Grid
do. Component offsets are rounded; the scale and slant of a component stay.
Nodes are moved in place, which is meant to keep node names and flags
(FontLab’s source; not measured).

Why: Scaling, interpolation and imports leave fractional or off-grid
coordinates. They cost file size and can cause rendering noise. Optional
anchor rounding uses fly.ap.anchor_writer in the same transaction. A layer
with ambiguous anchor names or an existing anchor that would move to 0, 0
is listed and kept (fl#8527).

Use: Select glyphs. Run the script. Set the grid and the masters; untick
"Component offsets" to keep them. Anchors starts ticked; untick Anchors to
round only nodes and offsets. Press Round. Press Reload selection after
you change the selection.

Benefit: Cleans many glyphs over many masters in one Undo step, and shows
the count before anything changes.

Safety: These shapes are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (their stored grid is not the visible
  grid);
- shapes moved by a fraction of a unit (FontLab may round the stored nodes,
  so the visible nodes could not land on the grid).

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
refuses before any history exists when FontLab holds queued glyph updates.
After the write, it reads every value back. If FontLab fails part-way, the
error says that native changes may remain. The change is recorded as one
Undo step. The one-step write, the automatic-layer rule, the pending-update
check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_round_coordinates.py,
Apache-2.0. Adapted for the current FontLab 9 API.
"""

import math
from typing import Any

import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402
import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt

QtGui = qt.QtGui
TITLE = "Round Coordinates"
KEY = "outlines_round_coordinates"


# ---------------------------------------------------------------- round logic
def snap(value: float, grid: int) -> float:
    """Nearest multiple of `grid`. Halves round up: 2.5 -> 3, -2.5 -> -2 (Qt's
    qRound).
    """
    return (
        float(math.floor(value / grid + 0.5) * grid) + 0.0
    )  # + 0.0 turns -0.0 into 0.0


def base_of(shape: Any) -> str:
    """Name of the glyph that a component shape refers to."""
    return str(shape.shapeData.componentGlyph)


def round_changes(layer: Any, grid: int, offsets: bool, anchors: bool = False) -> list[outline_writer.Change]:
    """Rows for one layer: off-grid nodes, then component offsets, then notes.

    Node edit: ("nodes", [(node, x, y)]) with x, y in shape coordinates.
    Offset edit: ("offset", shape, (dx, dy)).
    """
    anchor_edits = []
    if anchors:
        repeated = anchor_writer.duplicated(layer, [str(pin.name) for pin in layer.anchors])
        if repeated:
            return [outline_writer.Change("anchors", "", f"several anchors named {', '.join(repeated)}; layer kept")]
        for pin in layer.anchors:
            old = anchor_writer.raw_point(pin)
            new = (snap(old[0], grid), snap(old[1], grid))
            if old == new:
                continue
            if anchor_writer.on_origin(new):
                return [outline_writer.Change("anchors", "", "anchor would move to 0, 0; layer kept (fl#8527)")]
            anchor_edits.append(("set", str(pin.name), new))
    shapes, notes = outline_writer.outline_shapes(layer)
    moves = []
    for shape in shapes:
        dx, dy = outline_writer.translation(shape) or (0.0, 0.0)
        if (
            abs(snap(dx, 1) - dx) > outline_writer.EPSILON
            or abs(snap(dy, 1) - dy) > outline_writer.EPSILON
        ):
            notes.append("fractional shape offset, kept")
            continue
        for contour in shape.contours:
            for node in contour.nodes():
                x, y = float(node.x), float(node.y)
                nx, ny = snap(x + dx, grid) - dx, snap(y + dy, grid) - dy
                if (
                    abs(nx - x) > outline_writer.EPSILON
                    or abs(ny - y) > outline_writer.EPSILON
                ):
                    moves.append((node, nx, ny))
    rows = []
    if moves:
        rows.append(
            outline_writer.Change(
                "nodes", f"{len(moves)} off grid", f"on grid {grid}", ("nodes", moves)
            )
        )
    for shape in layer.shapes if offsets else ():
        if not shape.isComponent:
            continue
        old = (float(shape.transform.dx()), float(shape.transform.dy()))
        new = (snap(old[0], grid), snap(old[1], grid))
        if any(abs(new[i] - old[i]) > outline_writer.EPSILON for i in (0, 1)):
            rows.append(
                outline_writer.Change(
                    base_of(shape),
                    f"{outline_writer.fmt(old[0])}, {outline_writer.fmt(old[1])}",
                    f"{outline_writer.fmt(new[0])}, {outline_writer.fmt(new[1])}",
                    ("offset", shape, new),
                )
            )
    if anchor_edits:
        rows.append(outline_writer.Change("anchors", f"{len(anchor_edits)} off grid", f"on grid {grid}",
                                          ("anchors", anchor_edits)))
    return rows + outline_writer.note_rows(notes)


class RoundEditor(outline_writer.Editor):
    """Move nodes in place; set component offsets and keep their matrix."""

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        """Prepare native points before the shared history starts."""
        steps = []
        for step in edits:
            if step[0] != "anchors":
                steps.append(step)
                continue
            if anchor_writer.duplicated(layer, [name for _, name, _ in step[1]]):
                raise ValueError("Several anchors share a name; layer kept.")
            if any(anchor_writer.on_origin(value) for _, _, value in step[1]):
                raise ValueError("Anchor would move to 0, 0 (fl#8527).")
            steps.append(("anchors", anchor_writer.prepare(layer, step[1]), step[1]))
        return steps

    def write(self, layer: Any, steps: list[Any]) -> None:
        for step in steps:
            if step[0] == "anchors":
                anchor_writer.write(layer, step[1])
                continue
            if step[0] == "nodes":
                for node, x, y in step[1]:
                    node.x, node.y = x, y
                continue
            _, shape, (dx, dy) = step
            matrix = shape.transform
            shape.transform = QtGui.QTransform(
                matrix.m11(), matrix.m12(), matrix.m21(), matrix.m22(), dx, dy
            )
            shape.changed()

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed: list[str] = []
        for layer, steps in prepared:
            for step in steps:
                if step[0] == "anchors":
                    points = anchor_writer.anchor_points(layer)
                    missed.extend(f"{layer.name}/{name}" for _, name, value in step[2]
                                  if points.get(name) != value)
                    continue
                if step[0] == "nodes":
                    wrong = [
                        1
                        for node, x, y in step[1]
                        if abs(node.x - x) > 0.01 or abs(node.y - y) > 0.01
                    ]
                    if wrong:
                        missed.append(
                            f"{layer.name}: {outline_writer.plural(len(wrong), 'node')}"
                        )
                    continue
                _, shape, (dx, dy) = step
                matrix = shape.transform
                if abs(matrix.dx() - dx) > 0.01 or abs(matrix.dy() - dy) > 0.01:
                    missed.append(f"{layer.name}/{base_of(shape)}")
        return missed


class RoundCoordinates(outline_panel.panel_type()):
    """Grid, component option and master scope; one row per layer item."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Round", "Rounded", "item"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Item", "Now", "After")

    def build_controls(self) -> None:
        self.grid = self.spin(1, 100, 1, " units")
        self.anchors = QtGui.QCheckBox("Anchors")
        self.anchors.setChecked(True)
        self.offsets = QtGui.QCheckBox("Component offsets")
        self.offsets.setChecked(True)
        self.add_row("Grid", self.grid, self.anchors, self.offsets)
        self.watch(self.anchors.toggled)
        self.watch(self.offsets.toggled)

    def planner(self) -> outline_writer.Planner:
        grid, offsets = int(self.grid.value), self.offsets.isChecked()
        if grid < 1:
            raise ValueError("The grid must be 1 unit or more.")
        anchors = self.anchors.isChecked()
        return lambda glyph, master, layer: round_changes(layer, grid, offsets, anchors)

    def editor(self) -> outline_writer.Editor:
        return RoundEditor()


def main() -> Any:
    """Open the panel, or replace the one that is already open."""
    return scripting.show_script_dialog(RoundCoordinates, KEY)


if __name__ == "__main__":
    main()
