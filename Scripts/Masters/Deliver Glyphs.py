# this_file: Scripts/Masters/Deliver Glyphs.py
# SPDX-License-Identifier: Apache-2.0
"""Deliver selected outline glyphs to the font you activate next.

What:
    Keep a source font and glyph selection in a non-modal panel. Activate a
    destination font, preview master pairing, then Deliver. Repeat for other
    open fonts. Existing glyphs are kept unless Replace is ticked.
How:
    Master names match without case or surrounding spaces. Other destination
    masters use the source master captured on launch; every fallback is listed.
    glyph_creation runs FontLab's Add Glyph command for each new glyph.
    New glyph Unicode assignments go only through that command. Existing
    Unicode lists stay unchanged. Conflicts with other destination glyphs are
    kept rows. Outlines, anchors, advances and metrics expressions then travel
    in one geometry action through outline_writer and anchor_writer.
Why:
    Native copy and paste also transfers components and hints; this tool adds
    retained source selection, master-name pairing and visible fallbacks across
    repeated destinations. It writes only to the current font. Component links
    and hints are not carried to another font, so those glyphs are kept.
    Decompose components in the source if outline-only delivery is appropriate.
    Existing target components, hints and shared shape data also keep the
    glyph. Category, subcategory, script and export status from Postino are
    not transferred; existing destination values stay. Units per em must match.
    contour_copy restores node names and raw flags with selection cleared.
    Element names, notes and transforms are copied explicitly. Named contours
    and nodes with an explicit corner_smooth value are kept. Other node and
    contour properties are not detected and not copied (fl#8569). Nothing is saved.
Use:
    Select glyphs in the source Font window and run. Activate a destination Font
    window with its Glyph editors closed. Click Preview. Review every row and
    any 'may rebuild auto' warning. Tick consent if appropriate, then Deliver.
    Each new glyph is recorded as its own Undo step, and the outlines as one
    more Undo step. Existing glyph notes and other metadata stay as they are.
Benefit:
    Send a consistent set of outline glyphs to several working fonts without
    leaving empty masters or silently dropping components and hints.
Credit:
    Giuseppe Salerno / Resistenza Type, Postino.py,
    https://github.com/rsztype/Scripts, Apache-2.0.
    Independent behaviour-only rewrite. No source code was copied.
"""

import math
from time import monotonic
from typing import Any

TITLE, KEY = "Deliver Glyphs", "masters_deliver_glyphs"
METRICS = ("advanceWidth", "metricsLeft", "metricsRight", "metricsWidth")


def master_pairs(
    source: list[str], target: list[str], fallback: str
) -> list[tuple[str, str, bool]]:
    """Pair each target with a source, reporting fallback and ambiguity."""
    normalized = [name.strip().casefold() for name in source]
    if (
        not source
        or not target
        or fallback not in source
        or len(normalized) != len(set(normalized))
    ):
        raise ValueError(
            "Source masters must be unique; both fonts need masters and a valid fallback."
        )
    mapping = dict(zip(normalized, source, strict=True))
    return [
        (
            name,
            mapping.get(name.strip().casefold(), fallback),
            name.strip().casefold() not in mapping,
        )
        for name in target
    ]


def usable_layer(layer: Any) -> None:
    """Refuse content that this cross-font writer cannot retain faithfully."""
    if layer is None or layer.isNull:
        raise ValueError("A master layer is missing.")
    if layer.autoLayer or layer.isLocked or layer.isMaskLayer or layer.isService:
        raise ValueError(
            "Automatic, locked, mask and service layers cannot be delivered."
        )
    if layer.hasHints or layer.hasTTH:
        raise ValueError(
            "Hinted layers cannot be delivered; no hint writer is available."
        )
    if any(shape.isComponent for shape in layer.shapes):
        raise ValueError(
            "Components cannot be delivered; use plain outlines or FontLab's native Paste."
        )
    for shape in layer.shapes:
        if int(shape.shapeData.referenceCount) > 1:
            raise ValueError("shared shape data")
        for contour in shape.contours:
            if contour.name:
                raise ValueError("contour name is not copied")
            for node in contour.nodes():
                if node.getProperty("corner_smooth") is not None:
                    raise ValueError("explicit corner_smooth is not copied")
    if not math.isfinite(float(layer.advanceWidth)):
        raise ValueError("Advance width must be finite.")


