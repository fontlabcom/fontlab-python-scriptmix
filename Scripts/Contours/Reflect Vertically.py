# this_file: Scripts/Contours/Reflect Vertically.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Reflect Vertically
"""Reflect selected nodes and components vertically about their combined centre.


How: A glyph-space reflection maps selected own nodes and composes selected
component placements. Shape transforms are accounted for. Selected node bounds include handles;
component bounds use the transformed local bounding rectangle. Unselected
geometry stays; the table identifies the per-layer centre before Apply.

Why: FontLab's Tools > Flip Vertical command covers this reflection.
This panel adds a preview and processes several masters or selected layers
in one action. Each action is recorded as one Undo step. Contours > Transform
instead transforms whole layers.

Use: Select nodes or components. Open the panel, inspect the table and
press Reflect. Choose all masters to process stored selections on multiple
master layers together. Reload selection after choosing other glyphs.

Benefit: Repeat a selection edit across glyphs with one planned batch action.

Safety: Locked layers, locked shapes and shared selected outline data are
refused. Contours with their own transform are refused. Automatic-layer
glyphs and their bases are skipped. The action replans live node selection before writing. A failed write names Edit > Undo.
The change is recorded as one Undo step. Anchors, guides, widths and node
order stay. FontLab can round node coordinates to its grid.

Source: Independent behaviour-only rewrite after Alex Slobzheninov
(slobzheninov), https://github.com/slobzheninov/Glyphs-Scripts,
Apache-2.0. No source code, identifiers or comments were copied.
Behaviour source: Reflect/Reflect Vertically.py.
"""

import math
from time import monotonic
from typing import Any

import fly.ap.affine as affine  # noqa: PLR0402
import fly.ap.layer_selection as layer_selection  # noqa: PLR0402
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


TITLE = "Reflect Vertically"
KEY = "contours_reflect_vertically"
ACTION, DONE = "Reflect", "Reflected"


def LINEAR(value: float) -> affine.Affine:
    """Reflection linear part in glyph coordinates."""
    return (1, 0, 0, -1, 0, 0)


def selection_matrix(value: float, centre: XY) -> affine.Affine:
    """Map glyph coordinates about the selected geometry centre."""
    if not math.isfinite(value):
        raise ValueError("Enter a finite angle.")
    linear = LINEAR(value)
    ox, oy = centre
    a, b, c, d, _, _ = linear
    return affine.concat(
        linear, (1, 0, 0, 1, ox - a * ox - c * oy, oy - b * ox - d * oy)
    )


def selection_changes(layer: Any, value: float) -> list[outline_writer.Change]:
    """Plan selected nodes and component transforms in glyph coordinates."""
    entries, coordinates, components = [], [], []
    for shape, _, nodes in selected_contours(layer):
        forward = affine.from_qtransform(shape.transform)
        backward = affine.invert(forward)
        for node in nodes:
            if node.selected:
                point = affine.apply(forward, float(node.x), float(node.y))
                coordinates.append(point)
                entries.append((node, point, backward))
    for shape in layer.shapes:
        if not shape.isComponent or not shape.selected:
            continue
        if layer.isLocked or shape.contentLocked:
            raise ValueError("Unlock the selected layer and component first.")
        box = shape.boundingBox
        forward = affine.from_qtransform(shape.transform)
        for x in (box.x(), box.x() + box.width()):
            for y in (box.y(), box.y() + box.height()):
                coordinates.append(affine.apply(forward, x, y))
        components.append(shape)
    if not coordinates:
        return []
    xs, ys = zip(*coordinates, strict=True)
    centre = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
    matrix = selection_matrix(value, centre)
    moves = []
    for node, point, backward in entries:
        x, y = affine.apply(backward, *affine.apply(matrix, *point))
        if abs(x - node.x) > 1e-8 or abs(y - node.y) > 1e-8:
            moves.append((node, x, y, None))
    shapes = [
        (shape, affine.concat(affine.from_qtransform(shape.transform), matrix))
        for shape in components
        if matrix != affine.IDENTITY
    ]
    if not moves and not shapes:
        return []
    origin = f"centre {centre[0]:g}, {centre[1]:g}"
    return [
        outline_writer.Change(
            "selected geometry",
            f"{len(entries)} nodes, {len(components)} components",
            origin,
            (moves, shapes),
        )
    ]


class SelectionEditor(NodeEditor):
    """Keep node selection and compose selected component placements."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        """Change original coordinates and whole component matrices."""
        from fly import qt

        for moves, shapes in steps:
            super().write(layer, [moves])
            for shape, matrix in shapes:
                shape.transform = qt.QtGui.QTransform(*matrix)
                shape.changed()

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        """Read all moved points and all component matrix fields back."""
        for layer, steps in prepared:
            super().check([(layer, [moves for moves, _ in steps])])
            for _, shapes in steps:
                for shape, matrix in shapes:
                    now = affine.from_qtransform(shape.transform)
                    if any(abs(a - b) > 1e-6 for a, b in zip(now, matrix, strict=True)):
                        raise RuntimeError(
                            "Component placement differs. Native changes may remain; use Edit > Undo."
                        )
        return []


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
        return SelectionEditor()

    def planner(self) -> outline_writer.Planner:
        """Plan each stored node/component selection about its own centre."""
        return self.selected_planner(
            lambda glyph, master, layer: selection_changes(layer, 0)
        )


def main() -> Any:
    """Open one reusable panel for this menu."""
    return scripting.show_script_dialog(SelectionPanel, KEY)


if __name__ == "__main__":
    main()
