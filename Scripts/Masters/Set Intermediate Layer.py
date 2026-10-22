# this_file: Scripts/Masters/Set Intermediate Layer.py
# SPDX-License-Identifier: Apache-2.0
"""Add interpolated intermediate layers to selected glyphs at explicit coordinates.

What: Preview one new intermediate layer per selected glyph. Set each axis
coordinate in design units, then press Add Layers. Existing layers stay.
How: FontLab interpolates each glyph with interpolateInstance. The result gets
a location name such as :wt=512.5 and is added through shared history.commit.
The change is recorded as one Undo step. No glyph or font master is created.
Why: FontLab's Layers and Masters panel can add a layer and Glyph > Reinterpolate
can fill it. This panel combines the two over a selection, with a refusal report.
Use: Open a font with at least two masters and declared axes. Select glyphs,
run the tool, set coordinates and inspect the preview before adding layers.
Benefit: Build matching intermediate locations without repeating layer setup.

Automatic glyphs and their bases, locked sources, incompatible masters,
existing locations and fonts without declared axes are kept. Editor tabs and
their order stay in place; this tool does not replace displayed glyph slots.
Fractional coordinates are preserved. Invalid values are refused.

Independent behaviour rewrite after Reza Bohloul, RezaBohloul,
Glyph/Set Intermediate Layer.py; no licence declared.
Repository: https://github.com/RezaBohloul/RezaBohloul . No source code copied.
"""

import math
from dataclasses import dataclass
from typing import Any

import fly.ap.edit_guards as guards
import fly.ap.history as history  # noqa: PLR0402 - Fly resolves App modules lazily
import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly resolves App modules lazily
import fly.ap.selection_panel as panels
from fly import fl, qt

TITLE = "Set Intermediate Layer"
KEY = "masters_set_intermediate_layer"


@dataclass
class IntermediateRow:
    """One glyph, an explicit location, and an optional reason to keep it."""

    glyph: Any
    name: str
    values: dict[str, float]
    note: str = ""


def location_values(
    package: Any, values: dict[str, float]
) -> tuple[dict[str, float], str]:
    """Validate declared design coordinates and encode FontLab's layer-name form."""
    axes = list(package.axes)
    keys = [str(axis.shortName) for axis in axes]
    if (
        not axes
        or len({key.lower() for key in keys}) != len(keys)
        or any(not key.isalnum() for key in keys)
    ):
        raise ValueError("Declare axes with unique short names in Font Info first.")
    if set(values) != set(keys):
        raise ValueError("Set one coordinate for each declared axis.")
    result = {}
    for key, axis in zip(keys, axes, strict=True):
        number = float(values[key])
        if not math.isfinite(number) or not float(axis.designMin) <= number <= float(
            axis.designMax
        ):
            raise ValueError(
                f"{axis.name}: choose a finite coordinate inside the design range."
            )
        result[key] = 0.0 if number == 0 else number
    return result, ":" + ",".join(
        f"{key.lower()}={int(value) if value.is_integer() else repr(value)}"
        for key, value in result.items()
    )


def keep_reason(
    package: Any,
    glyph: Any,
    name: str,
    values: dict[str, float],
    facts: history.AutoFacts,
) -> str:
    """Keep unsafe, duplicate or incompatible glyphs; the other glyphs still write."""
    why = history.refusal(facts, glyph.name, "geometry")
    if why:
        return why
    existing = glyph.findLayer(name)
    if existing is not None and not existing.isNull:
        return "layer already exists"
    masters = [glyph.findLayer(str(master)) for master in package.masters]
    if len(masters) < 2 or any(layer is None or layer.isNull for layer in masters):
        return "needs at least two existing master layers"
    if any(layer.isLocked or layer.isService or layer.isImg for layer in masters):
        return "locked, service or image master layer"
    if any(not masters[0].isCompatible(layer, True) for layer in masters[1:]):
        return "master outlines are incompatible"
    for layer in glyph.layers:
        if layer.isMaskLayer or layer.isService:
            continue
        position = layer.getMasterPosition()
        if position_matches(position, values):
            return f"location already exists on {layer.name}"
    return ""


def position_matches(position: Any, values: dict[str, float]) -> bool:
    """Subscript only; a missing key reads as None. Layer names lower-case keys."""
    if position is None:
        return False
    for key, value in values.items():
        actual = position[key]
        if actual is None:
            actual = position[key.lower()]
        if not isinstance(actual, (float, int)) or actual != value:
            return False
    return True


def survey(
    package: Any, names: list[str], values: dict[str, float], facts: history.AutoFacts
) -> list[IntermediateRow]:
    """One row per selected glyph, with all refusals visible before writing."""
    coordinates, name = location_values(package, values)
    rows = []
    for glyph_name in dict.fromkeys(names):
        glyph = package.findName(glyph_name)
        if glyph is None or glyph.isNull:
            rows.append(
                IntermediateRow(
                    None, name, coordinates, f"{glyph_name}: missing glyph, kept"
                )
            )
            continue
        why = keep_reason(package, glyph, name, coordinates, facts)
        rows.append(
            IntermediateRow(glyph, name, coordinates, "kept: " + why if why else "")
        )
    return rows


