# this_file: Scripts/Anchors/Optical Center.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Optical Center
"""Report optical x and align an existing top anchor on selected master layers.

What: Move one third from the bounds centre toward the horizontal ink median.
How: Flatten the placed layer path once, including components. At at most
512 columns, sum exact filled-span lengths from the flattened rings. Use
nonzero winding; counters require correctly directed contours. Fill closes
open subpaths. Coordinates are absolute and round half up to font units.
Each layer has its own time budget. A refused layer becomes a note row;
other selected layers still run. No top anchor is created when it is missing.
Why: Scanline weights avoid thousands of PythonQt point-containment calls
and give a repeatable estimate based on ink rather than the bounding box.
Use: Select glyphs, inspect the non-modal preview, then click Align Top.
Benefit: Start visual anchor refinement from an ink-weight estimate.
Each application is recorded as one Undo step. This is an optical estimate.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.
"""

import math
from itertools import pairwise
from time import monotonic
from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup

TITLE = "Optical Center"
KEY = "anchors_optical_center"


def optical_position(
    strips: list[tuple[float, float]], left: float, right: float
) -> float:
    """Blend the bounds centre with the weighted median of occupied x strips."""
    total = sum(weight for _, weight in strips)
    if total <= 0:
        raise ValueError("No closed ink was found.")
    cumulative = 0.0
    for position, weight in strips:
        cumulative += weight
        if cumulative > total / 2:
            centre = (left + right) / 2
            return centre + (position - centre) / 3
    raise ValueError("No ink median was found.")


Point = tuple[float, float]
Rings = list[list[Point]]


def column_weight(rings: Rings, x: float, deadline: float = math.inf) -> float:
    """Sum exact filled vertical lengths of flattened rings using nonzero winding."""
    crossings: dict[float, int] = {}
    for ring in rings:
        for (ax, ay), (bx, by) in pairwise(ring):
            if monotonic() >= deadline:
                raise TimeoutError("Optical centre layer time budget exceeded.")
            if min(ax, bx) <= x < max(ax, bx):
                y = ay + (x - ax) * (by - ay) / (bx - ax)
                crossings[y] = crossings.get(y, 0) + (1 if bx > ax else -1)
    winding, previous, weight = 0, 0.0, 0.0
    for y, direction in sorted(crossings.items()):
        if winding:
            weight += y - previous
        winding += direction
        previous = y
    return weight


def estimate_rings(rings: Rings, deadline: float) -> int:
    """Use at most 512 column weights; retain each column's full filled length."""
    xs = [x for ring in rings for x, _ in ring]
    if not xs or not all(
        math.isfinite(v) for ring in rings for point in ring for v in point
    ):
        raise ValueError("No finite closed ink was found.")
    left, right = min(xs), max(xs)
    width = right - left
    if not math.isfinite(width) or width <= 0:
        raise ValueError("No closed ink was found.")
    count = max(1, min(512, math.ceil(width)))
    strips = []
    for column in range(count):
        x = left + (column + 0.5) * (width / count)
        strips.append((x, column_weight(rings, x, deadline)))
    return anchor_writer.half_up(optical_position(strips, left, right))


def layer_estimate(layer: Any) -> int:
    """Flatten the shared placed layer path once; give this layer its own budget."""
    import fly.ap.proof as proof  # noqa: PLR0402 - Fly submodule import

    deadline = monotonic() + 1.5
    path = proof.layer_path(layer)
    rings: Rings = []
    for polygon in path.toSubpathPolygons():
        ring = []
        for point in polygon:
            if monotonic() >= deadline:
                raise TimeoutError("Optical centre layer time budget exceeded.")
            ring.append((float(point.x()), float(point.y())))
        if len(ring) >= 3:
            if ring[0] != ring[-1]:
                ring.append(ring[0])
            rings.append(ring)
    return estimate_rings(rings, deadline)


def optical_changes(layer: Any) -> list[anchor_writer.Change]:
    """Report without creating top; move only the existing top pin's x."""
    try:
        x = layer_estimate(layer)
    except (ValueError, RuntimeError, TimeoutError) as error:
        return [anchor_writer.Change("optical x", "", f"{error}; layer skipped")]
    points = anchor_writer.anchor_points(layer)
    if "top" not in points:
        return [anchor_writer.Change("optical x", "", str(x))]
    old = points["top"]
    return (
        []
        if old[0] == x
        else [
            anchor_writer.Change(
                "top", str(old), str((x, old[1])), ("set", "top", (x, old[1]))
            )
        ]
    )


class OpticalAnchorCenter(anchor_panel.panel_type()):
    """Current-master optical estimate; no bounds-centre substitution."""

    TITLE, KEY, ACTION = TITLE, KEY, "Align Top"

    def refresh(self) -> None:
        """Contain scan errors inside the panel and disable its write action."""
        try:
            super().refresh()
        except (ValueError, RuntimeError, TimeoutError) as error:
            self.apply_button.setEnabled(False)
            self.status.setText(str(error))

    def chosen_masters(self) -> list[str]:
        return [self.current_master]

    def planner(self) -> anchor_writer.Planner:
        return lambda glyph, master, layer: optical_changes(layer)


def main() -> Any:
    """Open the estimate and top-anchor preview."""
    return scripting.show_script_dialog(OpticalAnchorCenter, KEY)


if __name__ == "__main__":
    main()
