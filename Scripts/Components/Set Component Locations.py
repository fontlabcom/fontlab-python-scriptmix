# this_file: Scripts/Components/Set Component Locations.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Set Component Locations
"""Set or reset component source locations across selected glyphs and masters.

What: Give components a font-axis location, such as #wt=650,wd=100. Reset
sets Base layer name to the host master layer, as Reset to current layer does.
How: Preview each occurrence and its old and new source-layer choice. Set
one coordinate per declared axis and component/master occurrence. Each row
starts at the component's current location. Set writes only edited rows,
and keeps an existing @node suffix. Write componentLayer in
place through the shared geometry history writer, then read it back. Each
write is recorded as one Undo step. No source glyph or layer is renamed.
Why: Select component instance and Reset to current layer work on individual
components. This panel adds batch scope, per-master values and kept rows.
A multi-master base already answers font-axis locations; no conversion is
needed. Glyph-local axes use source-layer locations. Use Set Intermediate
Layer to create those layers; this panel uses the font's declared axes.
Use: Select glyphs. Run this tool. Choose Set or Reset, the component scope
and the host masters. Optionally enter an exact source-name filter. Review
the preview before Apply. Selected components are read from each glyph's
active layer and matched by shape position and base name in other masters.
All components in selected glyphs is the default. For Selected components,
select components in a Glyph window first. Reload selection reads current
coordinates and clears pending field edits. In Set mode, Apply without edits
writes nothing.
Benefit: Tune or reset many instances without repeating per-component edits.
Automatic layers, their owners and bases, locked layers, shared element data
and missing sources are listed as kept. Other eligible occurrences still
write. Set refuses unknown axes and non-finite or out-of-range coordinates.

Credit: Independent behaviour rewrite after Fernando Díaz, Reset Type Studio,
Glyphs-Scripts/Smart Components/Values for Smart Components.py and Selected
to Normal Components.py. Apache-2.0, declared in README.md; no LICENSE file.
Copyright 2025 Fernando Díaz & Reset Type Studio.
Repository: https://github.com/Reset-Type-Studio/Glyphs-Scripts .
No source code was copied. Reset sets each base layer to its host master
layer without deleting the source glyph's variation layers.
"""

import math
import re
from typing import Any

import fly.ap.component_panel as panels
import fly.ap.component_writer as writer
import fly.ap.edit_guards as guards
import fly.ap.history as history  # noqa: PLR0402 - native facade
import fly.ap.scripting as scripting  # noqa: PLR0402 - native facade
from fly import qt

TITLE = "Set Component Locations"
KEY = "components_set_locations"
RowKey = tuple[str, str, Any]


def encode_location(package: Any, values: dict[str, float]) -> str:
    """Encode native # syntax in declared-axis order, within design bounds.

    The native builder replaces # with : before decodeMasterPosition parses
    comma-separated shortName=value pairs. Use design units, not user units.
    """
    axes = list(package.axes)
    keys = [str(axis.shortName).lower() for axis in axes]
    if (
        not keys
        or len(set(keys)) != len(keys)
        or any(not key.isascii() or not key.isalnum() for key in keys)
    ):
        raise ValueError("Declare axes with unique short names in Font Info.")
    if set(values) != set(keys):
        raise ValueError("Set one coordinate for each declared font axis.")
    pairs = []
    for key, axis in zip(keys, axes, strict=True):
        number = float(values[key])
        if not math.isfinite(number) or not float(axis.designMin) <= number <= float(
            axis.designMax
        ):
            raise ValueError(
                f"{key}: choose a finite coordinate inside the design range."
            )
        text = str(int(number)) if number.is_integer() else repr(number)
        pairs.append(f"{key}={text}")
    return "#" + ",".join(pairs)


def component_targets(
    glyph: Any, layer: Any, selected_only: bool
) -> list[tuple[Any, str]]:
    """Resolve selection by position and base name; never substitute a sibling."""
    if not selected_only:
        source = layer if layer is not None else glyph.updateActiveLayer(False)
        return (
            [
                (shape, "" if layer is not None else "missing master layer")
                for shape in writer.components(source)
            ]
            if source is not None
            else []
        )
    active = glyph.updateActiveLayer(False)
    if active is None or active.isNull:
        return []
    targets = []
    for index, source in enumerate(active.shapes):
        if not source.isComponent or not source.selected:
            continue
        shape = (
            layer.shapes[index]
            if layer is not None and index < len(layer.shapes)
            else None
        )
        same = (
            shape is not None
            and shape.isComponent
            and writer.base_of(shape) == writer.base_of(source)
        )
        targets.append(
            (
                shape if same else source,
                "" if same else "component position or source differs in this master",
            )
        )
    return targets


