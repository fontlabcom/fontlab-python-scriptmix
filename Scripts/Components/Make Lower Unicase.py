# this_file: Scripts/Components/Make Lower Unicase.py
# SPDX-License-Identifier: Apache-2.0
"""Make uppercase cells show lowercase components on every master.

What: Map encoded lowercase letters to their single-character uppercase cells.
Use existing uppercase glyphs only; list missing targets and later mappings as
kept. Existing uppercase contours, components and anchors are replaced; image
and sticker shapes stay. Target widths and kerning class memberships
follow the lowercase on each master. Multi-character uppercase mappings stay.
How: Use Unicode case data and current-font glyph names. Make plain components
from a plain component already in this font, with an explicit master layer.
Why: A plain component remains editable without automatic-layer rebuilds.
Use: Preview all uppercase/lowercase pairs, then Apply and confirm the font and
counts. Canonical round-trip lowercase comes first, then Unicode and glyph-name
order. Later sources for one target stay; their rows say kept. Existing Unicode
assignments stay. Replacing existing outlines is recorded as one Undo step.
Benefit: Build a lowercase unicase design consistently across every master.
Automatic targets and bases of automatic composites are refused. Circular
references are kept. Existing targets without a safe plain component to copy
are listed as kept; other eligible targets can still change. This tool creates
no capital glyph whose name is missing.

Independent behaviour rewrite after Pedro Arilla, based on Georg Seifert's
Make Unicase Font idea, glyphs-scripts/Components/Make lower-unicase font.py,
Apache-2.0. Repository: https://github.com/pedroarilla/glyphs-scripts .
No source code copied.
"""

from typing import Any

import fly.ap.component_creation as component_creation  # noqa: PLR0402
import fly.ap.component_writer as writer
import fly.ap.edit_guards as edit_guards  # noqa: PLR0402
import fly.ap.glyph_catalog as catalog
import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402
import fly.ap.glyph_creation as glyph_creation  # noqa: PLR0402
import fly.ap.history as history  # noqa: PLR0402
import fly.ap.scripting as scripting  # noqa: PLR0402
import fly.ap.selection_panel as selection_panel  # noqa: PLR0402

Pair = tuple[str, str]  # target, base


TITLE = "Make Lower Unicase"
KEY = "components_lower_unicase"


def survey(package: Any) -> list[glyph_copies.Row]:
    """Choose canonical round-trip sources first, then Unicode and glyph-name order.

    For each existing uppercase glyph, the first source wins. Later candidates
    are kept rows. Missing uppercase glyphs and multi-character case mappings
    are kept too; this tool never guesses a capital glyph name.
    """
    records = catalog.capture().rows
    owners: dict[int, list[str]] = {}
    sources = []
    for name, codes, _ in records:
        for text in str(codes).split():
            code = int(text.removeprefix("U+"), 16)
            owners.setdefault(code, []).append(str(name))
            char = chr(code)
            if char.islower() and char.isalpha():
                sources.append((char.upper().lower() != char, code, str(name)))
    rows, chosen = [], set()
    for _, code, source in sorted(set(sources)):
        upper = chr(code).upper()
        if len(upper) != 1:
            rows.append(
                glyph_copies.Row(source, "", note="kept: multi-character uppercase")
            )
            continue
        if upper == chr(code):
            rows.append(
                glyph_copies.Row(source, source, note="kept: no separate uppercase")
            )
            continue
        targets = sorted(owners.get(ord(upper), []))
        if not targets:
            rows.append(
                glyph_copies.Row(source, "", note="kept: no existing uppercase glyph")
            )
            continue
        target = targets[0]
        if target == source or target in chosen:
            rows.append(
                glyph_copies.Row(
                    source, target, note="kept: earlier source has priority"
                )
            )
            continue
        chosen.add(target)
        rows.append(glyph_copies.Row(source, target))
    return rows


def mappings(package: Any) -> list[Pair]:
    """Return only the ready pairs from the ordered, fully listed case survey."""
    return [(row.target, row.source) for row in survey(package) if not row.note]


def group_plan(package: Any, pairs: list[Pair]) -> dict[str, dict[str, Any]]:
    """Give targets the same per-side class memberships as their bases."""
    desired = {}
    for master in package.masters:
        groups = {}
        for name, (members, mode) in package.kerning(master).groups.items():
            original = list(members)
            if mode not in {"KernLeft", "KernRight", "KernBothSide"}:
                continue
            new = [member for member in original if member not in {t for t, _ in pairs}]
            new.extend(
                target
                for target, base in pairs
                if base in original and target not in new
            )
            if new != original:
                groups[str(name)] = (new, mode)
        desired[str(master)] = groups
    return desired


