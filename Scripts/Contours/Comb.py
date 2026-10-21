# this_file: Scripts/Contours/Comb.py
# SPDX-License-Identifier: MIT
"""Split ribbon contours into evenly spaced strips.

What: Split ribbon contours into evenly spaced strips. How: The shortest opposing
compatible line segments form caps. Pair the intervening edges in opposite directions
and interpolate their coordinates. Equal segment types are required. New contours
replace the ribbon. Read-back allows 0.5 unit per axis for native rounding. Why: Make a
striped outline while retaining cubic edge geometry. Use: Set strip count and filled
percentage. Inspect the contour counts, then Apply. Benefit: Generates editable strips
over selected glyphs and masters. Rebuilt contours have new node identities.

The non-modal panel previews the selected glyphs and chosen masters. Shared, scaled and
rotated outline shapes are kept. Automatic-layer owners are kept. Bases of automatic
composites are kept unless the shared consent option is enabled. Each Apply is recorded
as one Undo step through the App history writer. Reload after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Comb.py, MIT, copyright
2017 Simon Cozens. Repository: https://github.com/simoncozens/GlyphsScripts . No source
code was copied.
"""

import math
from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - native package lookup
import fly.ap.outline_writer as writer
import fly.ap.scripting as scripting  # noqa: PLR0402 - native package lookup
from fly import fl, qt

TITLE = "Comb"
KEY = "cozens_comb"


def spans(contour: Any) -> list[list[Any]]:
    """Read complete line or cubic spans; refuse quadratic and open contours."""
    if contour.isTT or not contour.closed:
        raise ValueError("Use closed PostScript contours.")
    nodes = list(contour.nodes())
    ends = [i for i, node in enumerate(nodes) if node.isOn()]
    result = []
    for number, start in enumerate(ends):
        stop = ends[(number + 1) % len(ends)]
        length = (stop - start) % len(nodes) or len(nodes)
        span = [nodes[(start + offset) % len(nodes)] for offset in range(length + 1)]
        if len(span) not in (2, 4):
            raise ValueError("A contour has an unsupported segment structure.")
        result.append(span)
    return result


Point = tuple[float, float, bool]


def striped(points: list[list[Point]], count: int, fill: float) -> list[list[Point]]:
    """Interpolate corresponding ribbon edges; cap each strip with lines."""
    if not 1 <= count <= 100 or not 0 < fill < 1:
        raise ValueError(
            "Use 1 to 100 strips and a filled fraction between zero and one."
        )
    caps = sorted(
        (math.dist(edge[0][:2], edge[-1][:2]), i)
        for i, edge in enumerate(points)
        if len(edge) == 2
    )
    if len(caps) < 2:
        raise ValueError("A ribbon needs two straight end caps.")
    pairs = [
        (a[0] + b[0], *sorted((a[1], b[1])))
        for i, a in enumerate(caps)
        for b in caps[i + 1 :]
        if abs(a[1] - b[1]) == len(points) // 2 and len(points) % 2 == 0
    ]
    if not pairs:
        raise ValueError("Ribbon sides need matching segment counts.")
    _, low, high = min(pairs)
    forward = points[low + 1 : high]
    backward = [edge[::-1] for edge in (points[high + 1 :] + points[:low])[::-1]]
    if not forward or len(forward) != len(backward):
        raise ValueError("Ribbon sides need matching segment counts.")
    if any(len(a) != len(b) for a, b in zip(forward, backward)):
        raise ValueError("Ribbon sides need matching segment types.")
    result = []
    for index in range(count):
        edges = []
        for fraction in (index / count, (index + fill) / count):
            edges.append(
                [
                    [
                        (
                            a[0] + (b[0] - a[0]) * fraction,
                            a[1] + (b[1] - a[1]) * fraction,
                            a[2],
                        )
                        for a, b in zip(left, right)
                    ]
                    for left, right in zip(forward, backward)
                ]
            )
        upper, lower = edges
        lower = [edge[::-1] for edge in lower[::-1]]
        joined = upper + [[upper[-1][-1], lower[0][0]]] + lower
        joined.append([lower[-1][-1], upper[0][0]])
        result.append([node for edge in joined for node in edge[:-1]])
    return result


def plan_content(layer: Any, count: int, fill: float) -> list[writer.Change]:
    """Plan strips without allocating any native objects."""
    shapes, notes = writer.outline_shapes(layer)
    rows = []
    for si, shape in enumerate(shapes):
        for ci, contour in enumerate(shape.contours):
            edges = [
                [(float(n.x), float(n.y), bool(n.isOn())) for n in edge]
                for edge in spans(contour)
            ]
            result = striped(edges, count, fill)
            rows.append(
                writer.Change(
                    f"contour {ci + 1}",
                    "ribbon",
                    f"{count} strips",
                    (shape, contour, result, ci),
                    key=(si, ci, tuple(map(len, result))),
                )
            )
    return rows + writer.note_rows(notes)


def changes(layer: Any, count: int, fill: float) -> list[writer.Change]:
    """Invalid controls fail; unsuitable outlines produce a kept row."""
    if not 1 <= count <= 100 or not 0 < fill < 1:
        raise ValueError(
            "Choose 1 to 100 strips and a filled fraction between zero and one."
        )
    try:
        return plan_content(layer, count, fill)
    except ValueError as error:
        return [writer.Change("glyph", "", f"{str(error).rstrip('.,')}, kept")]


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


class StripEditor(writer.Editor):
    """Prepare new contours before history; replace only the source ribbon."""

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        """Snapshot survivors and generated point lists before any native write."""
        groups: dict[int, Any] = {}
        for shape, _, result, index in edits:
            _, removed, added = groups.setdefault(int(shape.id), (shape, set(), []))
            removed.add(index)
            added.extend(result)
        expected = {
            key: [
                writer.node_points(c)
                for index, c in enumerate(shape.contours)
                if index not in removed
            ]
            + added
            for key, (shape, removed, added) in groups.items()
        }
        return [
            (
                shape,
                contour,
                [
                    fl.flContour(
                        [
                            fl.flNode(
                                qt.QtCore.QPointF(x, y),
                                nodeType="on" if on else "curve",
                            )
                            for x, y, on in points
                        ],
                        closed=True,
                    )
                    for points in result
                ],
                expected[int(shape.id)],
            )
            for shape, contour, result, _ in edits
        ]

    def write(self, layer: Any, steps: list[Any]) -> None:
        for shape, contour, fresh, _ in steps:
            shape.removeContour(contour)
            for item in fresh:
                shape.addContour(item)

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        """Read the stored shape, including native copies of the added contours."""
        return [
            layer.name
            for layer, steps in prepared
            for shape, _, _, expected in steps
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
        self.strips = self.spin(1, 100, 7)
        self.coverage = self.spin(1, 99, 50, " %")
        self.add_row("Strips", self.strips)
        self.add_row("Filled", self.coverage)

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
            layer, int(self.strips.value), float(self.coverage.value) / 100
        )

    def editor(self) -> writer.Editor:
        """Return the native write strategy used by the shared history kernel."""
        return StripEditor()


def main() -> Any:
    """Open one non-modal panel; replace an earlier panel of the same tool."""
    return scripting.show_script_dialog(ToolPanel, KEY)


if __name__ == "__main__":
    main()