def location_plan(
    package: Any,
    glyphs: list[Any],
    masters: list[str],
    values: dict[str, dict[str, float]],
    facts: history.AutoFacts,
    *,
    reset: bool = False,
    name: str = "",
    selected_only: bool = True,
    row_values: dict[RowKey, dict[str, float]] | None = None,
    changed: set[RowKey] | None = None,
    observed: dict[RowKey, str] | None = None,
    row_errors: dict[RowKey, str] | None = None,
) -> writer.Plan:
    """Preview each eligible edit or kept occurrence; a refusal stays local."""
    if any(c in name for c in ("\x00", "\u00a0", "\u2028", "\u2029")):
        raise ValueError(
            "Enter a source name without control or non-breaking characters."
        )
    plan = writer.Plan()
    refused = history.refusals(facts, [g.name for g in glyphs], "geometry")
    for glyph in glyphs:
        for master in masters:
            label = f"{glyph.name} · {master}"
            layer = writer.layer_of(glyph, master)
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
            edits = []
            for shape, mismatch in component_targets(glyph, layer, selected_only):
                base = writer.base_of(shape)
                if name.strip() and base != name.strip():
                    continue
                why = reason or mismatch
                if not why and int(shape.shapeData.referenceCount) != 1:
                    why = "shared element data"
                if not why and package.findName(base) is None:
                    why = f"missing source glyph {base}"
                old = str(shape.shapeData.componentLayer)
                key = (str(glyph.name), master, shape.id)
                location = str(layer.name) if reset and layer is not None else old
                untouched = not reset and changed is not None and key not in changed
                if not reset and not untouched and not why:
                    try:
                        coordinates = (
                            row_values.get(key, {})
                            if row_values is not None
                            else values.get(master, {})
                        )
                        location = encode_location(package, coordinates)
                        if "@" in old:
                            location += old[old.index("@") :]
                    except (ValueError, RuntimeError, TimeoutError) as error:
                        why = str(error)
                if not reset and observed is not None and observed.get(key) != old:
                    why = "component location changed; reload selection"
                if not reset and row_errors is not None and key in row_errors:
                    why = row_errors[key]
                edit = None if why or old == location else (shape.id, location)
                result = f"kept: {why}" if why else (location or "current layer")
                if not why and edit is None:
                    result = "same, kept"
                plan.rows.append(
                    (
                        label,
                        writer.Change(
                            base, old or "base active layer", result, edit, key=key
                        ),
                    )
                )
                if edit is not None:
                    edits.append(edit)
            if edits:
                plan.work.append((glyph, layer, edits))
    return plan


def current_coordinates(package: Any, shape: Any, master: str) -> dict[str, float]:
    """Read a component's explicit coordinates or named source-layer position.

    flLocation supports key reads: the native mapping returns None for an
    absent key, a float for a scalar and a tuple for an anisotropic value.
    Do not iterate it or reinterpret an anisotropic position as a scalar.
    """
    reference = str(shape.shapeData.componentLayer).split("@", 1)[0]
    head, marker, text = reference.partition("#")
    position = None
    if head in package.masters:
        position = package.location(head)
    elif head:
        base = package.findName(writer.base_of(shape))
        layer = writer.layer_of(base, head) if base is not None else None
        if layer is None:
            raise ValueError(
                f"Cannot read source layer {head}; use Reset or the native instance control."
            )
        position = layer.getMasterPosition()
    elif not marker:
        base = package.findName(writer.base_of(shape))
        layer = base.updateActiveLayer(False) if base is not None else None
        if layer is None:
            raise ValueError("Cannot read the base active layer; use Reset.")
        position = layer.getMasterPosition()
    values = {}
    aliases = {}
    for axis in package.axes:
        key = str(axis.shortName).lower()
        aliases[key] = aliases[str(axis.name).lower()] = key
        number = position[key] if position is not None else None
        if number is None:
            number = float(axis.designDef)
        if not isinstance(number, (int, float)) or not math.isfinite(number):
            raise ValueError(
                f"Cannot edit anisotropic or non-finite {key}; use the native instance control."
            )
        values[key] = float(number)
    if marker:
        for pair in re.split(r"[,;\s]+", text.strip()):
            if not pair:
                continue
            name, sign, value = pair.partition("=")
            if not sign or name.lower() not in aliases:
                raise ValueError(
                    "Cannot read custom or bounded axis coordinates; use the native instance control."
                )
            values[aliases[name.lower()]] = float(value)
    if any(not math.isfinite(value) for value in values.values()):
        raise ValueError("Current location is non-finite; use Reset.")
    return values