def validate_pairs(
    package: Any,
    pairs: list[Pair],
    *,
    facts: history.AutoFacts | None = None,
    allow_rebuild: bool = False,
) -> None:
    """Check masters, layer locks, automatic owners and component cycles."""
    if not package.masters:
        raise ValueError("The font needs at least one master.")
    if not pairs:
        raise ValueError("No matching glyphs. Check the font and figure names.")
    facts = history.scan_auto_facts(package) if facts is None else facts
    for target, base in pairs:
        why = history.refusal(facts, target, "geometry", allow_bases=allow_rebuild)
        if why:
            raise ValueError(f"{target}: {why}.")
        for master in package.masters:
            source = package.findName(base)
            layer = source.findLayer(master) if source is not None else None
            if layer is None or layer.isNull or layer.autoLayer:
                raise ValueError(f"{base}: needs a plain layer for {master}.")
            glyph = package.findName(target)
            old = glyph.findLayer(master) if glyph is not None else None
            if old is not None and not old.isNull and old.isLocked:
                raise ValueError(f"{target} · {master}: layer is locked.")
        # A new base must not reach the target through existing components.
        todo, seen = [base], set()
        while todo:
            name = todo.pop()
            if name == target:
                raise ValueError(f"{target}: the new component would be circular.")
            if name in seen:
                continue
            seen.add(name)
            glyph = package.findName(name)
            if glyph is not None:
                todo.extend(
                    writer.base_of(s)
                    for layer in glyph.layers
                    for s in writer.components(layer)
                )


def prepare(
    package: Any, pairs: list[Pair], *, allow_rebuild: bool = False
) -> list[tuple[str, str, Any, float]]:
    """Build detached components through the App before the outline commit."""
    facts = history.scan_auto_facts(package)
    validate_pairs(package, pairs, facts=facts, allow_rebuild=allow_rebuild)
    result = []
    for target, base in pairs:
        wanted = [
            component_creation.NewComponent(base, str(m)) for m in package.masters
        ]
        components = component_creation.build_components(package, target, wanted, facts)
        for master, component in zip(package.masters, components, strict=True):
            layer = package.findName(base).findLayer(master)
            result.append((target, str(master), component, float(layer.advanceWidth)))
    return result


def component_rows(
    package: Any, rows: list[glyph_copies.Row], *, allow_rebuild: bool = False
) -> list[glyph_copies.Row]:
    """List per-target refusals without discarding other eligible targets."""
    facts = history.scan_auto_facts(package)
    candidates = glyph_creation.auto_candidates(
        package,
        facts,
        [r.target for r in rows if r.target and package.findName(r.target) is None],
    )
    existing = any(not r.note and package.findName(r.target) is not None for r in rows)
    safe = component_creation.prototype(package, facts) if existing else None
    result = []
    for row in rows:
        note = row.note
        rebuild = candidates.get(row.target, ())
        if not note:
            try:
                validate_pairs(
                    package,
                    [(row.target, row.source)],
                    facts=facts,
                    allow_rebuild=allow_rebuild,
                )
                if package.findName(row.target) is not None:
                    if safe is None:
                        note = f"{row.target}: kept; {component_creation.NO_PROTOTYPE}."
                elif rebuild and not allow_rebuild:
                    note = f"{row.target}: kept; {glyph_creation.rebuild_note(rebuild)}"
            except ValueError as error:
                note = f"{row.target}: kept; {error}"
        result.append(
            glyph_copies.Row(row.source, row.target, note=note, rebuild=rebuild)
        )
    return result


