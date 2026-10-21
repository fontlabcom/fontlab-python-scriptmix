# this_file: Scripts/Contours/Interpolated Nudge.py
# SPDX-License-Identifier: MIT
"""Move selected endpoints while keeping adjacent handle tension.

What: Move selected endpoints while keeping adjacent handle tension. How: Plan
simultaneous moves from original coordinates. The moved node's own handles also scale.
Clamp per-axis handle factors to 0 through 4; zero collapses a handle at its endpoint
instead of flipping it. Tiny axis spans use rigid movement. Read-back allows 0.5 unit
per axis for native rounding. Adjacent handles can lose collinearity at smooth nodes;
inspect these nodes after a move. Scale each neighbouring handle about its endpoint by
the changed endpoint distance in each axis. Keep ratios when an axis span is zero. Why:
Adjust outlines with less handle repair. Use: Select on-curve nodes in the glyph editor,
reload the panel, set X and Y, then Apply. Repeat as needed. Benefit: A repeatable non-
modal nudge with one history action per Apply.

The non-modal panel previews the selected glyphs and chosen masters. Shared, scaled and
rotated outline shapes are kept. Automatic-layer owners are kept. Bases of automatic
composites are kept unless the shared consent option is enabled. Each Apply is recorded
as one Undo step through the App history writer. Reload after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Interpolated Nudge.py,
MIT, copyright 2017 Simon Cozens. Repository:
https://github.com/simoncozens/GlyphsScripts . No source code was copied.
"""

import math
from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - native package lookup
import fly.ap.outline_writer as writer
import fly.ap.scripting as scripting  # noqa: PLR0402 - native package lookup

TITLE = "Interpolated Nudge"
KEY = "cozens_interpolated_nudge"


def nudged(
    points: list[tuple[float, float, bool]], selected: set[int], dx: float, dy: float
) -> list[tuple[float, float]]:
    """Scale cubic handles between simultaneously moved original endpoints."""
    if not math.isfinite(dx) or not math.isfinite(dy):
        raise ValueError("Nudge distances must be finite.")
    on = [i for i, point in enumerate(points) if point[2]]
    if not selected or not selected.issubset(set(on)):
        raise ValueError("Select one or more on-curve nodes.")
    shifts = {i: (dx, dy) if i in selected else (0.0, 0.0) for i in on}
    result = [(point[0], point[1]) for point in points]
    for index, start in enumerate(on):
        end = on[(index + 1) % len(on)]
        distance = (end - start) % len(points) or len(points)
        inside = [(start + j) % len(points) for j in range(1, distance)]
        if len(inside) not in (0, 2):
            raise ValueError("Use line or cubic segments.")
        for control, anchor in zip(inside, (start, end)):
            values = []
            for axis in (0, 1):
                span = points[end][axis] - points[start][axis]
                delta = shifts[end][axis] - shifts[start][axis]
                factor = (
                    max(0.0, min(4.0, (span + delta) / span))
                    if abs(span) > 1e-9
                    else 1.0
                )
                values.append(
                    points[anchor][axis]
                    + shifts[anchor][axis]
                    + (points[control][axis] - points[anchor][axis]) * factor
                )
            result[control] = tuple(values)
    for index in on:
        result[index] = tuple(
            points[index][axis] + shifts[index][axis] for axis in (0, 1)
        )
    return result


def changes(layer: Any, dx: float, dy: float) -> list[writer.Change]:
    """Plan selected endpoints from one coordinate snapshot per contour."""
    shapes, notes = writer.outline_shapes(layer)
    rows = []
    for shape in shapes:
        for contour in shape.contours:
            if contour.isTT or not contour.closed:
                notes.append("open or quadratic contour, kept")
                continue
            nodes = list(contour.nodes())
            selected = {i for i, n in enumerate(nodes) if n.selected and n.isOn()}
            if not selected:
                continue
            result = nudged(writer.node_points(contour), selected, dx, dy)
            moves = [
                (node, x, y)
                for node, (x, y) in zip(nodes, result)
                if abs(node.x - x) > 1e-6 or abs(node.y - y) > 1e-6
            ]
            if moves:
                rows.append(
                    writer.Change(
                        "selected nodes", str(len(selected)), f"{dx:g}, {dy:g}", moves
                    )
                )
    if not rows:
        notes.append("select on-curve nodes and set a nonzero nudge")
    return rows + writer.note_rows(notes)


class NudgeEditor(writer.Editor):
    """Move original node objects; compare all planned positions after write."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        for moves in steps:
            for node, x, y in moves:
                node.x, node.y = x, y

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        return [
            layer.name
            for layer, steps in prepared
            for moves in steps
            for node, x, y in moves
            if abs(node.x - x) > 0.5 or abs(node.y - y) > 0.5
        ]


class ToolPanel(outline_panel.panel_type()):
    """Preview selected glyphs; apply one checked history action at a time."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Apply", "Changed", "item"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Item", "Now", "After")
    STRUCTURAL = False

    def build_controls(self) -> None:
        """Build only the controls that this outline operation needs."""
        self.horizontal = self.spin(-1000, 1000, 0, " units", 2)
        self.vertical = self.spin(-1000, 1000, 10, " units", 2)
        self.add_row("X nudge", self.horizontal)
        self.add_row("Y nudge", self.vertical)

    def refresh(self) -> None:
        """Contain planner timeouts during control changes."""
        try:
            super().refresh()
        except (ValueError, RuntimeError, TimeoutError) as error:
            self.slot_error = str(error)
            self.apply_button.setEnabled(False)
            self.status.setText(f"Error: {error}")

    def apply(self) -> None:
        """Clear an old error before each action; show recovery after a mismatch."""
        self.slot_error = ""
        super().apply()
        if outline_panel.NOT_STORED in self.slot_error:
            self.status.setText(self.status.text + " Use Edit > Undo.")

    def planner(self) -> writer.Planner:
        """Capture control values when the shared panel plans from live data."""
        return lambda glyph, master, layer: changes(
            layer, float(self.horizontal.value), float(self.vertical.value)
        )

    def editor(self) -> writer.Editor:
        """Return the native write strategy used by the shared history kernel."""
        return NudgeEditor()


def main() -> Any:
    """Open one non-modal panel; replace an earlier panel of the same tool."""
    return scripting.show_script_dialog(ToolPanel, KEY)


if __name__ == "__main__":
    main()
