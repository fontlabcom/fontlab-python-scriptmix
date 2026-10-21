# this_file: Scripts/Contours/Sandblast.py
# SPDX-License-Identifier: MIT
"""Add small irregular counters inside closed outlines.

What: Add small irregular counters inside closed outlines. How: Use a reproducible seed
and bounded placement attempts. Keep each hole wholly inside the combined filled shape,
outside existing counters, and separate from other holes. Cache placements per scan and
control setting. Orient each hole opposite its innermost containing contour. Why: Create
a distressed outline without a rejection loop that can hang. Use: Set hole count, radius
and seed. Inspect the placed count, then Apply. Benefit: Creates editable counters; the
preview reports the count actually placed.

The non-modal panel previews the selected glyphs and chosen masters. Shared, scaled and
rotated outline shapes are kept. Automatic-layer owners are kept. Bases of automatic
composites are kept unless the shared consent option is enabled. Each Apply is recorded
as one Undo step through the App history writer. Reload after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Sandblast.py, MIT,
copyright 2017 Simon Cozens. Repository: https://github.com/simoncozens/GlyphsScripts .
No source code was copied.
"""

import math
import random
from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - native package lookup
import fly.ap.outline_writer as writer
import fly.ap.scripting as scripting  # noqa: PLR0402 - native package lookup
from fly import fl, qt

TITLE = "Sandblast"
KEY = "cozens_sandblast"


def holes(
    path: Any,
    bounds: tuple[float, float, float, float],
    count: int,
    radius: float,
    seed: int,
) -> list[list[tuple[float, float]]]:
    """Place disjoint polygon holes; stop after a bounded number of attempts."""
    if not 1 <= count <= 1000 or not math.isfinite(radius) or radius <= 0:
        raise ValueError("Choose 1 to 1000 holes and a positive finite radius.")
    rng = random.Random(seed)
    left, bottom, right, top = bounds
    accepted = []
    centers: list[tuple[float, float]] = []
    for _ in range(count * 50):
        if len(accepted) == count:
            break
        x, y = rng.uniform(left, right), rng.uniform(bottom, top)
        if any(math.dist((x, y), center) < radius * 2 for center in centers):
            continue
        points = []
        for side in range(12):
            angle = side * math.tau / 12
            r = radius * rng.uniform(0.6, 1)
            points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
        polygon = qt.QtGui.QPainterPath()
        polygon.moveTo(*points[0])
        for point in points[1:]:
            polygon.lineTo(*point)
        polygon.closeSubpath()
        if path.contains(polygon):
            accepted.append(points)
            centers.append((x, y))
    return accepted


def changes(
    layer: Any, count: int, radius: float, seed: int, cache: dict | None = None
) -> list[writer.Change]:
    """Use each shape's combined filled path, including existing counters."""
    shapes, notes = writer.outline_shapes(layer)
    rows = []
    for si, shape in enumerate(shapes):
        if any(not c.closed for c in shape.contours):
            notes.append("open contour, kept")
            continue
        outlines = [writer.node_points(c) for c in shape.contours]
        points = [p for contour_points in outlines for p in contour_points]
        if not points:
            continue
        x, y = zip(*[(p[0], p[1]) for p in points])
        key = (
            count,
            radius,
            seed,
            tuple(tuple(p) for p in outlines),
            tuple(bool(c.clockwise) for c in shape.contours),
        )
        if cache is not None and key in cache:
            result = cache[key]
        else:
            result = holes(
                shape.closedPath, (min(x), min(y), max(x), max(y)), count, radius, seed
            )
            oriented = []
            for polygon in result:
                inside = []
                for contour in shape.contours:
                    if contour.path().contains(qt.QtCore.QPointF(*polygon[0])):
                        box = contour.path().boundingRect()
                        inside.append(
                            (
                                float(box.width()) * float(box.height()),
                                bool(contour.clockwise),
                            )
                        )
                if inside:
                    clockwise = min(inside)[1]
                    oriented.append(polygon if clockwise else polygon[::-1])
            result = oriented
            if cache is not None:
                cache[key] = result
        if result:
            rows.append(
                writer.Change(
                    f"shape {si + 1}",
                    "0 new holes",
                    f"{len(result)} holes",
                    (shape, result),
                    key=(si, len(result)),
                )
            )
    return rows + writer.note_rows(notes)


def point_lists_match(
    actual: list[list[writer.Point]], expected: list[list[writer.Point]]
) -> bool:
    """Compare stored contour counts, node counts and coordinates within half a unit."""
    return len(actual) == len(expected) and all(
        len(stored) == len(planned)
        and all(
            on == found[2] and abs(x - found[0]) <= 0.5 and abs(y - found[1]) <= 0.5
            for (x, y, on), found in zip(planned, stored)
        )
        for stored, planned in zip(actual, expected)
    )


class HoleEditor(writer.Editor):
    """Allocate detached hole contours before history and append inside history."""

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        """Snapshot complete expected shape geometry before adding the holes."""
        return [
            (
                shape,
                [
                    fl.flContour(
                        [
                            fl.flNode(qt.QtCore.QPointF(x, y), nodeType="on")
                            for x, y in polygon
                        ],
                        closed=True,
                    )
                    for polygon in polygons
                ],
                [writer.node_points(c) for c in shape.contours]
                + [[(x, y, True) for x, y in polygon] for polygon in polygons],
            )
            for shape, polygons in edits
        ]

    def write(self, layer: Any, steps: list[Any]) -> None:
        for shape, fresh, _ in steps:
            for contour in fresh:
                shape.addContour(contour)

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        """Compare actual stored contour lengths and point lists, never wrapper identity."""
        return [
            layer.name
            for layer, steps in prepared
            for shape, _, expected in steps
            if not point_lists_match(
                [writer.node_points(c) for c in shape.contours], expected
            )
        ]


class ToolPanel(outline_panel.panel_type()):
    """Preview selected glyphs; apply one checked history action at a time."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Apply", "Changed", "item"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Item", "Now", "After")
    STRUCTURAL = True

    def build_controls(self) -> None:
        """Build only the controls that this outline operation needs."""
        self.hole_count = self.spin(1, 1000, 50)
        self.radius = self.spin(0.1, 1000, 3, " units", 1)
        self.seed = self.spin(0, 1000000, 1)
        self.add_row("Holes", self.hole_count)
        self.add_row("Radius", self.radius)
        self.add_row("Seed", self.seed)

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

    def on_reload(self) -> None:
        """Drop cached placement when the font selection is reloaded."""
        self.hole_cache: dict = {}
        self.hole_settings: tuple | None = None

    def planner(self) -> writer.Planner:
        """Cache pure placement results for one scan and one control setting."""
        settings = (
            int(self.hole_count.value),
            float(self.radius.value),
            int(self.seed.value),
        )
        if settings != self.hole_settings:
            self.hole_cache.clear()
            self.hole_settings = settings
        return lambda glyph, master, layer: changes(layer, *settings, self.hole_cache)

    def editor(self) -> writer.Editor:
        """Return the native write strategy used by the shared history kernel."""
        return HoleEditor()


def main() -> Any:
    """Open one non-modal panel; replace an earlier panel of the same tool."""
    return scripting.show_script_dialog(ToolPanel, KEY)


if __name__ == "__main__":
    main()