def apply_pairs(
    package: Any,
    pairs: list[Pair],
    *,
    title: str = TITLE,
    replace_contours: bool = True,
    clear_anchors: bool = True,
    allow_rebuild: bool = False,
    unicodes: dict[str, tuple[int, ...]] | None = None,
    kept: list[str] | None = None,
    report: list[str] | None = None,
    disclosure: dict[str, Any] | None = None,
) -> int:
    """Replace target components, widths and class memberships in one history batch."""
    ids = edit_guards.pending_updates()
    captured = {"pending_updates": ids, "pending_note": edit_guards.pending_note(ids)}
    edit_guards.disclose(captured, disclosure if disclosure is not None else {})
    if report is not None and ids and disclosure is None:
        report.append(captured["pending_note"])
    elif disclosure is None and report is None:
        edit_guards.disclose(captured)
    facts = history.scan_auto_facts(package)
    rows = component_rows(
        package,
        [glyph_copies.Row(base, target) for target, base in pairs],
        allow_rebuild=allow_rebuild,
    )
    if kept is not None:
        kept.extend(row.note for row in rows if row.note)
    pairs = [(r.target, r.source) for r in rows if not r.note]
    existing = [(t, b) for t, b in pairs if package.findName(t) is not None]
    steps = prepare(package, existing, allow_rebuild=allow_rebuild) if existing else []
    specs = [
        glyph_creation.NewGlyph(
            target,
            tuple(
                (str(m), float(package.findName(base).findLayer(m).advanceWidth))
                for m in package.masters
            ),
            (unicodes or {}).get(target, ()),
            components=tuple(
                glyph_creation.Part(str(m), base) for m in package.masters
            ),
        )
        for target, base in pairs
        if package.findName(target) is None
    ]
    groups = group_plan(package, pairs)
    created = glyph_creation.create_glyphs(
        package, specs, title, facts, allow_rebuild=allow_rebuild
    )
    names = [str(glyph.name) for glyph in created.glyphs]
    created_text = "new glyphs that exist now: " + ", ".join(names) if names else ""
    diagnostics = list(created.mismatches)
    if report is not None:
        report.extend(([created_text] if created_text else []) + diagnostics)
    if diagnostics and not allow_rebuild:
        raise RuntimeError("; ".join([*diagnostics, created_text, history.UNDO_HINT]))
    if not steps and not any(groups.values()):
        return len(specs) * len(package.masters)
    if steps:
        edited = list(dict.fromkeys(target for target, _, _, _ in steps))
        glyphs = [package.findName(target) for target in edited]
        layers = [
            package.findName(target).findLayer(master) for target, master, _, _ in steps
        ]
        layers = [layer for layer in layers if layer is not None and not layer.isNull]
    else:
        memberships = [
            (target, master)
            for target, _ in pairs
            for master, changes in groups.items()
            if any(
                (target in package.kerning(master).groups[name][0])
                != (target in value[0])
                for name, value in changes.items()
            )
        ]
        edited = list(dict.fromkeys(target for target, _ in memberships))
        glyphs = [package.findName(target) for target in edited]
        layers = [
            package.findName(target).findLayer(master) for target, master in memberships
        ]
        layers = [layer for layer in layers if layer is not None and not layer.isNull]
    retain = [
        item
        for layer in layers
        for shape in writer.components(layer)
        for item in history.component_history(shape)
    ]
    container = package.kerningContainer()
    retain.extend([package, package.mastersContainer(), container])
    made, written = [], []

    def mutate() -> list[Any]:
        package.checkInitHistoryState(0)
        container.checkInitHistoryState(0)
        for target, master, component, width in steps:
            glyph = package.findName(target)
            if glyph is None:
                raise ValueError(f"{target}: target changed; Preview again.")
            layer = glyph.findLayer(master)
            if layer is None or layer.isNull:
                layer = glyph.findLayerCreate(master)
                made.append(layer)
            if replace_contours:
                for shape in list(layer.shapes):
                    if shape.isComponent or bool(shape.contours):
                        layer.removeShape(shape)
                if clear_anchors:
                    layer.clearAnchors()
            else:
                for shape in list(writer.components(layer)):
                    layer.removeShape(shape)
            component = component_creation.add_component(layer, component)
            writer.refreshed(component)
            layer.advanceWidth = width
            layer.changed()
            if layer.update() is False:
                raise RuntimeError(f"FontLab could not update {target} · {master}.")
            written.append((layer, component, width))
        for master, changes in groups.items():
            for name, value in changes.items():
                package.kerning(master).groups[name] = value
        return made

    def read_back() -> list[str]:
        missed = [
            str(layer.name)
            for layer, component, width in written
            if component not in layer.shapes or layer.advanceWidth != width
        ]
        for master, changes in groups.items():
            now = dict(package.kerning(master).groups.items())
            missed.extend(
                f"{master}: class {name}"
                for name, value in changes.items()
                if name not in now or (list(now[name][0]), now[name][1]) != value
            )
        return missed

    try:
        result = history.commit(
            title,
            layers,
            glyphs,
            mutate,
            operation="geometry" if steps else "metadata",
            facts=history.scan_auto_facts(package),
            allow_bases=allow_rebuild,
            retain=retain,
            read_back=read_back,
        )
    except (ValueError, RuntimeError, TimeoutError) as error:
        if names:
            raise history.PartialWriteError(
                title,
                [
                    error,
                    RuntimeError(created_text),
                    *(RuntimeError(text) for text in diagnostics),
                ],
            ) from error
        raise
    if result.mismatches:
        raise RuntimeError(
            "; ".join(
                [*diagnostics, *result.mismatches, created_text, history.UNDO_HINT]
            )
        )
    return len(steps) + len(specs) * len(package.masters)


