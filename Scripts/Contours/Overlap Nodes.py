# this_file: Scripts/Contours/Overlap Nodes.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Overlap Nodes
"""Move a tip's adjacent corner onto the tip and align the next handle.

What: Create coincident nodes for alternate contour construction. This does
not merge contours or remove overlap area.
How: For each selected on-curve tip, inspect the next corner first, then
the previous corner. Move the first corner followed by a control onto the
tip, make it sharp, and align the control x along its master's italic angle.
The layer name identifies its master, including auxiliary layers. The control
y stays. Handle x is truncated to an integer in glyph space.
Why: Explicit node selection, conflict refusal and a preview protect the
neighbourhood. Selected-layer/all-master scope uses each layer's stored selection.
Use: Select one tip per corner. Open the panel, inspect the rows and press
Overlap. Reload selection after choosing other glyphs. Scaled and rotated
shapes are refused; plain shape translations are supported.
Benefit: Repeat a precise tip construction without dragging two nodes.

Safety: Locked layers, locked shapes and shared selected outline data are
refused. Contours with their own transform are refused. Automatic-layer
glyphs and their bases are skipped. The action replans live node selection before writing. A failed write names Edit > Undo.
The change is recorded as one Undo step. Anchors, guides, widths and node
order stay. FontLab can round node coordinates to its grid.

Source: Independent behaviour-only rewrite after Alex Slobzheninov
(slobzheninov), https://github.com/slobzheninov/Glyphs-Scripts,
Apache-2.0. No source code, identifiers or comments were copied.
Additional idea credit: Rainer Erich Scheichelbauer (mekkablue), whose
italic-coordinate snippet is credited by the source; independent rewrite.
Behaviour source: Overlap nodes.py.
"""

import math
from time import monotonic
from typing import Any

import fly.ap.affine as affine  # noqa: PLR0402
import fly.ap.layer_selection as layer_selection  # noqa: PLR0402
import fly.ap.masters as masters  # noqa: PLR0402
import fly.ap.outline_panel as outline_panel  # noqa: PLR0402
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402
import fly.ap.scripting as scripting  # noqa: PLR0402

XY = tuple[float, float]
# Original node, target stored coordinates, and an optional smooth flag.
Move = tuple[Any, float, float, bool | None]


def selected_contours(layer: Any) -> list[tuple[Any, Any, list[Any]]]:
    """Read selected own contours; refuse locked or shared selected outlines."""
    result = []
    for shape in layer.shapes:
        if shape.isComponent:
            continue
        for contour in shape.contours:
            nodes = list(contour.nodes())
            if not any(node.selected for node in nodes):
                continue
            if not all(math.isfinite(float(v)) for n in nodes for v in (n.x, n.y)):
                raise ValueError("Selected contour has non-finite coordinates.")
            if layer.isLocked or shape.contentLocked:
                raise ValueError("Unlock the selected layer and shape first.")
            if int(shape.shapeData.referenceCount) > 1 or list(shape.includesList):
                raise ValueError("Selected outline data is shared; unlink it first.")
            if affine.from_qtransform(contour.transform) != affine.IDENTITY:
                raise ValueError("Bake the selected contour transform first.")
            result.append((shape, contour, nodes))
    return result


