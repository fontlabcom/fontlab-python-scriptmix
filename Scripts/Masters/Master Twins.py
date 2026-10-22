# this_file: Scripts/Masters/Master Twins.py
# SPDX-License-Identifier: Apache-2.0
"""Copy selected kinds of master-layer content across the current font.

What:
    Copy contours, components, anchors and metrics independently between two
    masters. Choose selected glyphs or all glyphs. An empty source clears the
    chosen content in the target. Guides, masks and glyph identity stay put.
How:
    A non-modal panel previews layer pairs. Copy plans again from the live
    font. Shape copies and anchor_writer steps are prepared before history.
    contour_copy restores node names and raw node flags, with selection
    cleared.
    Element names, notes and transforms are copied explicitly. Named contours
    and nodes with an explicit corner_smooth value are kept. Other node and
    contour properties are not detected and not copied. outline_writer records
    the complete action as one Undo step.
Why:
    Component-only copying and whole-font scope complement Copy Layer Between
    Masters. Automatic, locked and shared-data glyphs are kept and listed;
    other glyphs still copy. PostScript or TrueType hints keep a glyph only
    when contours are chosen. transferTTH is not used. Contour copies can
    lose extra node properties (fl#8569).
Use:
    Open a font with at least two masters. Choose From, To and the content
    switches. Check the preview and click Copy. Refresh reads the selection.
    Check master compatibility after copying contours or components.
Benefit:
    Seed a new master, including its components, without replacing other
    kinds of content. Refusals appear before any font write.
Credit:
    Giuseppe Salerno / Resistenza Type, MasterTwins.py,
    https://github.com/rsztype/Scripts, Apache-2.0.
    Independent behaviour-only rewrite. No source code was copied.
"""

import math
from dataclasses import dataclass
from time import monotonic
from typing import Any

TITLE, KEY = "Master Twins", "masters_master_twins"
METRICS = ("advanceWidth", "metricsLeft", "metricsRight", "metricsWidth")


@dataclass(frozen=True)
class Content:
    """Independent switches for the content kinds supported by this tool."""

    contours: bool = True
    components: bool = True
    anchors: bool = True
    metrics: bool = True


def shape_copy(shape: Any, master: str) -> Any:
    """Copy names, note and transform; shared helper restores node names/flags."""
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402

    cloned = shape.clone()
    cloned.name = shape.name
    cloned.shapeData.name = shape.shapeData.name
    cloned.shapeData.note = shape.shapeData.note
    cloned.transform = shape.transform
    cloned.active = cloned.selected = False
    if shape.isComponent:
        cloned.shapeData.componentLayer = master
    else:
        for before, after in zip(shape.contours, cloned.contours, strict=True):
            contour_copy.repair_nodes(before, after)
    return cloned


def shape_problem(shape: Any) -> str:
    """Refuse shared data and known contour/node fields outside the copy contract."""
    if int(shape.shapeData.referenceCount) > 1:
        return "shared shape data"
    if not shape.isComponent:
        for contour in shape.contours:
            if contour.name:
                return "contour name is not copied"
            for node in contour.nodes():
                if node.getProperty("corner_smooth") is not None:
                    return "explicit corner_smooth is not copied"
    return ""


def anchor_edits(source: Any, target: Any) -> list[tuple[str, str, Any]]:
    """Plan a full anchor replacement through the public anchor writer."""
    import fly.ap.anchor_writer as anchors

    for layer in (source, target):
        if anchors.duplicated(layer, [str(pin.name) for pin in layer.anchors]):
            raise ValueError("Duplicate anchor names; make the names unique first.")
    before, after = anchors.anchor_points(target), anchors.anchor_points(source)
    if any(not all(math.isfinite(v) for v in point) for point in after.values()):
        raise ValueError("Anchor positions must be finite.")
    for name, point in after.items():
        if name in before and point == (0.0, 0.0) and before[name] != point:
            raise ValueError(
                f"Anchor {name} would move to the origin; choose another layer."
            )
    return [("remove", n, None) for n in before if n not in after] + [
        ("set", n, point) for n, point in after.items() if before.get(n) != point
    ]


