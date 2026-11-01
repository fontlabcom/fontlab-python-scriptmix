# this_file: Scripts/Contours/Align And Distribute.py
# SPDX-License-Identifier: Apache-2.0
"""Align selected geometry or space selected nodes at equal intervals.

What: Six alignment choices and horizontal or vertical node distribution share
one non-modal panel. Whole selected contours move as units. Partial contours
contribute selected nodes. Components move by their transform; their base
glyphs stay. Anchors are never moved: this tool cannot read anchor selection.
Use Contour > Align Points to align selected anchors.

How: Work in upright glyph coordinates; italic angle is not applied. Alignment
uses the minimum, maximum or midpoint, or an explicit coordinate. Bounds
include selected control points, so results can differ from Contour > Align
Points. Component bounds use the transformed local bounding rectangle.
Distribution sorts selected nodes on the chosen axis, keeps both endpoints,
and divides their span equally. Ties keep contour/node order. Unselected
adjacent handles follow their moved on-curve node by the same offset. Selected
handles use their own targets. Node types and connection flags stay.

Why: Contour > Align Points aligns points on the current layer.
Element > Align / Distribute Shapes operates on shapes. This tool adds node
distribution, several glyph layers or masters in one Undo step, and a numeric
preview.

Use: Select nodes or components in a Glyph window. Choose an operation, inspect
the table and Apply. All nodes is for alignment only; distribution requires
selected nodes. All masters processes each loaded glyph's masters; node
selection is read separately in each layer. Reload selection after choosing
other glyphs or editor layers. Apply reads selected layers and geometry again.
A single item with Selection bounds has no move. Choose Coordinate to move it.
Two selected nodes that share one curve handle are kept; select the handle
too, or align them one at a time.
Automatic guide/metric snapping and italic deskew are not provided.

Benefit: Repeat alignment without reopening a dialog. Each Apply is recorded
as one Undo step. Automatic-layer glyphs and their bases are skipped. Locked
layers/shapes, shared node data and contours with their own transform are kept
and named in the preview; the other eligible items can still change. Advances,
anchors and guides stay. FontLab can round coordinates to its grid.

Source: Independent behaviour-only rewrite after Alex Slobzheninov,
https://github.com/slobzheninov/Glyphs-Scripts, Align/Align Top.py,
Align Bottom.py, Align Left.py, Align Right.py, Align Horizontal Center.py,
Align Vertical Center.py, Distribute Nodes Horizontally.py and Distribute Nodes
Vertically.py, Apache-2.0. The sources credit Rainer Erich Scheichelbauer
(mekkablue, Apache-2.0). No source code, identifiers or comments were copied.
"""

import math
from time import monotonic
from types import SimpleNamespace
from typing import Any

import fly.ap.affine as affine  # noqa: PLR0402
import fly.ap.layer_selection as layer_selection  # noqa: PLR0402
import fly.ap.outline_panel as outline_panel  # noqa: PLR0402
import fly.ap.outline_transform as outline_transform  # noqa: PLR0402
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402
import fly.ap.scripting as scripting  # noqa: PLR0402

TITLE, KEY = "Align And Distribute", "contours_align_and_distribute"
OPERATIONS = (
    ("Left", "left"),
    ("Right", "right"),
    ("Horizontal center", "horizontal"),
    ("Bottom", "bottom"),
    ("Top", "top"),
    ("Vertical center", "vertical"),
    ("Distribute horizontally", "distribute_x"),
    ("Distribute vertically", "distribute_y"),
)
XY = tuple[float, float]
# One node plus its glyph point and inverse shape transform.
Entry = tuple[Any, XY, affine.Affine]
# Kind, native item, member nodes and glyph-space bounding points.
Group = tuple[str, Any, list[Entry], list[XY]]


def kept(item: str, reason: str) -> outline_writer.Change:
    """Show an unchanged item; collect supplies its glyph and layer label."""
    return outline_writer.Change(item, "", f"{reason}, kept")


