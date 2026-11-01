# this_file: Scripts/Contours/Delete Close Points.py
# SPDX-License-Identifier: MIT
"""Merge endpoints of segments shorter than a chosen distance.

What: Merge endpoints of segments shorter than a chosen distance. How: Measure cubic arc
lengths with 32 samples; remove short incoming spans. Closed contours retain at least
three endpoints. Why: Remove tiny segments left by tracing. Use: Set the distance in
font units, inspect the counts, then press Apply. Benefit: Shows exactly which segments
change before a batch edit.

The non-modal panel previews the selected glyphs and chosen masters. Shared, scaled and
rotated outline shapes are kept. Automatic-layer owners are kept. Bases of automatic
composites are kept unless the shared consent option is enabled. Each Apply is recorded
as one Undo step through the App history writer. Reload after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Delete Close Points.py,
MIT, copyright 2017 Simon Cozens. Repository:
https://github.com/simoncozens/GlyphsScripts . No source code was copied.
"""

import math
from itertools import pairwise
from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - native package lookup
import fly.ap.outline_writer as writer
import fly.ap.scripting as scripting  # noqa: PLR0402 - native package lookup

TITLE = "Delete Close Points"
KEY = "cozens_delete_close_points"


def arc_length(span: list[Any]) -> float:
    """Sample a cubic at 32 equal parameter intervals; exact length for a line."""
    if len(span) == 2:
        return math.hypot(span[-1].x - span[0].x, span[-1].y - span[0].y)
    samples = []
    for index in range(33):
        t = index / 32
        weights = ((1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t**3)
        samples.append(
            tuple(
                sum(w * getattr(n, axis) for w, n in zip(weights, span))
                for axis in ("x", "y")
            )
        )
    return sum(math.dist(a, b) for a, b in pairwise(samples))


def changes(layer: Any, limit: float) -> list[writer.Change]:
    """Plan removals from original spans; keep three endpoints per contour."""
    if not math.isfinite(limit) or limit <= 0:
        raise ValueError("Distance must be finite and positive.")
    shapes, notes = writer.outline_shapes(layer)
    rows = []
    for si, shape in enumerate(shapes):
        for ci, contour in enumerate(shape.contours):
            if contour.isTT or not contour.closed:
                notes.append("open or quadratic contour, kept")
                continue
            nodes = list(contour.nodes())
            ends = [i for i, n in enumerate(nodes) if n.isOn()]
            edges = []
            edge_indices = []
            for number, start in enumerate(ends):
                stop = ends[(number + 1) % len(ends)]
                length = (stop - start) % len(nodes) or len(nodes)
                indices = [(start + j) % len(nodes) for j in range(length + 1)]
                edge_indices.append(indices)
                edges.append([nodes[i] for i in indices])
            if any(len(edge) not in (2, 4) for edge in edges):
                notes.append("unsupported segment structure, kept")
                continue
            picked = [i for i, edge in enumerate(edges) if arc_length(edge) <= limit]
            picked = picked[: max(0, len(edges) - 3)]
            doomed = {index for number in picked for index in edge_indices[number][1:]}
            indices = sorted(doomed)
            if indices:
                remaining = [n for i, n in enumerate(nodes) if i not in doomed]
                if remaining and not remaining[0].isOn():
                    first = next(i for i, n in enumerate(remaining) if n.isOn())
                    remaining = remaining[first:] + remaining[:first]
                if remaining and not remaining[-1].isOn() and remaining[-1].smooth:
                    notes.append("final control has Smooth set (fl#8517), kept")
                    continue
                kept = [(float(n.x), float(n.y), bool(n.isOn())) for n in remaining]
                rows.append(
                    writer.Change(
                        f"contour {ci + 1}",
                        str(len(picked)),
                        "merge",
                        (contour, indices, kept),
                        key=(si, ci, tuple(picked)),
                    )
                )
    return rows + writer.note_rows(notes)


class MergeEditor(writer.Editor):
    """Remove incoming short spans in reverse order; retain original survivors."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        for contour, indices, _ in steps:
            for index in reversed(indices):
                contour.removeAt(index)
            if not contour.nodes()[0].isOn():
                first = next(i for i, node in enumerate(contour.nodes()) if node.isOn())
                if contour.setStartPoint(first) is False:
                    raise RuntimeError("FontLab refused the surviving start node.")

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        return [
            layer.name
            for layer, steps in prepared
            for contour, _, expected in steps
            if writer.node_points(contour) != expected
            or (not contour.nodes()[-1].isOn() and contour.nodes()[-1].smooth)
        ]


class ToolPanel(outline_panel.panel_type()):
    """Preview selected glyphs; apply one checked history action at a time."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Apply", "Changed", "item"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Item", "Now", "After")
    STRUCTURAL = True

    def build_controls(self) -> None:
        """Build only the controls that this outline operation needs."""
        self.distance = self.spin(0.01, 1000, 5, " units", 2)
        self.add_row("Distance up to", self.distance)

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
        return lambda glyph, master, layer: changes(layer, float(self.distance.value))

    def editor(self) -> writer.Editor:
        """Return the native write strategy used by the shared history kernel."""
        return MergeEditor()


def main() -> Any:
    """Open one non-modal panel; replace an earlier panel of the same tool."""
    return scripting.show_script_dialog(ToolPanel, KEY)


if __name__ == "__main__":
    main()