class NodeEditor(outline_writer.Editor):
    """Write original node objects; check every coordinate and changed flag."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        """Assign coordinates without a clone or a smart-node move."""
        for moves in steps:
            for node, x, y, smooth in moves:
                node.x, node.y = x, y
                if smooth is not None:
                    node.smooth = smooth

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        """Diagnose missing writes after normal whole-unit host rounding."""
        for layer, steps in prepared:
            for moves in steps:
                for node, x, y, smooth in moves:
                    if (
                        not math.isfinite(node.x)
                        or not math.isfinite(node.y)
                        or abs(node.x - x) > 0.5
                        or abs(node.y - y) > 0.5
                        or (smooth is not None and bool(node.smooth) != smooth)
                    ):
                        raise RuntimeError(
                            f"{layer.name}: a node differs from the plan. "
                            "Native changes may remain; use Edit > Undo."
                        )
        return []


TITLE = "Overlap Nodes"
KEY = "contours_overlap_nodes"
ACTION, DONE = "Overlap", "Overlapped"


def tip_changes(layer: Any, angle: float) -> list[outline_writer.Change]:
    """Collapse the adjacent corner onto each selected tip and align its handle.

    FontLab italic angles have the opposite sign to the Glyphs convention.
    Truncate the handle x in glyph coordinates, as in the behaviour source.
    Plan all moves from the unchanged contour; refuse conflicting targets.
    """
    if not math.isfinite(angle) or not -89 < angle < 89:
        raise ValueError("The italic angle must be finite and between -89° and 89°.")
    shear = -math.tan(math.radians(angle))
    rows = []
    for shape, contour, nodes in selected_contours(layer):
        offset = outline_writer.translation(shape)
        if offset is None:
            raise ValueError(
                "Overlap Nodes needs an unscaled, unrotated selected outline."
            )
        if contour.isTT:
            rows.append(outline_writer.Change("contour", "", "quadratic contour kept"))
            continue
        planned: dict[int, Move] = {}
        for index, node in enumerate(nodes):
            if not node.selected or not node.isOn():
                continue
            for direction in (1, -1):
                indices = [index + direction * step for step in (1, 2)]
                if len(nodes) < 3 or (
                    not contour.closed
                    and any(i < 0 or i >= len(nodes) for i in indices)
                ):
                    continue
                corner, handle = [nodes[i % len(nodes)] for i in indices]
                if not corner.isOn() or handle.isOn():
                    continue
                x = (
                    math.trunc(node.x + offset[0] + shear * (handle.y - node.y))
                    - offset[0]
                )
                proposed = [
                    (corner, node.x, node.y, False),
                    (handle, x, handle.y, None),
                ]
                for item in proposed:
                    key = id(item[0])
                    if key in planned and planned[key][1:] != item[1:]:
                        raise ValueError(
                            "Selected tips give conflicting targets; select one tip per corner."
                        )
                    planned[key] = item
                break
        moves = [
            item
            for item in planned.values()
            if abs(item[0].x - item[1]) > 1e-8
            or abs(item[0].y - item[2]) > 1e-8
            or (item[3] is not None and bool(item[0].smooth) != item[3])
        ]
        if moves:
            rows.append(
                outline_writer.Change(
                    "tip neighbours",
                    str(len(moves)),
                    f"overlap · italic {angle:g}°",
                    moves,
                )
            )
    return rows


class SelectionPanel(outline_panel.panel_type()):
    """Non-modal preview and one action over selected glyph master layers."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, ACTION, DONE, "contour"
    HEADERS: tuple[str, ...] = ("Glyph · layer", "Selection", "Now", "After")

    def on_reload(self) -> None:
        """Keep automatic dependants outside the editable domain."""
        self.current_layers: set[tuple[str, str]] | None = None
        self.bases.setChecked(False)
        self.bases.setEnabled(False)
        self.bases.setVisible(False)
        self.scope.setItemText(0, "Selected layers")

    def chosen_masters(self) -> list[str]:
        """Use exact selected editor layers, or all declared masters."""
        if self.scope.currentIndex == 1:
            self.current_layers = None
            return list(self.masters)
        try:
            selected = layer_selection.capture(monotonic() + 2.0)
        except TimeoutError as error:
            raise ValueError(str(error)) from error
        if any(
            int(item.package.id) != int(self.package_id)
            for item in selected.occurrences
        ):
            raise ValueError(
                "Selected layers belong to another font; reload selection."
            )
        self.current_layers = {
            (item.glyph.name, item.layer.name) for item in selected.occurrences
        }
        return list(dict.fromkeys(item.layer.name for item in selected.occurrences))

    def selected_planner(self, plan: outline_writer.Planner) -> outline_writer.Planner:
        """Exclude unselected glyph/layer combinations from a mixed-layer batch."""
        selected = self.current_layers
        return lambda glyph, name, layer: (
            plan(glyph, name, layer)
            if selected is None or (glyph.name, name) in selected
            else []
        )

    def options(self) -> dict[str, Any]:
        """Never allow edits to bases of automatic composites."""
        return {"compatible": False, "allow_bases": False}

    def editor(self) -> outline_writer.Editor:
        """Return the coordinate writer for this action."""
        return NodeEditor()

    def planner(self) -> outline_writer.Planner:
        """Read angles once; resolve each edited layer to its own master."""
        angles = masters.italic_angles(self.package, list(self.masters))

        def plan(glyph: Any, name: str, layer: Any) -> list[outline_writer.Change]:
            associated = masters.associated_master(layer.name, self.masters)
            if associated is None:
                raise ValueError(
                    f"{layer.name}: no associated master; cannot read its italic angle."
                )
            return tip_changes(layer, angles[associated])

        return self.selected_planner(plan)


def main() -> Any:
    """Open one reusable panel for this menu."""
    return scripting.show_script_dialog(SelectionPanel, KEY)


if __name__ == "__main__":
    main()
