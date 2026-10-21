# this_file: Scripts/Contours/Retract Handles.py
# SPDX-License-Identifier: Apache-2.0
"""Retract cubic handles onto their attached on-curve nodes.

What: Retract every cubic handle, or only handles attached to selected on-curve
nodes, in selected glyphs on chosen masters. Node counts and types stay.
How: Resolve handles per segment, including the closing segment. Open contours
do not wrap. Quadratic contours and shared or transformed outlines are kept.
Why: Zero-length handles can prepare curves for deliberate corner edits.
Use: Select glyphs or on-curve nodes. Choose the node filter, inspect the table,
then press Retract. The change is recorded as one Undo step.
Benefit: Exact, repeatable retraction over many glyphs and masters. Automatic
layers are kept; leave the automatic-base consent off to keep their bases too.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Paths/Make zero handles selected glyphs.py and Make zero handles selected nodes.py,
Apache-2.0. Repository: https://github.com/pedroarilla/glyphs-scripts .
No source code copied. Per-contour indexing also handles open ends correctly.
"""

from itertools import pairwise
from typing import Any

import fly.ap.outline_panel as panel
import fly.ap.outline_writer as writer
import fly.ap.scripting as scripting  # noqa: PLR0402

TITLE = "Retract Handles"
KEY = "contours_retract_handles"


def moves(
    contour: Any, selected_only: bool, selected_indices: set[int] | None = None
) -> list[tuple[Any, float, float]]:
    """Return changed handles and exact targets for well-formed cubic segments."""
    if contour.isTT:
        return []
    nodes = list(contour.nodes())
    ends = [i for i, node in enumerate(nodes) if node.isOn()]
    pairs = list(pairwise(ends))
    if contour.closed and ends:
        pairs.append((ends[-1], ends[0] + len(nodes)))
    result = []
    for start, stop in pairs:
        if stop - start != 3:
            continue
        for handle_index, base_index in ((start + 1, start), (stop - 1, stop)):
            handle, base = (
                nodes[handle_index % len(nodes)],
                nodes[base_index % len(nodes)],
            )
            if selected_only and not (
                base.selected
                if selected_indices is None
                else base_index % len(nodes) in selected_indices
            ):
                continue
            if (handle.x, handle.y) != (base.x, base.y):
                result.append((handle, float(base.x), float(base.y)))
    return result


def changes(
    layer: Any, selected_only: bool, reference: Any = None
) -> list[writer.Change]:
    """Preview the number of handles that actually move in each contour."""
    shapes, notes = writer.outline_shapes(layer)
    result = []
    originals = (
        [c for shape in writer.outline_shapes(reference)[0] for c in shape.contours]
        if reference is not None
        else []
    )
    number = 0
    for shape in shapes:
        for contour in shape.contours:
            indices = None
            if selected_only and reference is not None:
                if (
                    number >= len(originals)
                    or len(originals[number].nodes()) != len(contour.nodes())
                    or [n.isOn() for n in originals[number].nodes()]
                    != [n.isOn() for n in contour.nodes()]
                ):
                    return [
                        writer.Change(
                            "nodes", "", "", problem="Master node structures differ."
                        )
                    ]
                indices = {
                    i
                    for i, node in enumerate(originals[number].nodes())
                    if node.selected
                }
            number += 1
            targets = moves(contour, selected_only, indices)
            if targets:
                result.append(
                    writer.Change("handles", str(len(targets)), "retracted", targets)
                )
    return result + writer.note_rows(notes)


class RetractEditor(writer.Editor):
    """Move existing handles; read exact coordinates back after the write."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        for targets in steps:
            for node, x, y in targets:
                node.x, node.y = x, y

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        return [
            str(layer.name)
            for layer, steps in prepared
            if any(
                (node.x, node.y) != (x, y)
                for targets in steps
                for node, x, y in targets
            )
        ]


class RetractPanel(panel.panel_type()):
    """Master scope, node filter and live preview."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Retract", "Retracted", "contour"
    HEADERS = ("Glyph · master", "Item", "Handles", "After")

    def build_controls(self) -> None:
        from fly import qt

        self.selected_filter = qt.QtGui.QCheckBox("Only at selected on-curve nodes")
        self.add_row("", self.selected_filter)
        self.watch(self.selected_filter.toggled)

    def planner(self) -> writer.Planner:
        selected = bool(self.selected_filter.isChecked())
        return lambda glyph, master, layer: changes(
            layer, selected, glyph.findLayer(self.current_master)
        )

    def editor(self) -> writer.Editor:
        return RetractEditor()


def main() -> Any:
    """Open the reusable non-modal retraction panel."""
    try:
        return scripting.show_script_dialog(RetractPanel, KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        from fly import ap, qt

        qt.QtGui.QMessageBox.warning(ap.fontlab.MainWindow(), TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