def layer_problem(layer: Any, outlines: bool = True) -> str:
    """Explain why a body layer is not a supported copy source or target."""
    if layer is None or layer.isNull:
        return "missing layer"
    if layer.autoLayer or layer.isMaskLayer or layer.isService:
        return "automatic, mask or service layer"
    if layer.isLocked:
        return "locked layer"
    if outlines and (layer.hasHints or layer.hasTTH):
        return "PostScript/TrueType hints; contour replacement kept"
    if not math.isfinite(float(layer.advanceWidth)):
        return "nonfinite advance width"
    return ""


def copy_work(
    package: Any,
    names: list[str],
    source: str,
    target: str,
    content: Content,
    facts: Any,
    kept: list[tuple[str, str]] | None = None,
) -> list[Any]:
    """Check every pair before history. Return (glyph, layer, [source/options])."""
    import fly.ap.history as history  # noqa: PLR0402 - lazy Fly module alias

    if (
        source == target
        or source not in package.masters
        or target not in package.masters
    ):
        raise ValueError("Choose two different masters.")
    if not any(
        (content.contours, content.components, content.anchors, content.metrics)
    ):
        raise ValueError("Choose at least one content kind.")
    if not names:
        raise ValueError("Select glyphs or choose All glyphs.")
    work = []
    notes = kept if kept is not None else []
    for name in dict.fromkeys(names):
        try:
            glyph = package.findName(name)
            if glyph is None or glyph.isNull:
                raise ValueError("missing glyph")
            old, new = glyph.findLayer(source), glyph.findLayer(target)
            reason = (
                history.refusal(facts, name, "geometry")
                or layer_problem(old, content.contours)
                or layer_problem(new, content.contours)
            )
            if reason:
                raise ValueError(reason)
            if content.anchors:
                anchor_edits(old, new)
            for layer in (old, new):
                for shape in layer.shapes:
                    chosen = (
                        content.components if shape.isComponent else content.contours
                    )
                    if chosen and (problem := shape_problem(shape)):
                        raise ValueError(problem)
            if content.components:
                for shape in old.shapes:
                    if not shape.isComponent:
                        continue
                    base = package.findName(str(shape.shapeData.componentGlyph))
                    if (
                        base is None
                        or base.isNull
                        or base.name == name
                        or layer_problem(base.findLayer(target), False)
                    ):
                        raise ValueError(
                            "component base absent, self-referencing or not editable"
                        )
            work.append((glyph, new, [(old, content)]))
        except ValueError as error:
            notes.append((name, str(error)))
    if content.components:
        # Dropping one replacement can expose a cycle through the kept layer.
        while work:
            bad = []
            for job in work:
                try:
                    check_component_graph(package, work, target, [str(job[0].name)])
                except ValueError as error:
                    notes.append((str(job[0].name), str(error)))
                    bad.append(job)
            if not bad:
                break
            work = [job for job in work if job not in bad]
    return work


def check_component_graph(
    package: Any, work: list[Any], master: str, roots: list[str]
) -> None:
    """Refuse any component cycle reachable after the planned replacement."""
    replacements = {str(glyph.name): edits[0][0] for glyph, _, edits in work}
    done: set[str] = set()
    deadline = monotonic() + 2.0
    for start in roots:
        stack: list[tuple[str, bool]] = [(start, False)]
        visiting: set[str] = set()
        while stack:
            if monotonic() > deadline:
                raise TimeoutError("Component check timed out; no layers were changed.")
            name, leaving = stack.pop()
            if leaving:
                visiting.remove(name)
                done.add(name)
                continue
            if name in visiting:
                raise ValueError(f"Component cycle through {name} in {master}.")
            if name in done:
                continue
            glyph = package.findName(name)
            layer = (
                replacements.get(name)
                if name in replacements
                else glyph.findLayer(master)
                if glyph is not None
                else None
            )
            if layer is None or layer.isNull or layer.autoLayer:
                raise ValueError(
                    f"Component base {name} is missing or automatic in {master}."
                )
            visiting.add(name)
            stack.append((name, True))
            stack.extend(
                (str(s.shapeData.componentGlyph), False)
                for s in layer.shapes
                if s.isComponent
            )