def contour_groups(
    shape: Any, contour: Any, all_nodes: bool, distribute: bool
) -> list[Group]:
    """Pair each selected on-curve node with its unselected adjacent controls."""
    nodes = list(contour.nodes())
    chosen = [i for i, node in enumerate(nodes) if all_nodes or node.selected]
    if not chosen:
        return []
    if affine.from_qtransform(contour.transform) != affine.IDENTITY:
        raise ValueError("contour has its own transform")
    forward = affine.from_qtransform(shape.transform)
    backward = affine.invert(forward)
    entries = [
        (node, affine.apply(forward, float(node.x), float(node.y)), backward)
        for node in nodes
    ]
    if not distribute and len(chosen) == len(nodes):
        return [("contour", contour, entries, [entry[1] for entry in entries])]
    groups, claimed = [], {}
    for index in chosen:
        members = [entries[index]]
        if nodes[index].isOn():
            for neighbour in (index - 1, index + 1):
                if not contour.closed and not 0 <= neighbour < len(nodes):
                    continue
                neighbour %= len(nodes)
                handle = nodes[neighbour]
                if handle.isOn() or neighbour in chosen:
                    continue
                if claimed.get(neighbour, index) != index:
                    raise ValueError("a curve handle has two selected owners")
                if neighbour not in claimed:
                    members.append(entries[neighbour])
                claimed[neighbour] = index
        groups.append(("node", nodes[index], members, [entries[index][1]]))
    return groups


def node_groups(
    layer: Any, all_nodes: bool, distribute: bool
) -> tuple[list[Group], list[outline_writer.Change]]:
    """Keep unsafe shapes/contours individually; return eligible node groups."""
    groups, notes = [], []
    for si, shape in enumerate(layer.shapes, 1):
        if shape.isComponent:
            continue
        contours = [
            c for c in shape.contours if any(all_nodes or n.selected for n in c.nodes())
        ]
        if not contours:
            continue
        label = f"shape {si}"
        if shape.contentLocked:
            notes.append(kept(label, "locked shape"))
            continue
        if int(shape.shapeData.referenceCount) > 1 or list(shape.includesList):
            notes.append(kept(label, "shared outline data"))
            continue
        for ci, contour in enumerate(contours, 1):
            try:
                groups.extend(contour_groups(shape, contour, all_nodes, distribute))
            except ValueError as error:
                notes.append(kept(f"{label}, contour {ci}", str(error)))
    return groups, notes


def component_groups(layer: Any) -> tuple[list[Group], list[outline_writer.Change]]:
    """Read selected component rectangles; never edit their base outlines."""
    groups, notes = [], []
    for index, shape in enumerate(layer.shapes, 1):
        if not shape.isComponent or not shape.selected:
            continue
        if shape.contentLocked:
            notes.append(kept(f"component {index}", "locked component"))
            continue
        try:
            box = shape.boundingBox
            matrix = affine.from_qtransform(shape.transform)
            points = [
                affine.apply(matrix, x, y)
                for x in (box.x(), box.x() + box.width())
                for y in (box.y(), box.y() + box.height())
            ]
            groups.append(("component", shape, [], points))
        except ValueError as error:
            notes.append(kept(f"component {index}", str(error)))
    return groups, notes


def position(points: list[XY], axis: int, fraction: float) -> float:
    """Coordinate at fraction 0, 0.5 or 1 of an item's coordinate bounds."""
    values = [point[axis] for point in points]
    low, high = min(values), max(values)
    value = low * (1 - fraction) + high * fraction
    if not math.isfinite(value):
        raise ValueError("Geometry exceeds the finite coordinate range.")
    return value


def group_edit(group: Group, dx: float, dy: float) -> Any:
    """Build node moves and delegate component transforms to the shared writer."""
    if not all(math.isfinite(v) for v in (dx, dy)):
        raise ValueError("Geometry exceeds the finite coordinate range.")
    kind, item, entries, _ = group
    if kind == "component":
        proxy = SimpleNamespace(shapes=[item], anchors=[])
        rows = outline_transform.transform_changes(
            proxy, (1, 0, 0, 1, dx, dy), False, "move"
        )
        return ([], [r.edit for r in rows if r.edit is not None])
    moves = []
    for node, (x, y), backward in entries:
        nx, ny = affine.apply(backward, x + dx, y + dy)
        moves.append((node, nx, ny))
    return (moves, [])


