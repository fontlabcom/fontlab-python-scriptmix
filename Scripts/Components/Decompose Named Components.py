# this_file: Scripts/Components/Decompose Named Components.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Decompose Named Components
"""Decompose a named component subtree across selected glyphs and masters.

What: Replace occurrences of one source glyph with independent outlines.
Flatten nested components inside each matched occurrence. Keep other direct
components, including those with the same names as nested parts.

How: Preview matching occurrences on all masters by default. Copy each
matched subtree only on Apply, before history starts, through the shared
component writer. Preview reads source-layer counts without native copies.
It composes the native transforms and repairs raw node connection flags,
element names and notes. Keep source glyphs, anchors and metrics unchanged.
Some per-node and per-contour properties are outside the shared copy helper.
Each action is recorded as one Undo step. Component removal uses retained
history objects; removed-component history depends on FontLab (fl#7641).

Why: Glyph > Decompose works on selected components or a whole layer. This
tool adds a source-name filter, all-master preview and recursive subtree
decomposition across several selected glyphs. A refused glyph or layer is
listed as kept; other eligible occurrences can still change.
Decompose Serif Components uses a fixed Serif prefix and removes one level;
this tool uses an exact source name and flattens its complete subtree.

Use: Select composite glyphs. Run this script. Enter the exact source glyph
name. Review the preview, then press Decompose. Use Reload selection after
changing the selection. The panel stays open for another source name.

Benefit: Make a repeated part independent without decomposing its siblings.
Automatic layers, their owners and their dependent bases are kept. Locked
layers, missing bases, cyclic components and unsupported transforms are kept.
Components with an interpolated # location are kept: the copy helper needs
a plain source layer. Reset their locations before decomposing them here.

Credit: Independent behaviour rewrite after Fernando Díaz, Reset Type Studio,
Glyphs-Scripts/Components/Decompose Specific Components (all masters).py.
Repository: https://github.com/Reset-Type-Studio/Glyphs-Scripts .
Source licence: Apache-2.0, declared in README.md; no LICENSE file.
Copyright 2025 Fernando Díaz & Reset Type Studio. No source code was copied.
Unlike the source's second name scan, nested parts are flattened only inside
matched occurrences, so unrelated sibling components stay linked.
"""

from typing import Any

import fly.ap.component_panel as component_panel  # noqa: PLR0402 - native facade
import fly.ap.component_writer as component_writer  # noqa: PLR0402 - native facade
import fly.ap.edit_guards as edit_guards  # noqa: PLR0402 - native facade
import fly.ap.history as history  # noqa: PLR0402 - native facade
import fly.ap.scripting as scripting  # noqa: PLR0402 - native facade
from fly import qt

TITLE = "Decompose Named Components"
KEY = "components_decompose_named"


def flatten_parts(shape: Any, depth: int = 0) -> list[Any]:
    """Copy one subtree into detached outlines, in drawing order.

    Use the public App eject helper at every level. Its native eject applies
    placement, and its copy repair keeps flags and element metadata.
    Bound recursion even when a component cache disagrees with the preview.
    """
    if depth >= component_writer.MAX_DEPTH:
        raise ValueError("Components nest too deeply; component kept.")
    result: list[Any] = []
    for part in component_writer.eject(shape):
        if part.isComponent:
            result.extend(flatten_parts(part, depth + 1))
        else:
            result.append(part)
    return result


def source_contours(package: Any, shape: Any, master: str, depth: int = 0) -> int:
    """Count expected contours from source layers, independently of copy caches."""
    if depth >= component_writer.MAX_DEPTH:
        raise ValueError("Components nest too deeply; component kept.")
    base = package.findName(component_writer.base_of(shape))
    layer_name = str(shape.shapeData.componentLayer) or master
    layer = component_writer.layer_of(base, layer_name) if base is not None else None
    if layer is None:
        raise ValueError(f"Missing base layer {layer_name}.")
    return sum(
        source_contours(package, part, master, depth + 1)
        if part.isComponent
        else len(part.contours)
        for part in layer.shapes
    )


def checked_parts(package: Any, shape: Any, master: str) -> list[Any]:
    """Refuse detached copy loss before history can remove the occurrence."""
    expected = source_contours(package, shape, master)
    parts = flatten_parts(shape)
    if sum(len(part.contours) for part in parts) != expected:
        raise ValueError("Copied contour count differs from the source subtree.")
    return parts


class NamedEditor(component_writer.EjectEditor):
    """Prepare full subtree copies; inherit retained removal and read-back."""

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        """Prepare (original component, flattened parts, placed parts)."""
        steps = []
        for shape_id, parts in edits:
            if parts is None:
                raise ValueError("Prepare component copies on Apply first.")
            shape = layer.shapes[component_writer.shape_index(layer, shape_id)]
            if self.unlock:
                for part in parts:
                    part.contentLocked = False
            steps.append((shape, parts, []))
        return steps