class LocationEditor(writer.Editor):
    """Change only the source-layer choice; no element is removed or cloned."""

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        """Resolve existing shape IDs before history opens."""
        return [
            (layer.shapes[writer.shape_index(layer, shape_id)], location)
            for shape_id, location in edits
        ]

    def write(self, layer: Any, steps: list[Any]) -> None:
        """Rebuild each existing component after setting its location."""
        for shape, location in steps:
            shape.shapeData.componentLayer = location
            writer.refreshed(shape)

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        """Read back each stored location and its occurrence identity."""
        return [
            f"{layer.name}/{writer.base_of(shape)}"
            for layer, steps in prepared
            for shape, location in steps
            if str(shape.shapeData.componentLayer) != location
            or shape.id not in {part.id for part in layer.shapes}
        ]


class LocationPanel(panels.panel_type()):
    """Non-modal per-occurrence coordinate table and read-only action preview."""

    TITLE, KEY, ACTION, DONE = TITLE, KEY, "Apply", "Changed"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Component", "Current", "New")

    def build_controls(self) -> None:
        """Keep one table signal; rebuilding rows creates no widget connections."""
        self.mode_box = qt.QtGui.QComboBox()
        self.mode_box.addItems(["Set location", "Reset to current layer"])
        self.target_box = qt.QtGui.QComboBox()
        self.target_box.addItems(
            ["Selected components", "All components in selected glyphs"]
        )
        self.target_box.setCurrentIndex(1)
        self.filter_edit = qt.QtGui.QLineEdit()
        self.filter_edit.setPlaceholderText("Optional exact source name")
        self.master_scope = self.scope_box()
        self.master_scope.setCurrentIndex(1)
        for row, (label, control, signal) in enumerate(
            [
                ("Action", self.mode_box, self.mode_box.currentIndexChanged),
                ("Components", self.target_box, self.target_box.currentIndexChanged),
                ("Source", self.filter_edit, self.filter_edit.textChanged),
                ("Masters", self.master_scope, self.master_scope.currentIndexChanged),
            ]
        ):
            self.form.addWidget(qt.QtGui.QLabel(label), row, 0)
            self.form.addWidget(control, row, 1)
            self.watch(signal)
        axes = list(self.package.axes) if self.package is not None else []
        self.control_schema = [
            (str(a.shortName).lower(), float(a.designMin), float(a.designMax))
            for a in axes
        ]
        self.control_masters = list(self.masters)
        self.axis_table = qt.QtGui.QTableWidget(0, len(axes))
        self.axis_table.setHorizontalHeaderLabels(
            [f"{a.name} ({a.shortName})" for a in axes]
        )
        self.axis_table.setMinimumHeight(120)
        self.axis_table.setMaximumHeight(200)
        self.form.addWidget(self.axis_table, 4, 0, 1, 2)
        self.watch(self.axis_table.itemChanged)
        self.coordinate_rows: list[RowKey] = []
        self.axis_controls: dict[tuple[RowKey, str], Any] = {}
        self.baselines: dict[RowKey, dict[str, float]] = {}
        self.source_names: dict[RowKey, str] = {}
        self.coordinate_errors: dict[RowKey, str] = {}

    def on_reload(self) -> None:
        """Discard field edits so the next preview reads current component data."""
        self.coordinate_rows = []
        self.axis_controls = {}

    def ensure_rows(self, package: Any, glyphs: list[Any]) -> None:
        """Read current locations when the selected occurrences change."""
        targets = []
        name = str(self.filter_edit.text).strip()
        for glyph in glyphs:
            for master in self.chosen_masters():
                layer = writer.layer_of(glyph, master)
                for shape, mismatch in component_targets(
                    glyph, layer, self.target_box.currentIndex == 0
                ):
                    if not mismatch and (not name or writer.base_of(shape) == name):
                        targets.append(((str(glyph.name), master, shape.id), shape))
        keys = [key for key, shape in targets]
        if keys == self.coordinate_rows:
            return
        self.coordinate_rows = keys
        (
            self.axis_controls,
            self.baselines,
            self.source_names,
            self.coordinate_errors,
        ) = {}, {}, {}, {}
        labels = []
        self.axis_table.blockSignals(True)
        try:
            self.axis_table.setRowCount(len(targets))
            for row, (key, shape) in enumerate(targets):
                label = f"{key[0]} · {key[1]} · {writer.base_of(shape)}"
                self.source_names[key] = str(shape.shapeData.componentLayer)
                values = {}
                try:
                    values = current_coordinates(package, shape, key[1])
                except (ValueError, RuntimeError, TimeoutError) as error:
                    self.coordinate_errors[key] = str(error)
                    label += f" — {error}"
                self.baselines[key] = values
                labels.append(label)
                for column, (axis, minimum, maximum) in enumerate(self.control_schema):
                    item = qt.QtGui.QTableWidgetItem(
                        str(values[axis]) if axis in values else ""
                    )
                    self.axis_controls[key, axis] = item
                    self.axis_table.setItem(row, column, item)
            self.axis_table.setVerticalHeaderLabels(labels)
        finally:
            self.axis_table.blockSignals(False)

    def current_plan(
        self, package: Any, glyphs: list[Any], facts: history.AutoFacts
    ) -> writer.Plan:
        """Set only changed occurrence rows; Reset uses the host layer names."""
        schema = [
            (str(a.shortName).lower(), float(a.designMin), float(a.designMax))
            for a in package.axes
        ]
        if (
            list(package.masters) != self.control_masters
            or schema != self.control_schema
        ):
            raise ValueError(
                "Axes or masters changed; close this panel and run it again."
            )
        self.ensure_rows(package, glyphs)
        reset = self.mode_box.currentIndex == 1
        self.axis_table.setEnabled(not reset)
        values, changed, errors = {}, set(), dict(self.coordinate_errors)
        if not reset:
            for key in self.coordinate_rows:
                coordinates = {}
                try:
                    coordinates = {
                        axis: float(self.axis_controls[key, axis].text())
                        for axis, low, high in schema
                    }
                except ValueError:
                    errors[key] = "Enter numeric axis coordinates."
                values[key] = coordinates
                if coordinates != self.baselines[key]:
                    changed.add(key)
        return location_plan(
            package,
            glyphs,
            self.chosen_masters(),
            {},
            facts,
            reset=reset,
            name=str(self.filter_edit.text),
            selected_only=self.target_box.currentIndex == 0,
            row_values=values,
            changed=changed,
            observed=self.source_names,
            row_errors=errors,
        )

    def refresh(self) -> None:
        """Preview untouched rows as kept; explain editor component selection."""
        plan, message = writer.Plan(), ""
        self.subtitle.setText(self.intro())
        try:
            if self.package is not None and self.glyphs:
                plan = self.current_plan(self.package, self.glyphs, self.facts)
        except (ValueError, RuntimeError, TimeoutError) as error:
            message = str(error)
        self.fill(plan)
        self.apply_button.setEnabled(bool(plan.work) and not message)
        if not message and not plan.rows and self.target_box.currentIndex == 0:
            message = "Select components in a Glyph window, or choose All components in selected glyphs."
        self.status.setText(message or self.summary(plan))

    def apply(self) -> None:
        """Replan from live data; no edited Set rows means no history action."""
        message = ""
        wrote = False
        try:
            package, glyphs = self.live_glyphs()

            self.facts = history.scan_auto_facts(package)
            plan = self.current_plan(package, glyphs, self.facts)
            wrote = bool(plan.work)
            self.last_result = writer.apply_work(
                plan.work, TITLE, self.facts, LocationEditor()
            )

            message = f"Changed {self.last_result['edits']} components; review kept rows above."
            message = guards.append_note(message, self.last_result)
        except (ValueError, RuntimeError, TimeoutError) as error:
            message = str(error)
        finally:
            if wrote:
                self.on_reload()
            self.refresh()
        self.status.setText(message)


def main() -> Any:
    """Show or raise the shared reusable panel; show host failures as text."""
    try:
        return scripting.show_script_dialog(LocationPanel, KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
