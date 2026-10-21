# this_file: Scripts/Contours/Node Duplicator.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Node Duplicator
"""Insert coincident nodes, with optional coincident cubic handles.

What: Duplicate selected on-curve nodes in selected editor layers or masters.
How: Read node indices from each glyph's selected reference layer. Require the same
contour closure and node types in every target master, then insert backwards.
The optional two handles create a zero-length cubic instead of a line.
Why: One selection controls corresponding nodes across masters. Unrelated
glyphs never inherit indices from the first glyph. The table previews counts.
Use: Select nodes, open this panel, choose scope and handles, then Duplicate.
Reload selection after changing glyphs. Disable Keep masters compatible only
when you intend to edit the current master separately.
Benefit: Prepare matching contour construction without dragging new nodes.

Locked, shared, transformed, quadratic and automatic outlines are kept and
listed. Other glyphs in the selection can still be edited.
Master scope targets only master layers. Only selected editor layers also
supports manual auxiliary layers and intentionally changes their structure
without a cross-master compatibility check. The change is recorded as one Undo step.
Existing nodes and shape metadata stay; new nodes are sharp. Both handle
positions coincide with the selected point, so the added segment has no area.

Independent behaviour-only rewrite after Fernando Díaz, Reset Type Studio,
https://github.com/Reset-Type-Studio/Glyphs-Scripts, Apache-2.0 declared in
README.md (no separate LICENSE file). Sources: Paths/Node Duplicator
(all masters).py, Paths/Node Duplicator (current layer).py, and
Paths/Node Duplicator + 2 Handles (all masters).py. No source code copied.
"""

import math
from time import monotonic
from typing import Any

import fly.ap.affine as affine  # noqa: PLR0402
import fly.ap.layer_selection as layer_selection  # noqa: PLR0402
import fly.ap.outline_panel as outline_panel  # noqa: PLR0402
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402
import fly.ap.scripting as scripting  # noqa: PLR0402

TITLE, KEY = "Node Duplicator", "contours_node_duplicator"
CAPTURE_SECONDS = 2.0


def contours_of(layer: Any) -> tuple[list[Any], str]:
    """Return safe own contours and a per-layer reason when content is kept."""
    result = []
    if layer.isLocked or layer.autoLayer:
        return [], "locked or automatic layer, kept"
    for shape in layer.shapes:
        if shape.isComponent:
            continue
        if (
            shape.contentLocked
            or int(shape.shapeData.referenceCount) > 1
            or list(shape.includesList)
            or affine.from_qtransform(shape.transform) != affine.IDENTITY
        ):
            return [], "locked, shared or transformed outline, kept"
        for contour in shape.contours:
            if (
                contour.isTT
                or affine.from_qtransform(contour.transform) != affine.IDENTITY
            ):
                return [], "quadratic or transformed contour, kept"
            if any(
                not math.isfinite(float(v)) for n in contour.nodes() for v in (n.x, n.y)
            ):
                return [], "non-finite contour coordinates, kept"
            result.append(contour)
    return result, ""


def signature(contours: list[Any]) -> tuple[Any, ...]:
    """Contour order, closure and full on/off pattern prove index correspondence."""
    return tuple(
        (bool(c.closed), tuple(bool(n.isOn()) for n in c.nodes())) for c in contours
    )


def duplicate_changes(
    glyph: Any, layer: Any, reference: str, handles: bool
) -> list[outline_writer.Change]:
    """Map this glyph's live reference selection to structurally equal targets."""
    source = glyph.findLayer(reference)
    if source is None or source.isNull:
        return [outline_writer.Change("layer", "", "reference layer missing, kept")]
    try:
        before, source_note = contours_of(source)
        target, target_note = contours_of(layer)
    except ValueError as error:
        return [outline_writer.Change("layer", "", f"{error}; kept")]
    if source_note or target_note:
        return [outline_writer.Change("layer", "", source_note or target_note)]
    chosen = [
        (i, j)
        for i, c in enumerate(before)
        for j, n in enumerate(c.nodes())
        if n.isOn() and n.selected
    ]
    if not chosen:
        return [
            outline_writer.Change("nodes", "0 selected", "Select on-curve nodes first")
        ]
    if signature(before) != signature(target):
        return [outline_writer.Change("nodes", "", "masters differ, kept")]
    rows = []
    for i, contour in enumerate(target):
        indices = tuple(j for ci, j in chosen if ci == i)
        if indices:
            rows.append(
                outline_writer.Change(
                    f"contour {i + 1}",
                    str(len(contour.nodes())),
                    f"+{len(indices) * (3 if handles else 1)} nodes",
                    (contour, indices, handles),
                    key=(signature(target), i, indices, handles),
                )
            )
    return rows


