# this_file: Scripts/Cleaning/Start From Scratch.py
# SPDX-License-Identifier: Apache-2.0
"""Clear chosen glyph data to prepare a fresh design.

What: Remove chosen anchors, layer guides, backgrounds, images, colour marks,
kerning class memberships, auxiliary layers, stickers, or paths and components. Reset
layer metric expressions and advances to 600 when requested. All options start
off. Choose selected or all glyphs, current or all masters, masters or all
foreground layers. Glyph marks and kerning membership use the glyph scope.
How: Preview the exact scope, then confirm the font and counts before Clear.
A changed scope needs a new Preview. Image and sticker shapes stay unless chosen.
Why: Explicit switches prevent accidental deletion of unrelated design data.
Use: Select glyphs, choose the scope and data, Preview, then Clear chosen data.
Benefit: Several cleanup operations are recorded as one Undo step. Automatic
layers and their bases are refused. Shared background mappings also refuse.
Font-level guides stay; the guide option clears only guides on scoped layers.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Cleaning/Start-from-scratch.py, Apache-2.0.
Repository: https://github.com/pedroarilla/glyphs-scripts . No source code copied.
"""

from typing import Any

import fly.ap.glyph_catalog as catalog
import fly.ap.history as history  # noqa: PLR0402
import fly.ap.masters as masters  # noqa: PLR0402
import fly.ap.scripting as scripting  # noqa: PLR0402

TITLE = "Start From Scratch"
KEY = "cleaning_start_from_scratch"
OPTIONS = {
    "stickers": "Stickers",
    "anchors": "Anchors",
    "guides": "Layer guides",
    "backgrounds": "Backgrounds",
    "images": "Images",
    "marks": "Colour marks",
    "groups": "Kerning class memberships",
    "metrics": "Metric expressions and advances (600)",
    "auxiliary": "Non-master layers",
    "shapes": "Paths and components",
}
Job = tuple[Any, Any]


def scope(
    package: Any, names: list[str], all_masters: bool, auxiliaries: bool
) -> list[Job]:
    """Return current live foreground layers in the explicit glyph/master scope."""
    if not names:
        raise ValueError("Select glyphs or choose Whole font.")
    wanted = list(package.masters) if all_masters else [str(package.master)]
    result = []
    for name in dict.fromkeys(names):
        glyph = package.findName(name)
        if glyph is None or glyph.isNull:
            raise ValueError(f"{name}: the glyph is no longer in this font.")
        for layer in glyph.layers:
            if layer.isMaskLayer or layer.isService:
                continue
            owner = masters.associated_master(str(layer.name), list(package.masters))
            if owner in wanted and (auxiliaries or str(layer.name) in wanted):
                result.append((glyph, layer))
    if not result:
        raise ValueError("No foreground layers in this scope.")
    return result


def sticker_kind() -> Any:
    """Resolve the native sticker enum, including padded dictionary keys."""
    from fly import ap

    for name, value in ap.fontlab.ShapeType.items():
        if str(name).strip() == "ShapeSticker":
            return value
    raise ValueError("FontLab does not expose the ShapeSticker enum.")


def fingerprint(package: Any, jobs: list[Job], options: set[str]) -> tuple:
    """Bind a Preview to the font, glyphs, layer content identities and options."""
    return (
        int(package.id),
        str(package.master),
        tuple(sorted(options)),
        tuple(
            (
                str(glyph.name),
                int(layer.id),
                tuple(int(s.id) for s in layer.shapes),
                len(layer.anchors),
                len(layer.guidelines),
            )
            for glyph, layer in jobs
        ),
    )