def copy_shapes(layer: Any) -> list[Any]:
    """Copy shapes; restore node names and raw flags through contour_copy only."""
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402

    output = []
    for shape in layer.shapes:
        cloned = shape.clone()
        cloned.name = shape.name
        cloned.shapeData.name = shape.shapeData.name
        cloned.shapeData.note = shape.shapeData.note
        cloned.transform = shape.transform
        cloned.active = cloned.selected = False
        for before, after in zip(shape.contours, cloned.contours, strict=True):
            contour_copy.repair_nodes(before, after)
        output.append(cloned)
    return output


def glyph_codes(package: Any) -> dict[str, list[int]]:
    """Read the FontGate Unicode lists of a registered package; no flGlyph.fgGlyph getter."""
    return {str(glyph.name): list(glyph.unicodes) for glyph in package.fgPackage}


def delivery_plan(
    source: Any, target: Any, names: list[str], fallback: str, replace: bool
) -> list[dict[str, Any]]:
    """List each selected glyph as deliverable or kept; make no font changes."""
    import fly.ap.anchor_writer as anchors
    import fly.ap.history as history  # noqa: PLR0402

    if int(source.fgId) == int(target.fgId):
        raise ValueError("Activate a different destination font.")
    if float(source.info.unitsPerEm) != float(target.info.unitsPerEm):
        raise ValueError(
            "Source and destination units per em differ; scale deliberately before delivery."
        )
    if not names:
        raise ValueError("The source selection is empty; reopen the panel.")
    pairs = master_pairs(list(source.masters), list(target.masters), fallback)
    facts = history.scan_auto_facts(target)
    source_codes, target_codes = glyph_codes(source), glyph_codes(target)
    owners: dict[int, set[str]] = {}
    for name, codes in target_codes.items():
        for code in codes:
            owners.setdefault(code, set()).add(name)
    jobs = []
    for name in dict.fromkeys(names):
        job: dict[str, Any] = {
            "name": name,
            "existing": False,
            "layers": [],
            "unicodes": [],
            "metrics": {},
            "note": "",
            "unicode_changes": False,
        }
        try:
            glyph = source.findName(name)
            if glyph is None or glyph.isNull or name not in source_codes:
                raise ValueError("source glyph is missing")
            existing = target.findName(name)
            job["existing"] = existing is not None and not existing.isNull
            if job["existing"] and not replace:
                raise ValueError("already exists; Replace is off")
            reason = history.refusal(facts, name, "geometry")
            if reason:
                raise ValueError(reason)
            conflicts = [
                code for code in source_codes[name] if owners.get(code, set()) - {name}
            ]
            if conflicts:
                raise ValueError(
                    "Unicode already held by another destination glyph: "
                    + ", ".join(f"U+{c:04X}" for c in conflicts)
                )
            layers = []
            for destination, origin, guessed in pairs:
                layer = glyph.findLayer(origin)
                usable_layer(layer)
                if anchors.duplicated(layer, [str(pin.name) for pin in layer.anchors]):
                    raise ValueError("Duplicate anchor names in source")
                points = anchors.anchor_points(layer)
                if any(
                    not all(math.isfinite(v) for v in point)
                    for point in points.values()
                ):
                    raise ValueError("Anchor positions must be finite")
                if job["existing"]:
                    old = existing.findLayer(destination)
                    usable_layer(old)
                    if anchors.duplicated(old, [str(pin.name) for pin in old.anchors]):
                        raise ValueError("Duplicate anchor names in destination")
                    before = anchors.anchor_points(old)
                    if any(
                        n in before and point == (0.0, 0.0) and before[n] != point
                        for n, point in points.items()
                    ):
                        raise ValueError("an existing anchor would move to the origin")
                layers.append((destination, origin, guessed, layer, points))
            job.update(
                layers=layers,
                unicodes=target_codes[name] if job["existing"] else source_codes[name],
                metrics={key: getattr(glyph, key) for key in METRICS[1:]},
                unicode_changes=bool(source_codes[name]) and not job["existing"],
            )
            if not job["existing"]:
                for code in source_codes[name]:
                    owners.setdefault(code, set()).add(name)
        except ValueError as error:
            job["note"] = str(error)
        jobs.append(job)
    return jobs