def write_rows(
    package: Any, rows: list[IntermediateRow], facts: history.AutoFacts
) -> dict[str, Any]:
    """Interpolate and append in one history action; retain partial additions on error."""
    ready = [
        row
        for row in rows
        if not row.note
        and row.glyph is not None
        and not keep_reason(package, row.glyph, row.name, row.values, facts)
    ]
    kept = [
        f"{r.glyph.name if r.glyph is not None else r.note}: {r.note}"
        for r in rows
        if r.note
    ]
    if not ready:
        return {"layers": 0, "mismatches": [], "kept": kept}
    guards.require_settled()
    prepared = []
    for row in ready:
        try:
            layer = row.glyph.interpolateInstance(fl.flLocation(row.values), False)
        except (ValueError, RuntimeError, TimeoutError) as error:
            kept.append(f"{row.glyph.name}: interpolation refused, kept: {error}")
            continue
        if layer is None or layer.isNull or layer.autoLayer:
            kept.append(f"{row.glyph.name}: interpolation refused, kept")
            continue
        layer.name = row.name
        prepared.append((row, layer))
    if not prepared:
        return {"layers": 0, "mismatches": [], "kept": kept}
    created: list[tuple[IntermediateRow, Any]] = []
    failures: list[str] = []

    def mutate() -> list[Any]:
        for row, layer in prepared:
            try:
                row.glyph.addLayer(layer)
                added = row.glyph.findLayer(row.name)
                if added is None or added.isNull or str(added.name) != row.name:
                    raise RuntimeError("FontLab did not add the layer.")
                created.append((row, added))
            except Exception as error:  # noqa: BLE001 - finish the one history action
                failures.append(f"{row.glyph.name}: {error}")
                try:
                    stored = row.glyph.findLayer(row.name)
                    if stored is not None and not stored.isNull:
                        created.append((row, stored))
                except (ValueError, RuntimeError, TimeoutError) as read_error:
                    failures.append(str(read_error))
                break
        return [layer for _, layer in created]

    def read_back() -> list[str]:
        missed = []
        for row, added in created:
            stored = row.glyph.findLayer(row.name)
            position = (
                None if stored is None or stored.isNull else stored.getMasterPosition()
            )
            if (
                stored is None
                or stored.isNull
                or stored.id != added.id
                or not position_matches(position, row.values)
            ):
                missed.append(f"{row.glyph.name}/{row.name}")
        return missed

    done = history.commit(
        TITLE,
        [],
        [row.glyph for row, _ in prepared],
        mutate,
        operation="geometry",
        facts=facts,
        read_back=read_back,
    )
    if done.mismatches or failures:
        raise RuntimeError(
            "FontLab did not finish adding layers: "
            + "; ".join([*failures, *done.mismatches])
            + ". Native changes may remain; use Edit > Undo."
        )
    return {"layers": len(created), "mismatches": [], "kept": kept}


class IntermediatePanel(panels.panel_type()):
    """One coordinate control per declared axis, with the shared selection preview."""

    TITLE, KEY, ACTION = TITLE, KEY, "Add Layers"
    HEADERS = ("Glyph", "New layer", "Action")
    SCOPE, CONSENT, ALIGN = False, "", False

    def build_controls(self) -> None:
        self.axis_controls: dict[str, Any] = {}
        package = scripting.current_package()
        for axis in package.axes if package is not None else ():
            box = qt.QtGui.QDoubleSpinBox()
            box.setDecimals(6)
            box.setRange(float(axis.designMin), float(axis.designMax))
            box.setValue((float(axis.designMin) + float(axis.designMax)) / 2)
            key = str(axis.shortName)
            self.axis_controls[key] = box
            self.add_row(f"{axis.name} ({key})", box)
            self.watch(box.valueChanged)

    def plan_rows(self, package: Any, masters: list[str]) -> list[IntermediateRow]:
        values = {key: float(box.value) for key, box in self.axis_controls.items()}
        return survey(package, self.names, values, self.facts)

    def cells(self, row: IntermediateRow) -> list[str]:
        return [
            str(row.glyph.name) if row.glyph is not None else "Missing glyph",
            row.name,
            row.note or "add interpolated layer",
        ]

    def write(self, package: Any, rows: list[IntermediateRow]) -> dict[str, Any]:
        return write_rows(package, rows, history.scan_auto_facts(package))

    def result_text(self, result: dict[str, Any]) -> str:
        text = f"Added {result['layers']} intermediate layer(s)"
        if result.get("kept"):
            text += "; " + "; ".join(result["kept"])
        return text


def main() -> Any:
    """Show the modeless coordinate panel, or diagnose an opening refusal."""
    try:
        return scripting.show_script_dialog(IntermediatePanel, KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        qt.QtGui.QMessageBox.warning(fl.MainWindow(), TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