def plan_key(package: Any, rows: list[glyph_copies.Row]) -> tuple:
    """Bind Preview and confirmation to the font, rows and target shape identities."""
    return (
        int(package.id),
        tuple(str(m) for m in package.masters),
        tuple(
            (
                row.source,
                row.target,
                row.note,
                tuple(
                    (
                        str(layer.name),
                        tuple(int(shape.id) for shape in layer.shapes),
                        len(layer.anchors),
                    )
                    for layer in package.findName(row.target).layers
                )
                if row.target and package.findName(row.target) is not None
                else (),
            )
            for row in rows
        ),
    )


def panel_type() -> type:
    """Use the shared full table with an explicit Preview and confirmation."""
    from fly import qt

    class UnicasePanel(selection_panel.panel_type()):
        """List every chosen and kept case mapping; never change the font on open."""

        TITLE, KEY, ACTION = TITLE, KEY, "Apply"
        SCOPE, CONSENT, ALIGN = False, "", False
        HEADERS = ("Lowercase source", "Uppercase target", "Action")

        def build_controls(self) -> None:
            self.preview_key: tuple | None = None
            self.preview_button = qt.QtGui.QPushButton("Preview")
            self.add_row("", self.preview_button)
            self.watch(self.preview_button.clicked, self.preview)

        def plan(self) -> list[glyph_copies.Row]:
            package = self.font_package()
            self.font_masters = list(package.masters)
            return component_rows(package, survey(package))

        def cells(self, row: glyph_copies.Row) -> list[str]:
            return [
                row.source,
                row.target,
                row.note or f"replace on {len(self.font_masters)} masters",
            ]

        def intro(self) -> str:
            return "Canonical round-trip lowercase first; then Unicode and glyph-name order. Later mappings stay. Replacing existing outlines is recorded as one Undo step."

        def refresh(self) -> None:
            super().refresh()
            try:
                unchanged = (
                    self.preview_key is not None
                    and plan_key(self.font_package(), self.rows) == self.preview_key
                )
                self.apply_button.setEnabled(
                    unchanged and any(not row.note for row in self.rows)
                )
            except (ValueError, RuntimeError, TimeoutError):
                self.apply_button.setEnabled(False)

        def preview(self) -> None:
            self.preview_key = None
            self.refresh()
            if any(not row.note for row in self.rows):
                self.preview_key = plan_key(self.font_package(), self.rows)
                self.apply_button.setEnabled(True)
                self.status.setText("Preview ready. Apply asks for confirmation.")

        def apply(self) -> None:
            try:
                package = self.font_package()
                rows = self.plan()
                if (
                    self.preview_key is None
                    or plan_key(package, rows) != self.preview_key
                ):
                    self.preview_key = None
                    self.apply_button.setEnabled(False)
                    raise ValueError("The plan changed. Press Preview before Apply.")
                todo = [row for row in rows if not row.note]
                count = len(todo)
                message = f'Replace uppercase drawings in "{package.name}"?\n{count} glyphs, {count * len(package.masters)} layers.\n0 targets created; {count} targets replaced.'
                answer = qt.QtGui.QMessageBox.question(
                    self,
                    TITLE,
                    message,
                    qt.QtGui.QMessageBox.StandardButtons(
                        qt.QtGui.QMessageBox.Yes | qt.QtGui.QMessageBox.No
                    ),
                    qt.QtGui.QMessageBox.No,
                )
                if answer != qt.QtGui.QMessageBox.Yes:
                    return
                package = self.font_package()
                rows = self.plan()
                if plan_key(package, rows) != self.preview_key:
                    raise ValueError(
                        "The plan changed during confirmation. Press Preview again."
                    )
                disclosure = {"pending_updates": (), "pending_note": ""}
                changed = apply_pairs(
                    package, [(row.target, row.source) for row in rows if not row.note], disclosure=disclosure
                )
                self.preview_key = None
                self.refresh()
                self.last_result = {"layers": changed, **disclosure}
                self.status.setText(edit_guards.append_note(f"Changed {changed} master layers.", self.last_result))
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.preview_key = None
                self.apply_button.setEnabled(False)
                self.status.setText(str(error))

    return UnicasePanel


def main() -> Any:
    """Show the reusable current-font component-set panel."""
    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        from fly import ap, qt

        qt.QtGui.QMessageBox.warning(ap.fontlab.MainWindow(), TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