def plan_layer(
    layer: Any,
    mode: str,
    all_nodes: bool = False,
    coordinate: float | None = None,
) -> list[outline_writer.Change]:
    """Plan each layer independently; stable distribution never changes endpoints."""
    if mode not in {key for _, key in OPERATIONS}:
        raise ValueError("Choose a supported operation.")
    if coordinate is not None and not math.isfinite(coordinate):
        raise ValueError("Enter a finite coordinate.")
    distribute = mode.startswith("distribute_")
    if distribute and all_nodes:
        raise ValueError("Distribution needs selected nodes; choose Selected geometry.")
    has_nodes = any(
        all_nodes or n.selected
        for s in layer.shapes
        if not s.isComponent
        for c in s.contours
        for n in c.nodes()
    )
    has_components = (
        not distribute
        and not all_nodes
        and any(s.isComponent and s.selected for s in layer.shapes)
    )
    if not has_nodes and not has_components:
        return []
    if layer.isLocked or layer.isMaskLayer or layer.isService:
        return [kept("layer", "locked or non-body layer")]
    groups, notes = node_groups(layer, all_nodes, distribute)
    if not distribute and not all_nodes:
        components, component_notes = component_groups(layer)
        groups += components
        notes += component_notes
    if not groups:
        return notes
    if distribute and len(groups) < 3:
        return notes + [kept("nodes", "select at least three nodes to distribute")]
    axis = 0 if mode in {"left", "right", "horizontal", "distribute_x"} else 1
    fraction = 0 if mode in {"left", "bottom"} or distribute else 1
    if mode in {"horizontal", "vertical"}:
        fraction = 0.5
    points = [point for group in groups for point in group[3]]
    try:
        target = position(points, axis, fraction) if coordinate is None else coordinate
    except ValueError as error:
        return notes + [kept("geometry", str(error))]
    if distribute:
        groups.sort(key=lambda group: group[3][0][axis])
    rows = list(notes)
    for index, group in enumerate(groups):
        try:
            old = position(group[3], axis, fraction)
            if distribute:
                ratio = index / (len(groups) - 1)
                target = position(points, axis, ratio)
            distance = target - old
            if abs(distance) <= 1e-8:
                continue
            edit = group_edit(
                group, distance if axis == 0 else 0, distance if axis == 1 else 0
            )
        except ValueError as error:
            rows.append(kept(f"{group[0]} {index + 1}", str(error)))
            continue
        rows.append(
            outline_writer.Change(
                f"{group[0]} {index + 1}",
                f"{'x' if axis == 0 else 'y'} {old:g}",
                f"{target:g} ({distance:+g})",
                edit,
            )
        )
    return rows


