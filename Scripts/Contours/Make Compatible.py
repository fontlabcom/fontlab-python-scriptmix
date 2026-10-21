# this_file: Scripts/Contours/Make Compatible.py
# SPDX-License-Identifier: MIT
"""Promote straight segments where corresponding masters contain cubics.

What: Promote straight segments where corresponding masters contain cubics. How: Compare
each contour and segment with every declared master. Keep glyphs with mismatched contour
counts, open paths or quadratic outlines. Endpoints stay. Why: Repair line-versus-cubic
interpolation mismatches without moving endpoints. Use: Align starts and directions
first (run Superaligner), then select glyphs, choose All masters, inspect the conversion
rows, and Apply. Benefit: Repairs segment types across masters rather than merely
reporting them.

The non-modal panel previews the selected glyphs and chosen masters. A glyph with
shared, scaled or rotated outline shapes is kept as a whole. Automatic-layer owners are
kept. Bases of automatic composites are kept unless the shared consent option is
enabled. Each Apply is recorded as one Undo step through the App history writer. Reload
after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Make Compatible.py, MIT,
copyright 2017 Simon Cozens. Repository: https://github.com/simoncozens/GlyphsScripts .
No source code was copied.
"""

from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - native package lookup
import fly.ap.outline_writer as writer
import fly.ap.scripting as scripting  # noqa: PLR0402 - native package lookup

TITLE = "Make Compatible"
KEY = "cozens_make_compatible"


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


def plan_content(
    glyph: Any, master: str, layer: Any, masters: list[str]
) -> list[writer.Change]:
    """Compare corresponding segments of every declared master before planning."""
    layers = [writer.layer_of(glyph, name) for name in masters]
    if any(item is None for item in layers):
        raise ValueError("Every declared master must have a layer.")
    groups = [contours(item) for item in layers]
    if len({len(group) for group in groups}) != 1:
        raise ValueError("Master contour counts differ.")
    rows = []
    for ci, aligned in enumerate(zip(*groups)):
        edges = [spans(contour) for contour in aligned]
        if len({len(group) for group in edges}) != 1:
            raise ValueError("Master segment counts differ.")
        current = edges[masters.index(master)]
        picked = [
            i
            for i, corresponding in enumerate(zip(*edges))
            if len(current[i]) == 2 and any(len(edge) == 4 for edge in corresponding)
        ]
        if picked:
            contour = aligned[masters.index(master)]
            rows.append(
                writer.Change(
                    f"contour {ci + 1}",
                    str(len(picked)),
                    "line to cubic",
                    (
                        contour,
                        [current[i][-1] for i in picked],
                        contour.nodesCount + 2 * len(picked),
                    ),
                )
            )
    return rows


def changes(
    glyph: Any, master: str, layer: Any, masters: list[str]
) -> list[writer.Change]:
    """Keep an unsuitable glyph; allow other selected glyphs to proceed."""
    try:
        # Check every layer before returning any per-layer edits.
        for name in masters:
            target = writer.layer_of(glyph, name)
            plan_content(glyph, name, target, masters)
        return plan_content(glyph, master, layer, masters)
    except ValueError as error:
        return [writer.Change("glyph", "", f"{str(error).rstrip('.,')}, kept")]


class CompatibleEditor(writer.Editor):
    """Promote lines in place; do not change endpoint connection flags."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        for _, endpoints, _ in steps:
            for endpoint in endpoints:
                if endpoint.convertToCurve(False) is False:
                    raise RuntimeError("FontLab refused cubic conversion.")

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        return [
            layer.name
            for layer, steps in prepared
            for contour, _, count in steps
            if contour.nodesCount != count
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
        """Clear an old failure before retrying this action."""
        self.slot_error = ""
        super().apply()
        if outline_panel.NOT_STORED in self.slot_error:
            self.status.setText(self.status.text + " Use Edit > Undo.")

    def planner(self) -> writer.Planner:
        """Use declared masters; corresponding contour starts must already match."""
        masters = list(scripting.current_package().masters)
        return lambda glyph, master, layer: changes(glyph, master, layer, masters)

    def editor(self) -> writer.Editor:
        """Return the native write strategy used by the shared history kernel."""
        return CompatibleEditor()


def main() -> Any:
    """Open one non-modal panel; replace an earlier panel of the same tool."""
    return scripting.show_script_dialog(ToolPanel, KEY)


if __name__ == "__main__":
    main()