def editor_type() -> type:
    """Use the shared geometry and anchor kernels for one history action."""
    import fly.ap.anchor_writer as anchors
    import fly.ap.history as history  # noqa: PLR0402 - lazy Fly module alias
    import fly.ap.outline_writer as outlines

    class CopyContent(outlines.Editor):
        """Stage copies before history and keep removed component history alive."""

        def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
            source, options = edits[0]

            def chosen(shape: Any) -> bool:
                return options.components if shape.isComponent else options.contours

            removed = [shape for shape in layer.shapes if chosen(shape)]
            added = [
                shape_copy(shape, str(layer.name))
                for shape in source.shapes
                if chosen(shape)
            ]
            pins = (
                anchors.prepare(layer, anchor_edits(source, layer))
                if options.anchors
                else []
            )
            metrics = (
                {key: getattr(source, key) for key in METRICS}
                if options.metrics
                else {}
            )
            return [(removed, added, pins, metrics)]

        def retain(self, steps: list[Any]) -> list[Any]:
            return [
                item
                for removed, _, _, _ in steps
                for shape in removed
                for item in history.component_history(shape)
            ]

        def write(self, layer: Any, steps: list[Any]) -> None:
            for removed, added, pins, metrics in steps:
                for shape in removed:
                    layer.removeShape(shape)
                for shape in added:
                    layer.addShape(shape)
                anchors.write(layer, pins)
                for key, value in metrics.items():
                    setattr(layer, key, value)

        def check(self, prepared: list[Any]) -> list[str]:
            errors = []
            for layer, steps in prepared:
                for removed, added, pins, metrics in steps:
                    stored = {shape.id for shape in layer.shapes}
                    if any(s.id in stored for s in removed) or any(
                        s.id not in stored for s in added
                    ):
                        errors.append(f"{layer.name}: shape replacement")
                    if any(getattr(layer, k) != v for k, v in metrics.items()):
                        errors.append(f"{layer.name}: metrics")
                    points = anchors.anchor_points(layer)
                    for action, pin, value in pins:
                        if action == "remove" and str(pin.name) in points:
                            errors.append(f"{layer.name}: anchor removal")
                        if action in ("move", "add"):
                            name = str(pin.name if action == "move" else value.name)
                            point = value if action == "move" else value.point
                            if points.get(name) != (float(point.x()), float(point.y())):
                                errors.append(f"{layer.name}: anchor {name}")
            return errors

    return CopyContent