class GeometryEditor(outline_writer.Editor):
    """Move original nodes and compose component placements without copies."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        """Write each planned coordinate and the prepared component matrices."""
        for moves, shapes in steps:
            for node, x, y in moves:
                node.x, node.y = x, y
            outline_transform.TransformEditor().write(layer, shapes)

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        """Return a layer-labelled text for each missing node or component move."""
        misses = []
        for layer, steps in prepared:
            for moves, shapes in steps:
                if any(
                    not math.isfinite(n.x)
                    or not math.isfinite(n.y)
                    or abs(n.x - x) > 0.5
                    or abs(n.y - y) > 0.5
                    for n, x, y in moves
                ):
                    misses.append(
                        f"{layer.name}: node coordinates differ from the plan"
                    )
                misses.extend(
                    outline_transform.TransformEditor().check([(layer, shapes)])
                )
        return misses


class GeometryPanel(outline_panel.panel_type()):
    """Preview repeated alignment actions through the shared history panel."""

    TITLE, KEY, UNIT = TITLE, KEY, "move"
    HEADERS = ("Glyph · layer", "Selection", "Now", "After")

    def build_controls(self) -> None:
        """Operation, node scope and optional coordinate target."""
        from fly import qt

        self.operation_box = qt.QtGui.QComboBox()
        for label, _ in OPERATIONS:
            self.operation_box.addItem(label)
        self.node_scope = qt.QtGui.QComboBox()
        for label in ("Selected geometry", "All nodes"):
            self.node_scope.addItem(label)
        self.reference_box = qt.QtGui.QComboBox()
        for label in ("Selection bounds", "Coordinate"):
            self.reference_box.addItem(label)
        self.target_value = self.spin(-1000000, 1000000, 0, " units", decimals=2)
        self.add_row("Operation", self.operation_box)
        self.add_row("Geometry", self.node_scope)
        self.add_row("Align to", self.reference_box, self.target_value)
        for box in (self.operation_box, self.node_scope, self.reference_box):
            self.watch(box.currentIndexChanged, self.control_changed)
        self.control_changed()

    def on_reload(self) -> None:
        """Use exact editor occurrences, including an unencoded current glyph."""
        self.layer_keys: set[tuple[str, str]] = set()
        self.layer_names: list[str] = []
        self.bases.setChecked(False)
        self.bases.setEnabled(False)
        self.bases.setVisible(False)
        self.scope.setItemText(0, "Selected layers")
        if self.package is not None:
            selected = self.capture_layers()
            self.glyphs = list(
                {i.glyph.name: i.glyph for i in selected.occurrences}.values()
            )

    def validate_selection(self, selection: Any) -> None:
        """Refuse cross-font selection before reading or writing geometry."""
        if any(
            int(item.package.id) != int(self.package_id)
            for item in selection.occurrences
        ):
            raise ValueError(
                "Selected layers belong to another font; reload selection."
            )

    def capture_layers(self) -> Any:
        """Capture once per scan or action; never from a control-change preview."""
        selected = layer_selection.capture(monotonic() + 2)
        self.validate_selection(selected)
        self.layer_keys = {(i.glyph.name, i.layer.name) for i in selected.occurrences}
        self.layer_names = list(
            dict.fromkeys(i.layer.name for i in selected.occurrences)
        )
        return selected

    def chosen_masters(self) -> list[str]:
        """Use cached editor layers or every declared master."""
        return (
            list(self.masters)
            if self.scope.currentIndex == 1
            else list(self.layer_names)
        )

    def intro(self) -> str:
        """Give the correct selection surface when no glyph is loaded."""
        if self.package is None:
            return "Open a font first."
        if not self.glyphs:
            return "Select nodes or components in a Glyph window, then press Reload selection."
        return f"{len(self.glyphs)} glyph(s): " + ", ".join(
            g.name for g in self.glyphs[:8]
        )

    def control_changed(self) -> None:
        """Update control availability without reading editor selection."""
        distribute = self.operation_box.currentIndex >= 6
        self.reference_box.setEnabled(not distribute)
        self.target_value.setEnabled(
            not distribute and self.reference_box.currentIndex == 1
        )
        if hasattr(self, "apply_button"):
            self.refresh()

    def options(self) -> dict[str, Any]:
        """Keep automatic dependants outside the editable domain."""
        return {"compatible": False, "allow_bases": False}

    def planner(self) -> outline_writer.Planner:
        """Capture controls; read live node selection separately on each layer."""
        mode = OPERATIONS[self.operation_box.currentIndex][1]
        distribute = mode.startswith("distribute_")
        numeric = self.reference_box.currentIndex == 1 and not distribute
        coordinate = float(self.target_value.value) if numeric else None
        all_nodes = self.node_scope.currentIndex == 1
        if distribute and all_nodes:
            raise ValueError(
                "Distribution needs selected nodes; choose Selected geometry."
            )
        keys = None if self.scope.currentIndex == 1 else self.layer_keys
        return lambda glyph, master, layer: (
            plan_layer(layer, mode, all_nodes, coordinate)
            if keys is None or (glyph.name, master) in keys
            else []
        )

    def editor(self) -> outline_writer.Editor:
        """Use one geometry writer for all eight operations."""
        return GeometryEditor()

    def apply(self) -> None:
        """Capture selected layers once, then let history plan from live geometry."""
        try:
            self.live_glyphs()
            self.capture_layers()
            super().apply()
            if outline_panel.NOT_STORED in self.status.text:
                self.status.setText(
                    self.status.text + " " + outline_panel.UNDO_HINT
                )
        except (ValueError, RuntimeError, TimeoutError) as error:
            self.slot_error = str(error)
            self.apply_button.setEnabled(False)
            self.status.setText(f"Error: {error}")

    def refresh(self) -> None:
        """Contain native selection timeouts during control changes and reload."""
        try:
            super().refresh()
        except (ValueError, RuntimeError, TimeoutError) as error:
            self.slot_error = str(error)
            self.apply_button.setEnabled(False)
            self.status.setText(f"Error: {error}")


def main() -> Any:
    """Show one non-modal panel through the owned dialog registry."""
    return scripting.show_script_dialog(GeometryPanel, KEY)


if __name__ == "__main__":
    main()