def rebuild_rows(target: Any, jobs: list[dict[str, Any]]) -> dict[str, tuple[str, ...]]:
    """Use the shared suffix-scoped auto-candidate scan for new glyphs only."""
    import fly.ap.glyph_creation as glyph_creation  # noqa: PLR0402
    import fly.ap.history as history  # noqa: PLR0402

    return glyph_creation.auto_candidates(
        target,
        history.scan_auto_facts(target),
        [j["name"] for j in jobs if not j["note"] and not j["existing"]],
    )


def deliver(target: Any, jobs: list[dict[str, Any]], consent: bool) -> dict[str, Any]:
    """Add through glyph_creation; fill all eligible master layers in one action."""
    import fly.ap.anchor_writer as anchors
    import fly.ap.edit_guards as guards
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402
    import fly.ap.glyph_creation as glyph_creation  # noqa: PLR0402
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.outline_writer as outlines
    import fly.ap.scripting as scripting  # noqa: PLR0402

    current = scripting.current_package()
    if current is None or int(current.fgId) != int(target.fgId):
        raise ValueError("Activate the destination Font window first.")
    # This guard explicitly takes an object id, not a fontpr/workspace font id.
    guards.require_selection_window(int(current.id))
    guards.require_no_editors()
    guards.require_settled()
    ready = [j for j in jobs if not j["note"]]
    if not ready:
        return {"created": 0, "glyphs": 0, "layers": 0, "unicode_changes": []}
    # All source shape copies exist before the first Add Glyph command.
    prepared = [
        (
            job,
            [
                (
                    master,
                    copy_shapes(layer),
                    dict(points),
                    {key: getattr(layer, key) for key in METRICS},
                )
                for master, _, _, layer, points in job["layers"]
            ],
        )
        for job in ready
    ]
    facts = history.scan_auto_facts(target)
    specs = [
        glyph_creation.NewGlyph(
            job["name"],
            tuple(
                (master, glyph_copies.half_up(metrics["advanceWidth"]))
                for master, _, _, metrics in layers
            ),
            tuple(job["unicodes"]),
        )
        for job, layers in prepared
        if not job["existing"]
    ]
    auto_before = glyph_creation.auto_signatures(target, facts)
    made = glyph_creation.create_glyphs(
        target, specs, TITLE, facts, allow_rebuild=consent
    )
    try:
        if made.mismatches:
            raise RuntimeError("; ".join(made.mismatches))
        work = []
        for job, layers in prepared:
            glyph = target.findName(job["name"])
            if glyph is None or glyph.isNull:
                raise RuntimeError(f"FontLab did not keep {job['name']}.")
            for master, shapes, points, metrics in layers:
                layer = glyph.findLayer(master)
                usable_layer(layer)
                before = anchors.anchor_points(layer)
                edits = [("remove", n, None) for n in before if n not in points] + [
                    ("set", n, point)
                    for n, point in points.items()
                    if before.get(n) != point
                ]
                work.append((glyph, layer, [(job, shapes, edits, metrics)]))

        class Delivery(outlines.Editor):
            """Write outlines and anchors only; Unicode is never assigned here."""

            def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
                job, shapes, pins, metrics = edits[0]
                return [
                    (
                        job,
                        list(layer.shapes),
                        shapes,
                        anchors.prepare(layer, pins),
                        metrics,
                    )
                ]

            def write(self, layer: Any, steps: list[Any]) -> None:
                for job, removed, shapes, pins, metrics in steps:
                    for shape in removed:
                        layer.removeShape(shape)
                    for shape in shapes:
                        layer.addShape(shape)
                    anchors.write(layer, pins)
                    for key, value in metrics.items():
                        setattr(layer, key, value)
                    glyph = target.findName(job["name"])
                    for key, value in job["metrics"].items():
                        setattr(glyph, key, value)

            def check(self, prepared: list[Any]) -> list[str]:
                errors = []
                codes = glyph_codes(target)
                for layer, steps in prepared:
                    for job, removed, shapes, _, metrics in steps:
                        ids = {shape.id for shape in layer.shapes}
                        if any(shape.id not in ids for shape in shapes) or any(
                            shape.id in ids for shape in removed
                        ):
                            errors.append(f"{job['name']}: shapes")
                        if (
                            any(
                                getattr(layer, key) != value
                                for key, value in metrics.items()
                            )
                            or codes.get(job["name"]) != job["unicodes"]
                        ):
                            errors.append(f"{job['name']}: metrics or Unicode")
                        points = next(
                            p
                            for master, _, _, _, p in job["layers"]
                            if master == str(layer.name)
                        )
                        if anchors.anchor_points(layer) != points:
                            errors.append(f"{job['name']}: anchors")
                return errors + glyph_creation.auto_changes(target, auto_before)

        result = outlines.apply_work(
            work,
            TITLE,
            history.scan_auto_facts(target),
            Delivery(),
            allow_bases=consent,
        )
        return {
            "created": len(made.glyphs),
            "glyphs": len(ready),
            "layers": result["layers"],
            "unicode_changes": [j["name"] for j in ready if j["unicode_changes"]],
        }
    except (ValueError, RuntimeError, TimeoutError) as error:
        if "use Edit > Undo" not in str(error):
            raise RuntimeError(
                f"{error} Native changes may remain; use Edit > Undo"
            ) from error
        raise