def clean(package: Any, jobs: list[Job], options: set[str]) -> int:
    """Validate the complete plan, then clear it through one shared commit."""
    if not options or options - OPTIONS.keys():
        raise ValueError("Choose at least one supported cleanup option.")
    if not jobs:
        raise ValueError("No layers to clear.")
    geometry = bool(options - {"marks", "groups", "stickers"})
    operation = "geometry" if geometry else "metadata"
    sticker_type = sticker_kind() if "stickers" in options else None
    glyphs = list({str(glyph.name): glyph for glyph, _ in jobs}.values())
    doomed: dict[int, Job] = {}
    affected = {int(layer.id): layer for _, layer in jobs}
    for glyph, layer in jobs:
        if layer.autoLayer or layer.isLocked:
            raise ValueError(f"{glyph.name} · {layer.name}: automatic or locked layer.")
        if "auxiliary" in options and str(layer.name) not in package.masters:
            doomed[int(layer.id)] = (glyph, layer)
        for key, getter in (
            ("backgrounds", layer.getMaskLayer),
            ("images", layer.getImgLayer),
        ):
            if key not in options:
                continue
            mapped = getter(False)
            if mapped is None or mapped.isNull:
                continue
            if mapped.autoLayer or mapped.isLocked:
                raise ValueError(f"{glyph.name}: mapped layer is automatic or locked.")
            # The same physical mask must not also serve a foreground layer
            # outside the scope: clearing it would reach an excluded layer.
            for other in glyph.layers:
                if other.isMaskLayer or other.isService or int(other.id) in affected:
                    continue
                sibling = (
                    other.getMaskLayer(False)
                    if key == "backgrounds"
                    else other.getImgLayer(False)
                )
                if (
                    sibling is not None
                    and not sibling.isNull
                    and sibling.id == mapped.id
                ):
                    raise ValueError(
                        f"{glyph.name}: shared {key} crosses the chosen scope."
                    )
            doomed[int(mapped.id)] = (glyph, mapped)
    carriers = []
    for glyph in glyphs:
        kept = [
            layer
            for layer in glyph.layers
            if not layer.autoLayer
            and not layer.isService
            and not layer.isMaskLayer
            and int(layer.id) not in doomed
        ]
        if not kept:
            raise ValueError(f"{glyph.name}: needs one kept layer to record history.")
        edited = [
            layer
            for owner, layer in jobs
            if owner is glyph and int(layer.id) not in doomed
        ]
        carriers.extend(edited or kept[:1])
    retained = [
        obj
        for _, layer in [*jobs, *doomed.values()]
        for shape in layer.shapes
        for obj in history.component_history(shape)
    ]
    groups: dict[str, dict[str, Any]] = {}
    if "groups" in options:
        targets = {str(glyph.name) for glyph in glyphs}
        for master in package.masters:
            changed = {}
            for name, (members, mode) in package.kerning(master).groups.items():
                if mode in {"KernLeft", "KernRight", "KernBothSide"}:
                    remaining = [name for name in members if name not in targets]
                    if remaining != list(members):
                        changed[str(name)] = (remaining, mode)
            groups[str(master)] = changed
        retained.extend(
            [package, package.mastersContainer(), package.kerningContainer()]
        )

    removed = [
        (glyph, layer, int(layer.id), str(layer.name))
        for glyph, layer in doomed.values()
    ]
    retained.extend(
        item
        for _, layer in jobs
        for shape in layer.shapes
        if sticker_type is not None and shape.shapeType == sticker_type
        for item in (shape, shape.shapeData)
    )
    retained = list({id(item): item for item in retained}.values())

    def mutate() -> None:
        if "groups" in options:
            package.checkInitHistoryState(0)
            package.kerningContainer().checkInitHistoryState(0)
        for glyph, layer in jobs:
            if int(layer.id) in doomed:
                continue
            if "anchors" in options:
                layer.clearAnchors()
            if "guides" in options:
                layer.guidelines = []
            for shape in list(layer.shapes):
                if (
                    "shapes" in options
                    and (shape.isComponent or bool(shape.contours))
                    or "stickers" in options
                    and shape.shapeType == sticker_type
                ):
                    layer.removeShape(shape)
            if "metrics" in options:
                layer.resetMetricsLeft()
                layer.resetMetricsRight()
                layer.resetMetricsWidth()
                layer.advanceWidth = 600
            if geometry:
                layer.changed()
            if geometry and layer.update() is False:
                raise RuntimeError(
                    f"FontLab could not update {glyph.name} · {layer.name}."
                )
        if "marks" in options:
            for glyph in glyphs:
                glyph.mark = 0
        for master, changes in groups.items():
            for name, value in changes.items():
                package.kerning(master).groups[name] = value
        for glyph, layer in doomed.values():
            glyph.removeLayer(layer)

    def read_back() -> list[str]:
        missed = []
        for glyph, layer in jobs:
            if int(layer.id) in doomed:
                continue
            bad = (
                "anchors" in options
                and bool(layer.anchors)
                or "guides" in options
                and bool(layer.guidelines)
                or "shapes" in options
                and any(shape.isComponent or shape.contours for shape in layer.shapes)
                or "stickers" in options
                and any(shape.shapeType == sticker_type for shape in layer.shapes)
                or "metrics" in options
                and (
                    layer.advanceWidth != 600
                    or layer.metricsLeft
                    or layer.metricsRight
                    or layer.metricsWidth
                )
            )
            if bad:
                missed.append(f"{glyph.name} · {layer.name}")
        missed.extend(
            str(glyph.name)
            for glyph in glyphs
            if "marks" in options and glyph.mark != 0
        )
        missed.extend(
            name
            for glyph, _, layer_id, name in removed
            if any(other.id == layer_id for other in glyph.layers)
        )
        for master, changes in groups.items():
            now = dict(package.kerning(master).groups.items())
            missed.extend(
                f"{master}: class {name}"
                for name, value in changes.items()
                if name not in now or (list(now[name][0]), now[name][1]) != value
            )
        return missed

    result = history.commit(
        TITLE,
        carriers,
        glyphs,
        mutate,
        operation=operation,
        facts=history.scan_auto_facts(package),
        retain=retained,
        read_back=read_back,
    )
    if result.mismatches:
        raise RuntimeError(
            "Some data remain. Native changes may remain; use Edit > Undo."
        )
    return len(jobs)