def make_plan(
    package: Any,
    glyphs: list[Any],
    masters: list[str],
    name: str,
    facts: history.AutoFacts,
    *,
    copy: bool = False,
) -> component_writer.Plan:
    """Read counts for preview; copy only on Apply, before history opens."""
    plan = component_writer.Plan()
    refused = history.refusals(facts, [g.name for g in glyphs], "geometry")
    for glyph in glyphs:
        for master in masters:
            label = f"{glyph.name} · {master}"
            layer = component_writer.layer_of(glyph, master)
            candidates = (
                [
                    s
                    for s in component_writer.components(layer)
                    if component_writer.base_of(s) == name
                ]
                if layer is not None
                else []
            )
            if not candidates and (
                layer is not None
                or not any(
                    component_writer.base_of(s) == name
                    for other in glyph.layers
                    for s in component_writer.components(other)
                )
            ):
                continue
            reason = refused.get(glyph.name, "")
            if layer is None:
                reason = "missing master layer"
            elif (
                layer.autoLayer
                or layer.isLocked
                or layer.isMaskLayer
                or layer.isService
            ):
                reason = "automatic, locked or service layer"
            if reason:
                plan.rows.append(
                    (label, component_writer.Change(name, "", f"kept: {reason}"))
                )
                plan.refused.append(label)
                continue
            edits = []
            for shape in candidates:
                reason = component_writer.copy_problem(
                    package, (glyph.name, master), shape, master
                )
                parts = None
                if not reason:
                    try:
                        if copy:
                            parts = checked_parts(package, shape, master)
                        else:
                            source_contours(package, shape, master)
                    except (ValueError, RuntimeError, TimeoutError) as error:
                        reason = str(error)
                row = component_writer.Change(
                    name,
                    "",
                    f"kept: {reason}" if reason else "independent outlines",
                    None if reason else (shape.id, parts),
                )
                plan.rows.append((label, row))
                if not reason:
                    edits.append((shape.id, parts))
            if edits:
                plan.work.append((glyph, layer, edits))
    return plan


class NamedDecomposition(component_panel.panel_type()):
    """Reuse the shared non-modal preview and signal lifecycle."""

    TITLE, KEY, ACTION, DONE = TITLE, KEY, "Decompose", "Decomposed"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Source", "Result")

    def build_controls(self) -> None:
        """One name field and a master scope, initially all masters."""
        self.source_edit = qt.QtGui.QLineEdit()
        self.source_edit.setPlaceholderText("Exact component source name")
        self.master_scope = self.scope_box()
        self.master_scope.setCurrentIndex(1)
        self.form.addWidget(qt.QtGui.QLabel("Component"), 0, 0)
        self.form.addWidget(self.source_edit, 0, 1)
        self.form.addWidget(qt.QtGui.QLabel("Masters"), 1, 0)
        self.form.addWidget(self.master_scope, 1, 1)
        self.watch(self.source_edit.textChanged)
        self.watch(self.master_scope.currentIndexChanged)

    def planner(self) -> str:
        """Return the exact name; refuse text PythonQt cannot round-trip."""
        text = str(self.source_edit.text)
        if any(c in text for c in ("\x00", "\u00a0", "\u2028", "\u2029")):
            raise ValueError(
                "Enter a glyph name without control or non-breaking characters."
            )
        if not text.strip():
            raise ValueError("Enter a component source name.")
        return text.strip()

    def editor(self) -> NamedEditor:
        """Use recursive copies with the shared retained-removal writer."""
        return NamedEditor(unlock=True)

    def refresh(self) -> None:
        """Preview without letting a kept row block other eligible items."""
        self.subtitle.setText(self.intro())
        plan, message = component_writer.Plan(), ""
        try:
            if self.package is not None and self.glyphs:
                plan = make_plan(
                    self.package,
                    self.glyphs,
                    self.chosen_masters(),
                    self.planner(),
                    self.facts,
                )
        except (ValueError, RuntimeError, TimeoutError) as error:
            message = str(error)
        self.fill(plan)
        self.apply_button.setEnabled(bool(plan.work) and not message)
        self.status.setText(message or self.summary(plan))

    def apply(self) -> None:
        """Re-resolve current data; write eligible layers in one history call."""
        message = ""
        try:
            package, glyphs = self.live_glyphs()

            facts = history.scan_auto_facts(package)
            plan = make_plan(
                package,
                glyphs,
                self.chosen_masters(),
                self.planner(),
                facts,
                copy=True,
            )
            result = component_writer.apply_work(plan.work, TITLE, facts, self.editor())
            self.last_result = result
            self.facts = facts

            message = f"Decomposed {result['edits']} occurrences on {result['layers']} layers; review kept rows above."
            message = edit_guards.append_note(message, self.last_result)
        except (ValueError, RuntimeError, TimeoutError) as error:
            message = str(error)
        finally:
            self.refresh()
        self.status.setText(message)


def main() -> Any:
    """Show or raise the reusable panel; report host access failures."""
    try:
        return scripting.show_script_dialog(NamedDecomposition, KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
