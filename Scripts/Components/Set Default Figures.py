# this_file: Scripts/Components/Set Default Figures.py
# SPDX-License-Identifier: Apache-2.0
"""Set one figure family as components in the default digit cells.

What: Choose lining (.lf), oldstyle (.osf), tabular lining (.tf), or tabular
oldstyle (.tosf) figures. Missing default digit cells are created. With Replace
own contours on, their old contours are removed; turn it off to
keep them. Their components, widths and kerning class memberships follow
the chosen figures on every master. Unicode assignments stay.
How: Preview exact base names and set explicit base and master-layer names. No
automatic layer is made.
Why: One complete set avoids mixing figure styles between glyphs or masters.
Use: Choose the set and the contour option, inspect the table, then Apply.
Benefit: Ten digits across every master. Each new glyph is recorded as its own
Undo step.
Changed kerning memberships are recorded in the same Undo step, or as one more
Undo step when no outlines are filled. Circular references, automatic targets
and targets without
a safe plain component to copy are listed as kept; other targets can change.
Components are placed at the origin with the source advance; Glyphs'
automatic component alignment has no identical FontLab control here.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Components/Set default figures.py, Apache-2.0.
Repository: https://github.com/pedroarilla/glyphs-scripts . No source code
copied.
"""

from typing import Any

import fly.ap.component_creation as component_creation  # noqa: PLR0402
import fly.ap.component_writer as writer
import fly.ap.edit_guards as edit_guards  # noqa: PLR0402
import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402
import fly.ap.glyph_creation as glyph_creation  # noqa: PLR0402
import fly.ap.history as history  # noqa: PLR0402
import fly.ap.scripting as scripting  # noqa: PLR0402
import fly.ap.selection_panel as selection_panel  # noqa: PLR0402

Pair = tuple[str, str]  # target, base


TITLE = "Set Default Figures"
KEY = "components_default_figures"
CHOICES = (
    "Lining (.lf)",
    "Oldstyle (.osf)",
    "Tabular lining (.tf)",
    "Tabular oldstyle (.tosf)",
)
DIGITS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
)


def mappings(package: Any, option: int = 0) -> list[Pair]:
    """Require every source in the requested family; allow missing default cells."""
    if option not in range(4):
        raise ValueError("Choose one of the four figure sets.")
    suffix = ("lf", "osf", "tf", "tosf")[option]
    pairs = [(name, f"{name}.{suffix}") for name in DIGITS]
    for target, base in pairs:
        if package.findName(base) is None:
            raise ValueError(f"Missing {target} or {base}; no figures changed.")
    return pairs


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


def write_components(
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


def apply_pairs(
    package: Any,
    pairs: list[Pair],
    *,
    replace_contours: bool = True,
    allow_rebuild: bool = False,
    kept: list[str] | None = None,
    report: list[str] | None = None,
    disclosure: dict[str, Any] | None = None,
) -> int:
    """Use the single component-set writer with figure-specific preservation rules."""
    return write_components(
        package,
        pairs,
        title=TITLE,
        replace_contours=replace_contours,
        clear_anchors=False,
        allow_rebuild=allow_rebuild,
        kept=kept,
        report=report,
        disclosure=disclosure,
        unicodes={name: (ord("0") + i,) for i, name in enumerate(DIGITS)},
    )


def panel_type() -> type:
    """Use the App selection panel for the figure-family preview and controls."""
    from fly import qt

    class FiguresPanel(selection_panel.panel_type()):
        """Choose the family and whether the old digit contours stay."""

        TITLE, KEY, ACTION = TITLE, KEY, "Apply"
        SCOPE, CONSENT, ALIGN = False, glyph_creation.REBUILD_LABEL, False
        HEADERS = ("Figure source", "Default cell", "Action")

        def build_controls(self) -> None:
            self.figure_family = qt.QtGui.QComboBox()
            self.figure_family.addItems(list(CHOICES))
            self.replace_contours = qt.QtGui.QCheckBox("Replace own contours")
            self.replace_contours.setChecked(True)
            self.add_row("Family", self.figure_family)
            self.add_row("", self.replace_contours)
            self.watch(self.figure_family.currentIndexChanged)
            self.watch(self.replace_contours.toggled)

        def plan(self) -> list[glyph_copies.Row]:
            package = self.font_package()
            self.font_masters = list(package.masters)
            return component_rows(
                package,
                [
                    glyph_copies.Row(source, target)
                    for target, source in mappings(
                        package, int(self.figure_family.currentIndex)
                    )
                ],
                allow_rebuild=self.consented(),
            )

        def cells(self, row: glyph_copies.Row) -> list[str]:
            action = (
                "replace contours and components"
                if self.replace_contours.isChecked()
                else "replace components; keep contours"
            )
            if row.rebuild and not row.note:
                action += " · " + glyph_creation.rebuild_note(row.rebuild)
            return [row.source, row.target, row.note or action]

        def intro(self) -> str:
            package = self.font_package()
            filled = any(
                not row.note and package.findName(row.target) is not None
                for row in self.rows
            )
            return (
                "Source advances and kerning memberships are copied; existing anchors stay. "
                + glyph_creation.undo_text(filled)
                + " Changed kerning memberships are recorded in the same Undo step, or as one more Undo step when no outlines are filled."
            )

        def write(self, package: Any, rows: list[glyph_copies.Row]) -> dict[str, Any]:
            disclosure = {"pending_updates": (), "pending_note": ""}
            report: list[str] = []
            count = apply_pairs(
                package,
                [(row.target, row.source) for row in rows],
                replace_contours=bool(self.replace_contours.isChecked()),
                allow_rebuild=self.consented(),
                report=report,
                disclosure=disclosure,
            )
            return {"layers": count, "report": report, **disclosure}

        def result_text(self, result: dict[str, Any]) -> str:
            return f"Changed {result['layers']} master layers." + (
                " " + "; ".join(result["report"]) if result.get("report") else ""
            )

    return FiguresPanel


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