class DuplicateEditor(outline_writer.Editor):
    """Construct new nodes before history and insert into existing contours."""

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        from fly import fl, qt

        steps = []
        for contour, indices, handles in edits:
            nodes, inserts = list(contour.nodes()), []
            expected = outline_writer.node_points(contour)
            for index in reversed(indices):
                old = nodes[index]
                kinds = ("curve", "curve", "on") if handles else ("on",)
                fresh = [
                    fl.flNode(qt.QtCore.QPointF(old.x, old.y), nodeType=k)
                    for k in kinds
                ]
                for node in fresh:
                    node.smooth = False
                inserts.append((index + 1, fresh))
                expected[index + 1 : index + 1] = [
                    (float(n.x), float(n.y), k == "on")
                    for n, k in zip(fresh, kinds, strict=True)
                ]
            steps.append((contour, inserts, expected))
        return steps

    def write(self, layer: Any, steps: list[Any]) -> None:
        for contour, inserts, _ in steps:
            for index, nodes in inserts:
                contour.insert(index, nodes)

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed = []
        for layer, steps in prepared:
            for contour, _, expected in steps:
                actual = outline_writer.node_points(contour)
                if (
                    len(actual) != len(expected)
                    or not all(math.isfinite(v) for p in actual for v in p[:2])
                    or any(
                        a[2] != b[2] or math.dist(a[:2], b[:2]) > 0.75
                        for a, b in zip(actual, expected)
                    )
                ):
                    missed.append(str(layer.name))
        return missed


class DuplicatePanel(outline_panel.panel_type()):
    """Corresponding master scope, compatibility and handle construction."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Duplicate", "Duplicated in", "contour"
    STRUCTURAL = True

    def build_controls(self) -> None:
        from fly import qt

        self.add_handles = qt.QtGui.QCheckBox("Add two coincident cubic handles")
        self.add_row("Segment", self.add_handles)
        self.watch(self.add_handles.toggled)
        self.editor_layers = qt.QtGui.QCheckBox(
            "Only selected editor layers (ignore master scope)"
        )
        self.add_row("Scope", self.editor_layers)
        self.watch(self.editor_layers.toggled, self.sync_scope_controls)

    def sync_scope_controls(self) -> None:
        """Make the explicit layer-only mode visible in the master controls."""
        selected = self.editor_layers.isChecked()
        self.scope.setEnabled(not selected)
        self.compatible.setEnabled(not selected)
        if selected:
            self.compatible.setChecked(False)
        self.refresh()

    def chosen_masters(self) -> list[str]:
        """Capture once per plan; both scope and planner use the same facts."""
        self._capture_problem = ""
        self._selection_snapshot = None
        self._selected_occurrences = ()
        try:
            self._selection_snapshot = layer_selection.capture(
                monotonic() + CAPTURE_SECONDS
            )
            self._selected_occurrences = self._selection_snapshot.occurrences
        except (ValueError, TimeoutError) as error:
            self._capture_problem = str(error)
        if self.editor_layers.isChecked():
            return list(
                dict.fromkeys(str(r.layer.name) for r in self._selected_occurrences)
            )
        return super().chosen_masters()

    def options(self) -> dict[str, Any]:
        values = super().options()
        if self.editor_layers.isChecked():
            values["compatible"] = False
        return values

    def planner(self) -> outline_writer.Planner:
        if self._capture_problem:
            # The shared refresh catches ValueError; preserve capture diagnostics.
            raise ValueError(self._capture_problem)
        handles = self.add_handles.isChecked()
        selected = self.editor_layers.isChecked()
        occurrences = self._selected_occurrences
        sources: dict[str, list[str]] = {}
        for row in occurrences:
            sources.setdefault(str(row.glyph.name), []).append(str(row.layer.name))

        def plan(glyph: Any, master: str, layer: Any) -> list[outline_writer.Change]:
            names = list(dict.fromkeys(sources.get(str(glyph.name), [])))
            if selected:
                return (
                    duplicate_changes(glyph, layer, str(layer.name), handles)
                    if str(layer.name) in names
                    else []
                )
            if len(names) > 1:
                return [
                    outline_writer.Change("layers", "", "two reference layers, kept")
                ]
            reference = names[0] if names else self.current_master
            return duplicate_changes(glyph, layer, reference, handles)

        return plan

    def editor(self) -> outline_writer.Editor:
        return DuplicateEditor()


def main() -> Any:
    """Open the modeless panel; report font and selection errors safely."""
    try:
        return scripting.show_script_dialog(DuplicatePanel, KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        from fly import fl, qt

        qt.QtGui.QMessageBox.warning(fl.MainWindow(), TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