def preview_rows(
    jobs: list[dict[str, Any]], candidates: dict[str, tuple[str, ...]] | None = None
) -> list[tuple[str, str, str, str]]:
    """Keep a visible row for every selected glyph, including each refusal."""
    import fly.ap.glyph_creation as glyph_creation  # noqa: PLR0402

    rows = []
    for job in jobs:
        if job["note"]:
            rows.append((job["name"], "", "", "kept: " + job["note"]))
            continue
        for master, source, guessed, _, _ in job["layers"]:
            action = (
                "replace; Unicode kept"
                if job["existing"]
                else "add; Unicode assigned on creation"
                if job["unicode_changes"]
                else "add; no Unicode"
            )
            if (candidates or {}).get(job["name"]):
                action += "; " + glyph_creation.rebuild_note(candidates[job["name"]])
            rows.append(
                (
                    job["name"],
                    master,
                    source,
                    action + ("; fallback" if guessed else ""),
                )
            )
    return rows


def panel_type() -> type:
    """Build a source-retaining panel; never switch the active font in code."""
    import fly.ap.glyph_creation as glyph_creation  # noqa: PLR0402
    import fly.ap.layer_selection as selection
    import fly.ap.scripting as scripting  # noqa: PLR0402 - lazy Fly module alias
    from fly import fl, qt

    gui = qt.QtGui

    class DeliveryPanel(scripting.names_dialog_type()):
        """Let the user activate each destination before explicit delivery."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent, TITLE, KEY)
            self.source_id: int | None = None
            self.source_names: list[str] = []
            self.fallback = ""
            self.replace_box = gui.QCheckBox("Replace existing glyphs")
            self.consent_box = gui.QCheckBox(glyph_creation.REBUILD_LABEL)
            self.root.addWidget(self.replace_box)
            self.root.addWidget(self.consent_box)
            self.root.addWidget(gui.QLabel(glyph_creation.UNDO_TEXT))
            self.table = self.make_table(
                ["Glyph", "Destination master", "Source master", "Action"]
            )
            self.root.addWidget(self.table)
            self.status = gui.QLabel("")
            self.status.setWordWrap(True)
            self.root.addWidget(self.status)
            footer = gui.QHBoxLayout()
            self.preview_button, self.apply_button, self.close_button = [
                gui.QPushButton(t) for t in ("Preview", "Deliver", "Close")
            ]
            for button in (self.preview_button, self.close_button, self.apply_button):
                footer.addWidget(button)
            self.root.addLayout(footer)
            self._connect(
                self.preview_button.clicked, lambda *a: self.preview_delivery()
            )
            self._connect(self.apply_button.clicked, lambda *a: self.write_delivery())
            self._connect(self.close_button.clicked, lambda *a: self.close())
            self._connect(self.replace_box.toggled, lambda *a: self.preview_delivery())
            self.apply_button.setEnabled(False)
            self.preview_token: tuple[Any, ...] | None = None
            try:
                package = scripting.current_package()
                if package is None:
                    raise ValueError("Select glyphs in the source font first.")
                capture = selection.capture(monotonic() + 2.0)
                self.source_names = list(
                    dict.fromkeys(o.glyph_name for o in capture.occurrences)
                )
                if not self.source_names:
                    raise ValueError("Select source glyphs, then reopen this panel.")
                self.source_id, self.fallback = int(package.fgId), str(package.master)
                self.subtitle.setText(
                    f"{len(self.source_names)} source glyphs · activate a destination Font window, then Preview"
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

        def fresh_plan(self) -> tuple[Any, list[dict[str, Any]]]:
            """Require both fonts to remain open and a distinct current target."""
            if self.source_id is None:
                raise ValueError("Reopen this tool with a source selection.")
            source = fl.flWorkspace.instance().findPackageId(self.source_id)
            target = scripting.current_package()
            if source is None or source.isNull or target is None:
                raise ValueError("The source or destination font is closed.")
            return target, delivery_plan(
                source,
                target,
                self.source_names,
                self.fallback,
                self.replace_box.isChecked(),
            )

        def preview_delivery(self) -> None:
            """Display every master mapping, plus any automatic rebuild warning."""
            self.apply_button.setEnabled(False)
            self.preview_token = None
            self.table.setRowCount(0)
            self.consent_box.setChecked(False)
            try:
                target, jobs = self.fresh_plan()
                candidates = rebuild_rows(target, jobs)
                rows = preview_rows(jobs, candidates)
                self.table.setRowCount(len(rows))
                for row, cells in enumerate(rows):
                    for column, text in enumerate(cells):
                        self.table.setItem(row, column, gui.QTableWidgetItem(text))
                warnings = [
                    f"{name}: {glyph_creation.rebuild_note(owners)}"
                    for name, owners in candidates.items()
                ]
                self.status.setText(
                    "\n".join(
                        [
                            f"{sum(not j['note'] for j in jobs)} glyphs to deliver · {sum(bool(j['note']) for j in jobs)} kept",
                            *warnings[:8],
                            *(
                                ["More rebuild candidates are listed in the table."]
                                if len(warnings) > 8
                                else []
                            ),
                        ]
                    )
                )
                self.preview_token = (int(target.fgId), tuple(rows), tuple(warnings))
                self.apply_button.setEnabled(any(not j["note"] for j in jobs))
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

        def write_delivery(self) -> None:
            """Check target and mapping against preview, then write current font."""
            try:
                target, jobs = self.fresh_plan()
                candidates = rebuild_rows(target, jobs)
                rows = preview_rows(jobs, candidates)
                warnings = [
                    f"{name}: {glyph_creation.rebuild_note(owners)}"
                    for name, owners in candidates.items()
                ]
                if self.preview_token != (
                    int(target.fgId),
                    tuple(rows),
                    tuple(warnings),
                ):
                    raise ValueError("The delivery changed; click Preview again.")
                result = deliver(target, jobs, self.consent_box.isChecked())
                self.preview_delivery()
                self.status.setText(
                    f"Delivered {result['glyphs']} glyphs in {result['layers']} layers; {result['created']} added."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.apply_button.setEnabled(False)
                self.status.setText(str(error))

    return DeliveryPanel


def main() -> Any:
    """Open the panel on the source selection; each target stays user-selected."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - lazy Fly module alias

    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
