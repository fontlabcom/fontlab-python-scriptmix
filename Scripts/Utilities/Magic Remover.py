# this_file: Scripts/Utilities/Magic Remover.py
# SPDX-License-Identifier: Apache-2.0
"""Remove corresponding selected items from compatible glyph layers.

What: Preview selected polygon nodes, whole contours and components on every
compatible foreground master or intermediate layer of one glyph. If any
compatible master must keep an item, every master keeps that item.
How: Match stored shape, contour and node indices and component bases.
Use the shared outline writer. Components retain their
original history objects. The change is recorded as one Undo step.
Why: FontLab Delete with Preferences > Variations > Synchronize "Remove node"
and matching edits removes corresponding nodes, including curve nodes, on the
other masters. This panel adds a per-layer preview and explicit kept reasons.
Use: Select items in one Glyph window slot. Run the tool, inspect the rows,
then press Remove. Use selection refreshes the current editor selection.
Benefit: Remove the same detail over compatible masters without repeated edits.

Partial curve-node selections are kept: use FontLab's Delete as described above.
The public contour API does not expose curve-preserving node deletion.
Whole curved contours can be removed, along with any outline shape left empty.
Anchors are not part of selection removal: the public pin binding exposes no
selection member. Existing anchors stay unchanged.
Polygon endpoints and the minimum of three closed or two open nodes are kept.
Masks, service, locked, shared and transformed outlines are kept. Automatic
glyphs and their bases are kept. Glyphs corner-component hints have no FontLab
counterpart. For a separate outline backup, use Masters > Copy Outline To Mask
before removal; this tool never overwrites a mask on a modifier-key press.

Independent behaviour rewrite after Reza Bohloul, RezaBohloul,
Edit/Magic Remover.py; no licence declared.
Repository: https://github.com/RezaBohloul/RezaBohloul . No source code copied.
"""

from dataclasses import dataclass, field
from time import monotonic
from typing import Any

import fly.ap.history as history  # noqa: PLR0402 - Fly resolves App modules lazily
import fly.ap.layer_selection as selection
import fly.ap.outline_writer as outlines
import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly resolves App modules lazily
import fly.ap.selection_panel as panels

TITLE = "Magic Remover"
KEY = "utilities_magic_remover"
CAPTURE_SECONDS = 2.0


@dataclass
class RemovalRow:
    """One layer's prepared edits, or a kept layer and its reason."""

    glyph: Any
    layer: Any
    steps: list[Any] = field(default_factory=list)
    note: str = ""


def structure(layer: Any) -> tuple[Any, ...]:
    """Exact stored shape order, base names, contour closure and node types."""
    return tuple(
        (
            "component",
            str(shape.shapeData.componentGlyph),
            str(shape.shapeData.componentLayer),
        )
        if shape.isComponent
        else (
            "outline",
            tuple(
                (bool(c.closed), bool(c.isTT), tuple(str(n.type) for n in c.nodes()))
                for c in shape.contours
            ),
        )
        for shape in layer.shapes
    )


def selection_keys(layer: Any) -> tuple[list[Any], list[int]]:
    """Read bound node and component selections without reading pin state."""
    nodes, components = [], []
    for si, shape in enumerate(layer.shapes):
        if shape.isComponent:
            if shape.selected:
                components.append(si)
            continue
        for ci, contour in enumerate(shape.contours):
            chosen = [i for i, node in enumerate(contour.nodes()) if node.selected]
            if chosen:
                nodes.append((si, ci, chosen))
    return nodes, components


def changes(
    layer: Any, keys: tuple[list[Any], list[int]]
) -> tuple[list[Any], list[str]]:
    """Plan only supported edits; describe every selected detail that stays."""
    node_keys, component_keys = keys
    steps, notes = [], []
    editable, _ = outlines.outline_shapes(layer)
    allowed = {int(shape.id) for shape in editable}
    for si, ci, chosen in node_keys:
        shape = layer.shapes[si]
        contour = shape.contours[ci]
        nodes = contour.nodes()
        if shape.contentLocked or int(shape.id) not in allowed:
            notes.append(f"shape {si + 1}: locked, shared or transformed outline, kept")
        elif len(chosen) == len(nodes):
            steps.append(("contour", shape, contour))
        elif any(not node.isOn() for node in nodes):
            notes.append(f"contour {ci + 1}: partial curve selection, kept")
        elif len(nodes) - len(chosen) < (3 if contour.closed else 2):
            notes.append(f"contour {ci + 1}: too few nodes would remain, kept")
        elif not contour.closed and (0 in chosen or len(nodes) - 1 in chosen):
            notes.append(f"contour {ci + 1}: open endpoint selected, kept")
        else:
            steps.append(("nodes", contour, tuple(chosen)))
    for index in component_keys:
        shape = layer.shapes[index]
        if shape.contentLocked or int(shape.shapeData.referenceCount) > 1:
            notes.append(f"component {index + 1}: locked or shared, kept")
        else:
            steps.append(("component", shape, None))
    return steps, notes