def panel_type() -> type:
    """Build a compact modeless panel with explicit content switches."""
    import fly.ap.glyph_catalog as catalog
    import fly.ap.history as history  # noqa: PLR0402 - lazy Fly module alias
    import fly.ap.layer_selection as selection
    import fly.ap.outline_writer as outlines
    import fly.ap.scripting as scripting  # noqa: PLR0402 - lazy Fly module alias
    from fly import qt

    gui = qt.QtGui

    class MasterCopyPanel(scripting.names_dialog_type()):
        """Own one source-bound font, a preview and a Copy action."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent, TITLE, KEY)
            self.package_id: int | None = None
            self.names: list[str] = []
            self.all_names: list[str] = []
            self.auto_facts: Any = None
            self.kept_rows: list[tuple[str, str]] = []
            grid = gui.QGridLayout()
            self.from_master, self.to_master = gui.QComboBox(), gui.QComboBox()
            for row, (label, control) in enumerate(
                (("From", self.from_master), ("To", self.to_master))
            ):
                grid.addWidget(gui.QLabel(label), row, 0)
                grid.addWidget(control, row, 1)
            self.all_glyphs = gui.QCheckBox("All glyphs")
            grid.addWidget(self.all_glyphs, 2, 1)
            self.switches = [
                gui.QCheckBox(t)
                for t in ("Contours", "Components", "Anchors", "Metrics")
            ]
            for row, switch in enumerate(self.switches, 3):
                switch.setChecked(True)
                grid.addWidget(switch, row, 1)
            self.root.addLayout(grid)
            self.table = self.make_table(["Glyph", "From", "To", "Action"])
            self.root.addWidget(self.table)
            self.status = gui.QLabel("")
            self.status.setWordWrap(True)
            self.root.addWidget(self.status)
            footer = gui.QHBoxLayout()
            self.refresh_button, self.apply_button, self.close_button = [
                gui.QPushButton(t) for t in ("Refresh", "Copy", "Close")
            ]
            for button in (self.refresh_button, self.close_button, self.apply_button):
                footer.addWidget(button)
            self.root.addLayout(footer)
            for button, slot in (
                (self.refresh_button, self.read_font),
                (self.apply_button, self.write_content),
            ):
                self._connect(button.clicked, lambda *a, callback=slot: callback())
            self._connect(self.close_button.clicked, lambda *a: self.close())
            for signal in (
                self.from_master.currentIndexChanged,
                self.to_master.currentIndexChanged,
                self.all_glyphs.toggled,
                *(switch.toggled for switch in self.switches),
            ):
                self._connect(signal, lambda *a: self.preview_pairs())
            self.read_font()

        def read_font(self) -> None:
            """Bind to the current font; retain master choices when possible."""
            try:
                package = scripting.current_package()
                if package is None or len(package.masters) < 2:
                    raise ValueError("Open a font with at least two masters.")
                self.package_id = int(package.fgId)
                capture = selection.capture(monotonic() + 2.0)
                self.names = list(
                    dict.fromkeys(o.glyph_name for o in capture.occurrences)
                )
                self.all_names = [row[0] for row in catalog.capture().rows]
                self.auto_facts = history.scan_auto_facts(package)
                for box in (self.from_master, self.to_master):
                    box.blockSignals(True)
                    previous = str(box.currentText)
                    box.clear()
                    for master in package.masters:
                        box.addItem(str(master))
                    if previous in package.masters:
                        box.setCurrentIndex(list(package.masters).index(previous))
                    box.blockSignals(False)
                if self.from_master.currentText == self.to_master.currentText:
                    self.to_master.setCurrentIndex(
                        (self.from_master.currentIndex + 1) % len(package.masters)
                    )
                self.preview_pairs()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.package_id = None
                self.apply_button.setEnabled(False)
                self.status.setText(str(error))

        def build_work(self, fresh: bool = False) -> tuple[list[Any], Any]:
            """Build fresh work or refuse a changed font and stale masters."""
            package = scripting.current_package()
            if package is None or int(package.fgId) != self.package_id:
                raise ValueError("The font changed; press Refresh.")
            if fresh:
                self.all_names = [row[0] for row in catalog.capture().rows]
                self.auto_facts = history.scan_auto_facts(package)
            names = self.all_names if self.all_glyphs.isChecked() else self.names
            facts = self.auto_facts
            self.kept_rows = []
            work = copy_work(
                package,
                names,
                str(self.from_master.currentText),
                str(self.to_master.currentText),
                Content(*(switch.isChecked() for switch in self.switches)),
                facts,
                self.kept_rows,
            )
            return work, facts

        def preview_pairs(self) -> None:
            """Show all affected names; a refusal disables Copy."""
            self.apply_button.setEnabled(False)
            self.table.setRowCount(0)
            try:
                work, _ = self.build_work()
                rows = [
                    (str(g.name), str(edits[0][0].name), str(layer.name), "copy")
                    for g, layer, edits in work
                ]
                rows += [
                    (name, "", "", f"kept: {reason}") for name, reason in self.kept_rows
                ]
                self.table.setRowCount(len(rows))
                for row, cells in enumerate(rows):
                    for column, text in enumerate(cells):
                        self.table.setItem(row, column, gui.QTableWidgetItem(text))
                self.status.setText(
                    f"{len(work)} layers to copy · {len(self.kept_rows)} kept. Check master compatibility afterwards."
                )
                self.apply_button.setEnabled(bool(work))
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

        def write_content(self) -> None:
            """Plan again, prepare detached copies, then make one history action."""
            import fly.ap.edit_guards as result_guards
            try:
                work, facts = self.build_work(fresh=True)
                result = outlines.apply_work(work, TITLE, facts, editor_type()())
                self.preview_pairs()
                self.last_result = result
                self.status.setText(result_guards.append_note(f"Copied {result['layers']} layers.", result))
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(
                    str(error)
                    + (
                        " Native changes may remain; use Edit > Undo"
                        if isinstance(error, RuntimeError)
                        and "use Edit > Undo" not in str(error)
                        else ""
                    )
                )

    return MasterCopyPanel


def main() -> Any:
    """Open one owned Master Twins panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - lazy Fly module alias

    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
