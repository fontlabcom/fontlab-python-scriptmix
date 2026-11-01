# this_file: Scripts/Contours/Straighten All Curves.py
# SPDX-License-Identifier: MIT
"""Replace every cubic segment with its straight chord.

What: Replace every cubic segment with its straight chord. How: Native conversion
removes handles; endpoints stay in place. FontLab may reset the smooth flags of both end
nodes during conversion. Why: Create a polygonal version of an outline.
Use: Select nodes in the current layer to choose whole contours, or leave nodes
unselected for all contours. The same contour and endpoint indices apply only to layers
with matching contour counts, node counts and point types. Incompatible layers are
listed as kept. Inspect the curve counts, then press Apply.
Benefit: Converts the chosen contours across compatible layers with a preview.

The non-modal panel previews the selected glyphs and chosen masters. A layer that has a shared, scaled or
rotated outline shape is kept as a whole. Automatic-layer owners are kept. Bases of automatic
composites are kept unless the shared consent option is enabled. Each Apply is recorded
as one Undo step through the App history writer. Reload after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Straighten All
Curves.py, MIT, copyright 2017 Simon Cozens. Repository:
https://github.com/simoncozens/GlyphsScripts . No source code was copied.
"""

from time import monotonic
from typing import Any

import fly.ap.layer_selection as layer_selection  # noqa: PLR0402 - native package lookup
import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - native package lookup
import fly.ap.outline_writer as writer
import fly.ap.scripting as scripting  # noqa: PLR0402 - native package lookup

TITLE = "Straighten All Curves"
KEY = "cozens_straighten_all_curves"


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


MODE = "line"


def changes(layer: Any, reference: Any | None = None) -> list[writer.Change]:
    """Map selected contour and endpoint indices from the current layer."""
    reference = layer if reference is None else reference
    shapes, notes = writer.outline_shapes(layer)
    source_shapes, source_notes = writer.outline_shapes(reference)
    target = [c for shape in shapes for c in shape.contours]
    source = [c for shape in source_shapes for c in shape.contours]
    if notes or source_notes:
        return [writer.Change("layer", "", "shared or scaled shape, kept")]
    if len(source) != len(target) or any(
        a.nodesCount != b.nodesCount for a, b in zip(source, target)
    ):
        return [writer.Change("layer", "", "incompatible contour or node counts, kept")]
    selection = [{i for i, n in enumerate(c.nodes()) if n.selected} for c in source]
    selected = any(selection)
    rows = []
    for ci, (original, contour) in enumerate(zip(source, target)):
        if selected and not selection[ci]:
            continue
        if original.isTT or not original.closed or contour.isTT or not contour.closed:
            notes.append("open or quadratic contour, kept")
            continue
        if [n.isOn() for n in original.nodes()] != [n.isOn() for n in contour.nodes()]:
            return [writer.Change("layer", "", "incompatible point types, kept")]
        source_nodes = list(original.nodes())
        nodes = list(contour.nodes())
        # Any selected node selects its complete contour, as in the source tool.
        endpoint_indices = [i for i, n in enumerate(source_nodes) if n.isOn()]
        picked = []
        for number, span in enumerate(spans(original)):
            if len(span) == (2 if MODE == "curve" else 4):
                # Index through one source snapshot, never through another layer's selection.
                index = endpoint_indices[(number + 1) % len(endpoint_indices)]
                picked.append(nodes[index])
        if picked:
            expected = contour.nodesCount + len(picked) * (2 if MODE == "curve" else -2)
            rows.append(
                writer.Change(
                    f"contour {ci + 1}",
                    str(len(picked)),
                    MODE,
                    (contour, picked, expected),
                )
            )
    return rows + writer.note_rows(notes)


class ConversionEditor(writer.Editor):
    """Convert the planned native endpoints and check every segment count."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        for contour, endpoints, expected in steps:
            for endpoint in endpoints:
                if MODE == "curve":
                    ok = endpoint.convertToCurve(False)
                else:
                    ok = endpoint.convertToLine()
                if ok is False:
                    raise RuntimeError("FontLab refused segment conversion.")
            if MODE == "curve":
                for node in contour.nodes():
                    if node.isOn():
                        node.smooth = True

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        return [
            layer.name
            for layer, steps in prepared
            for contour, _, expected in steps
            if contour.nodesCount != expected
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
        """Capture the selected editor layers through the public layer-selection API."""
        captured = layer_selection.capture(monotonic() + 2.0)
        sources = {}
        for occurrence in captured.occurrences:
            sources.setdefault(occurrence.glyph.name, occurrence.layer)

        def plan(glyph: Any, master: str, layer: Any) -> list[writer.Change]:
            if glyph.name not in sources:
                return [writer.Change("glyph", "", "no current selected layer, kept")]
            return changes(layer, sources[glyph.name])

        return plan

    def editor(self) -> writer.Editor:
        """Return the native write strategy used by the shared history kernel."""
        return ConversionEditor()


def main() -> Any:
    """Open one non-modal panel; replace an earlier panel of the same tool."""
    return scripting.show_script_dialog(ToolPanel, KEY)


if __name__ == "__main__":
    main()
