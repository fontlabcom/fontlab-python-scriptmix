# this_file: Scripts/Contours/Simplify Selected Nodes.py
# SPDX-License-Identifier: Apache-2.0
"""Remove alternate selected nodes from straight contours.

What: Keep the first selected node, remove the second, and repeat in contour
order. Open endpoints stay. Closed polygons keep at least three nodes.
How: Preview the removals on each master. Delete by descending stored index.
Curves are kept; use FontLab Contour > Simplify for curve reduction. Shared or transformed outlines are also kept.
Why: Restrict this operation to polygons so deletion cannot break cubic topology.
Use: Select polygon nodes, run the tool, choose masters and press Simplify.
Benefit: A repeatable reduction with matching selected indices applied across compatible masters.
The change is recorded as one Undo step. Automatic layers are kept; leave the
automatic-base consent off to keep their bases too.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Paths/Simplify selection.py, Apache-2.0.
Repository: https://github.com/pedroarilla/glyphs-scripts . No source code copied.
"""

from typing import Any

import fly.ap.outline_panel as panel
import fly.ap.outline_writer as writer
import fly.ap.scripting as scripting  # noqa: PLR0402

TITLE = "Simplify Selected Nodes"
KEY = "contours_simplify_selected_nodes"


def removals(contour: Any, selected_indices: list[int] | None = None) -> list[int]:
    """Alternate selected indices, bounded by endpoints and minimum node count."""
    nodes = list(contour.nodes())
    if any(not node.isOn() for node in nodes):
        return []
    selected = (
        [i for i, node in enumerate(nodes) if node.selected]
        if selected_indices is None
        else selected_indices
    )
    candidates = selected[1::2]
    if not contour.closed:
        candidates = [i for i in candidates if 0 < i < len(nodes) - 1]
    minimum = 3 if contour.closed else 2
    return candidates[: max(0, len(nodes) - minimum)]


def changes(layer: Any, reference: Any = None) -> list[writer.Change]:
    """One row per editable polygon with selected nodes to remove."""
    shapes, notes = writer.outline_shapes(layer)
    rows = []
    reference_shapes = (
        writer.outline_shapes(reference)[0] if reference is not None else shapes
    )
    originals = [contour for shape in reference_shapes for contour in shape.contours]
    current = [contour for shape in shapes for contour in shape.contours]
    if len(originals) != len(current):
        return [
            writer.Change("contours", "", "", problem="Master contour counts differ.")
        ]
    number = 0
    for shape in shapes:
        for contour in shape.contours:
            number += 1
            original = originals[number - 1]
            if (
                len(original.nodes()) != len(contour.nodes())
                or original.closed != contour.closed
                or [node.isOn() for node in original.nodes()]
                != [node.isOn() for node in contour.nodes()]
            ):
                return [
                    writer.Change(
                        "nodes", "", "", problem="Master node structures differ."
                    )
                ]
            indices = removals(
                contour, [i for i, node in enumerate(original.nodes()) if node.selected]
            )
            if indices:
                count = len(contour.nodes())
                rows.append(
                    writer.Change(
                        f"contour {number}",
                        str(count),
                        str(count - len(indices)),
                        (contour, indices, count - len(indices)),
                        key=(number, tuple(indices)),
                    )
                )
    return rows + writer.note_rows(notes)


class SimplifyEditor(writer.Editor):
    """Remove only planned polygon nodes; verify the remaining count."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        for contour, indices, _ in steps:
            for index in reversed(indices):
                contour.removeAt(index)

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        return [
            str(layer.name)
            for layer, steps in prepared
            if any(len(contour.nodes()) != count for contour, _, count in steps)
        ]


class SimplifyPanel(panel.panel_type()):
    """Reuse the master scope and structural-compatibility preview."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Simplify", "Simplified", "contour"
    STRUCTURAL = True
    HEADERS = ("Glyph · master", "Polygon", "Nodes", "After")

    def planner(self) -> writer.Planner:
        return lambda glyph, master, layer: changes(
            layer, glyph.findLayer(self.current_master)
        )

    def editor(self) -> writer.Editor:
        return SimplifyEditor()


def main() -> Any:
    """Show the non-modal polygon reduction panel."""
    try:
        return scripting.show_script_dialog(SimplifyPanel, KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        from fly import ap, qt

        qt.QtGui.QMessageBox.warning(ap.fontlab.MainWindow(), TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