def survey(glyph: Any, source: Any, facts: history.AutoFacts) -> list[RemovalRow]:
    """Veto each structural item across masters if any compatible master keeps it."""
    if (
        source.isMaskLayer
        or source.isService
        or source.isImg
        or not source.isMasterLayer
    ):
        raise ValueError("Select items on a foreground master or intermediate layer.")
    keys = selection_keys(source)
    if not any(keys):
        raise ValueError("Select nodes or components in one Glyph window slot.")
    signature = structure(source)
    refused = history.refusal(facts, glyph.name, "geometry")
    if refused:
        return [RemovalRow(glyph, source, note="kept: " + refused)]
    rows = []
    compatible = []
    for layer in glyph.layers:
        why = ""
        if layer.isMaskLayer or layer.isService or not layer.isMasterLayer:
            why = "not a foreground master or intermediate layer"
        elif structure(layer) != signature:
            why = "incompatible shape or node structure"
        if why:
            rows.append(RemovalRow(glyph, layer, note="kept: " + why))
            continue
        compatible.append(layer)
    edits = {int(layer.id): [] for layer in compatible}
    details = [
        (f"contour {si + 1}.{ci + 1}", ([key], []))
        for key in keys[0]
        for si, ci, _ in [key]
    ]
    details.extend((f"component {index + 1}", ([], [index])) for index in keys[1])
    for label, detail in details:
        planned = []
        for layer in compatible:
            if layer.isLocked or layer.autoLayer or layer.isImg:
                steps, notes = [], ["locked, automatic or image layer"]
            else:
                steps, notes = changes(layer, detail)
            if notes or not steps:
                reason = "; ".join(notes) or "item cannot be removed"
                rows.append(
                    RemovalRow(
                        glyph,
                        layer,
                        note=f"{layer.name}: {label}: {reason}; kept on all masters",
                    )
                )
                break
            planned.append((layer, steps))
        else:
            for layer, steps in planned:
                edits[int(layer.id)].extend(steps)
    rows.extend(
        RemovalRow(glyph, layer, edits[int(layer.id)])
        for layer in compatible
        if edits[int(layer.id)]
    )
    return rows


class RemovalEditor(outlines.Editor):
    """Retain component history and remove outline shapes that become empty."""

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        steps = []
        for kind, item, value in edits:
            if kind == "nodes":
                survivors = tuple(
                    (float(node.x), float(node.y), str(node.type))
                    for i, node in enumerate(item.nodes())
                    if i not in value
                )
                value = (value, survivors)
            elif kind == "contour":
                removed = sum(
                    1
                    for tag, shape, _ in edits
                    if tag == "contour" and shape.id == item.id
                )
                value = (value, removed == len(item.contours))
            steps.append((kind, item, value))
        return steps

    def retain(self, steps: list[Any]) -> list[Any]:
        return [
            obj
            for kind, item, _ in steps
            if kind == "component"
            for obj in history.component_history(item)
        ]

    def write(self, layer: Any, steps: list[Any]) -> None:
        for kind, item, value in steps:
            if kind == "component":
                layer.removeShape(item)
            elif kind == "contour":
                item.removeContour(value[0])
                item.changed()
                if not item.contours:
                    layer.removeShape(item)
            else:
                for index in reversed(value[0]):
                    item.removeAt(index)

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        """Check node survivors, removed contours and emptied outline shapes."""
        missed = []
        for layer, steps in prepared:
            for kind, item, value in steps:
                if kind == "component" and any(s.id == item.id for s in layer.shapes):
                    missed.append(f"{layer.name}: component")
                elif kind == "contour":
                    present = any(s.id == item.id for s in layer.shapes)
                    if present == value[1] or (
                        present and any(c.id == value[0].id for c in item.contours)
                    ):
                        missed.append(f"{layer.name}: contour or empty shape")
                elif (
                    kind == "nodes"
                    and tuple(
                        (float(node.x), float(node.y), str(node.type))
                        for node in item.nodes()
                    )
                    != value[1]
                ):
                    missed.append(f"{layer.name}: node removal")
        return missed


def write_rows(rows: list[RemovalRow], facts: history.AutoFacts) -> dict[str, int]:
    """Write ready rows in one shared outline-writer action."""
    work = [
        (r.glyph, r.layer, r.steps)
        for r in rows
        if not r.note and not history.refusal(facts, r.glyph.name, "geometry")
    ]
    try:
        return outlines.apply_work(work, TITLE, facts, RemovalEditor())
    except RuntimeError as error:
        if "Native changes may remain" in str(error):
            raise
        raise RuntimeError(
            f"{error} Native changes may remain; use Edit > Undo."
        ) from error


class MagicPanel(panels.panel_type()):
    """A modeless preview bound to the current font and one selected editor slot."""

    TITLE, KEY, ACTION = TITLE, KEY, "Remove"
    HEADERS = ("Glyph · layer", "Action")
    SCOPE, CONSENT, ALIGN = False, "", False

    def plan(self) -> list[RemovalRow]:
        package = self.font_package()
        captured = selection.capture(monotonic() + CAPTURE_SECONDS)
        if captured.context[2] != "editor" or len(captured.occurrences) != 1:
            raise ValueError("Select exactly one glyph slot in the Glyph window.")
        self.editor_carrier = captured
        item = captured.occurrences[0]
        if int(item.package.id) != int(package.id):
            raise ValueError("The font changed. Run this script again.")
        self.names = [str(item.glyph.name)]
        return survey(item.glyph, item.layer, history.scan_auto_facts(package))

    def reselect(self) -> None:
        self.refresh()

    def cells(self, row: RemovalRow) -> list[str]:
        return [
            f"{row.glyph.name} · {row.layer.name}",
            row.note or f"remove {len(row.steps)} item(s)",
        ]

    def write(self, package: Any, rows: list[RemovalRow]) -> dict[str, int]:
        return write_rows(rows, history.scan_auto_facts(package))

    def result_text(self, result: dict[str, int]) -> str:
        return f"Removed {result['edits']} item(s) on {result['layers']} layer(s)"


def main() -> Any:
    """Show the shared non-modal preview, or diagnose an opening refusal."""
    try:
        return scripting.show_script_dialog(MagicPanel, KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        from fly import fl, qt

        qt.QtGui.QMessageBox.warning(fl.MainWindow(), TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