def panel_type() -> type:
    """Small non-modal checklist with explicit scope and a counted preview."""
    from fly import qt

    gui = qt.QtGui

    class ResetPanel(gui.QDialog):
        """All deletion switches start off; read selection again for each action."""

        def __init__(self, parent: Any = None) -> None:
            gui.QDialog.__init__(self, parent)
            self._connections: list[Any] = []
            package = scripting.current_package()
            self.package_id = int(package.id) if package is not None else None
            self.preview_key: tuple | None = None
            self.setWindowTitle(TITLE)
            self.setMinimumWidth(440)
            box = gui.QVBoxLayout(self)
            box.setContentsMargins(20, 18, 20, 16)
            box.setSpacing(10)
            self.glyph_choice = gui.QComboBox()
            self.glyph_choice.addItems(["Selected glyphs", "Whole font"])
            self.master_choice = gui.QComboBox()
            self.master_choice.addItems(["Current master", "All masters"])
            self.layer_choice = gui.QComboBox()
            self.layer_choice.addItems(["Master layers", "All foreground layers"])
            for widget in (self.glyph_choice, self.master_choice, self.layer_choice):
                box.addWidget(widget)
            self.switches = {}
            for key, label in OPTIONS.items():
                widget = gui.QCheckBox(label)
                widget.setChecked(False)
                self.switches[key] = widget
                box.addWidget(widget)
            hint = gui.QLabel(
                "Font-level guides stay. Stickers include text, arrows and symbols."
            )
            hint.setWordWrap(True)
            box.addWidget(hint)
            self.status = gui.QLabel("Choose scope and data, then Preview.")
            self.status.setWordWrap(True)
            box.addWidget(self.status)
            buttons = gui.QHBoxLayout()
            for text, slot in (
                ("Preview", self.inspect_scope),
                ("Clear chosen data", self.execute),
                ("Close", self.close),
            ):
                button = gui.QPushButton(text)
                if text == "Clear chosen data":
                    self.clear_button = button
                    button.setEnabled(False)
                buttons.addWidget(button)
                scripting.connect_guarded(
                    self, button.clicked, lambda *a, action=slot: action()
                )
            box.addLayout(buttons)
            for control in (self.glyph_choice, self.master_choice, self.layer_choice):
                scripting.connect_guarded(
                    self, control.currentIndexChanged, lambda *a: self.invalidate()
                )
            for control in self.switches.values():
                scripting.connect_guarded(
                    self, control.toggled, lambda *a: self.invalidate()
                )

        def invalidate(self) -> None:
            self.preview_key = None
            self.clear_button.setEnabled(False)

        def plan(self) -> tuple[Any, list[Job], set[str]]:
            package = scripting.current_package(self.package_id)
            if self.package_id is None or package is None:
                raise ValueError("Open the original font and run this tool again.")
            names = (
                [str(row[0]) for row in catalog.capture().rows]
                if self.glyph_choice.currentIndex
                else scripting.names_selected_names()
            )
            jobs = scope(
                package,
                names,
                bool(self.master_choice.currentIndex),
                bool(self.layer_choice.currentIndex),
            )
            options = {
                key for key, widget in self.switches.items() if widget.isChecked()
            }
            if not options:
                raise ValueError("Choose at least one cleanup option.")
            if "auxiliary" in options and not self.layer_choice.currentIndex:
                raise ValueError(
                    "To delete non-master layers, choose All foreground layers."
                )
            return package, jobs, options

        def inspect_scope(self) -> None:
            try:
                package, jobs, options = self.plan()
                self.preview_key = fingerprint(package, jobs, options)
                self.clear_button.setEnabled(True)
                count = len({str(glyph.name) for glyph, _ in jobs})
                labels = ", ".join(OPTIONS[key] for key in OPTIONS if key in options)
                self.status.setText(
                    f"{count} glyphs, {len(jobs)} layers. Clear: {labels}."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

        def execute(self) -> None:
            try:
                package, jobs, options = self.plan()
                if (
                    self.preview_key is None
                    or fingerprint(package, jobs, options) != self.preview_key
                ):
                    self.invalidate()
                    raise ValueError("The plan changed. Press Preview before Clear.")
                glyph_count = len({str(glyph.name) for glyph, _ in jobs})
                labels = ", ".join(OPTIONS[key] for key in OPTIONS if key in options)
                message = f'Clear {labels} in "{package.name}"?\n{glyph_count} glyphs, {len(jobs)} layers.'
                answer = gui.QMessageBox.question(
                    self,
                    TITLE,
                    message,
                    gui.QMessageBox.StandardButtons(
                        gui.QMessageBox.Yes | gui.QMessageBox.No
                    ),
                    gui.QMessageBox.No,
                )
                if answer != gui.QMessageBox.Yes:
                    return
                package, jobs, options = self.plan()
                if fingerprint(package, jobs, options) != self.preview_key:
                    self.invalidate()
                    raise ValueError(
                        "The plan changed during confirmation. Press Preview again."
                    )
                count = clean(package, jobs, options)
                self.invalidate()
                self.status.setText(f"Cleared chosen data on {count} layers.")
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

        def closeEvent(self, event: Any) -> None:
            scripting.close_script_dialog(self, event, KEY)

    return ResetPanel


def main() -> Any:
    """Open the cleanup checklist; no data change on opening."""
    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        from fly import ap, qt

        qt.QtGui.QMessageBox.warning(ap.fontlab.MainWindow(), TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
