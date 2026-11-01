# this_file: Scripts/Contours/Superaligner.py
# SPDX-License-Identifier: MIT
"""Align contour start nodes and directions to the first declared master.

What: Align contour start nodes and directions to the first declared master. How:
Compare normalized point geometry among cyclic point-type matches in both directions.
Choose the unique closest order; keep a glyph when scores tie. Read back the actual
point coordinates, start and winding after each write. Why: Repair master point ordering
before interpolation. Use: Choose All masters, inspect the start and direction changes,
then Apply. Benefit: Adds a batch preview to start-node and direction commands.

The non-modal panel previews the selected glyphs and chosen masters. A glyph with
shared, scaled or rotated outline shapes is kept as a whole. Automatic-layer owners are
kept. Bases of automatic composites are kept unless the shared consent option is
enabled. Each Apply is recorded as one Undo step through the App history writer. Reload
after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Superaligner.py, MIT,
copyright 2017 Simon Cozens. Repository: https://github.com/simoncozens/GlyphsScripts .
No source code was copied.
"""

import math
from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - native package lookup
import fly.ap.outline_writer as writer
import fly.ap.scripting as scripting  # noqa: PLR0402 - native package lookup

TITLE = "Superaligner"
KEY = "cozens_superaligner"


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


def contours(layer: Any) -> list[Any]:
    """Read editable contours; refuse omitted shapes for cross-master mapping."""
    shapes, notes = writer.outline_shapes(layer)
    if notes:
        raise ValueError("Use own, unscaled outline shapes.")
    return [contour for shape in shapes for contour in shape.contours]


def normalized(points: list[writer.Point]) -> list[tuple[float, float]]:
    """Remove translation and axis scale before comparing master geometry."""
    left, right = min(p[0] for p in points), max(p[0] for p in points)
    bottom, top = min(p[1] for p in points), max(p[1] for p in points)
    return [
        ((x - left) / (right - left or 1), (y - bottom) / (top - bottom or 1))
        for x, y, _ in points
    ]


def alignment(
    reference: list[writer.Point], candidate: list[writer.Point]
) -> tuple[bool, int]:
    """Choose the unique nearest geometry among both cyclic point-type orders."""
    if len(reference) != len(candidate) or not reference:
        raise ValueError("Master point counts differ or a contour is empty.")
    ref = normalized(reference)
    wanted = [p[2] for p in reference]
    scored = []
    for reverse in (False, True):
        sequence = candidate[:1] + candidate[:0:-1] if reverse else candidate
        xy = normalized(sequence)
        for shift, point in enumerate(sequence):
            ordered = sequence[shift:] + sequence[:shift]
            if point[2] and [p[2] for p in ordered] == wanted:
                positions = xy[shift:] + xy[:shift]
                score = sum(math.dist(a, b) ** 2 for a, b in zip(ref, positions))
                scored.append((score, reverse, shift))
    if not scored:
        raise ValueError("No cyclic point-type match exists between masters.")
    scored.sort()
    if len(scored) > 1 and math.isclose(
        scored[0][0], scored[1][0], abs_tol=1e-10, rel_tol=1e-9
    ):
        raise ValueError("ambiguous start,")
    return scored[0][1], scored[0][2]


def plan_content(
    glyph: Any, master: str, layer: Any, reference: str
) -> list[writer.Change]:
    """Match contour order to the first declared master; refuse incomplete pairs."""
    first = writer.layer_of(glyph, reference)
    if first is None:
        raise ValueError("Reference master layer is missing.")
    original, target = contours(first), contours(layer)
    if len(original) != len(target):
        raise ValueError("Master contour counts differ.")
    rows = []
    for ci, (source, dest) in enumerate(zip(original, target)):
        spans(source)
        spans(dest)
        if master == reference:
            continue
        ref = writer.node_points(source)
        actual = writer.node_points(dest)
        reverse, shift = alignment(ref, actual)
        planned = actual[:1] + actual[:0:-1] if reverse else actual
        planned = planned[shift:] + planned[:shift]
        expected_clockwise = (
            not bool(dest.clockwise) if reverse else bool(dest.clockwise)
        )
        raw = list(dest.nodes())
        raw = raw[:1] + raw[:0:-1] if reverse else raw
        raw = raw[shift:] + raw[:shift]
        if raw and not raw[-1].isOn() and raw[-1].smooth:
            raise ValueError("final control has Smooth set (fl#8517),")
        if reverse or shift:
            rows.append(
                writer.Change(
                    f"contour {ci + 1}",
                    "point order",
                    f"reverse {reverse}, start {shift}",
                    (dest, reverse, shift, planned, expected_clockwise),
                )
            )
    return rows


def changes(
    glyph: Any, master: str, layer: Any, masters: list[str]
) -> list[writer.Change]:
    """Keep a whole unsuitable glyph while other glyphs remain writable."""
    try:
        for name in masters:
            target = writer.layer_of(glyph, name)
            if target is None:
                raise ValueError("A declared master layer is missing.")
            plan_content(glyph, name, target, masters[0])
        return plan_content(glyph, master, layer, masters[0])
    except ValueError as error:
        return [writer.Change("glyph", "", f"{str(error).rstrip('.,')}, kept")]


class AlignEditor(writer.Editor):
    """Reverse and rotate native contours without cloning them."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        for contour, reverse, shift, _, _ in steps:
            if reverse:
                contour.reverse()
            if shift and contour.setStartPoint(shift) is False:
                raise RuntimeError("FontLab refused the start point.")

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        return [
            layer.name
            for layer, steps in prepared
            for contour, _, _, planned, clockwise in steps
            if writer.node_points(contour) != planned
            or bool(contour.clockwise) != clockwise
            or (not contour.nodes()[-1].isOn() and contour.nodes()[-1].smooth)
        ]


class ToolPanel(outline_panel.panel_type()):
    """Preview selected glyphs; apply one checked history action at a time."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Apply", "Changed", "item"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Item", "Now", "After")
    STRUCTURAL = False  # The planner applies its own cross-layer compatibility rule.
    SCOPE = 1

    def build_controls(self) -> None:
        """Build only the controls that this outline operation needs."""

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
        """Compare against the first declared master through the public font API."""
        masters = list(scripting.current_package().masters)
        return lambda glyph, master, layer: changes(glyph, master, layer, masters)

    def editor(self) -> writer.Editor:
        """Return the native write strategy used by the shared history kernel."""
        return AlignEditor()


def main() -> Any:
    """Open one non-modal panel; replace an earlier panel of the same tool."""
    return scripting.show_script_dialog(ToolPanel, KEY)


if __name__ == "__main__":
    main()
