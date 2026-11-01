# this_file: Scripts/Masters/Selection Layer Navigator.py
# SPDX-License-Identifier: Apache-2.0
# ruff: noqa: PLR0402 -- Fly submodules require explicit import aliases.
"""Compare selected glyph slots by layer name or by one design axis.

What: A non-modal navigator with Previous and Next. Layer order uses the first
usable selected slot to choose one name for all selected slots, across masters
and auxiliary layers. Skip locked layers in this mode. An unusable reference
gets a named kept row; the next usable slot supplies the reference instead.
Axis mode moves each slot to its next coordinate while keeping
all other axis coordinates fixed. Wrap at either end. Italic / Slant selects
the first axis tagged ital or slnt. All font axes are available.

How: Read the live selection on each click through App. Explicit text-block
layer names stay explicit, so repeated glyphs can show different layers. Slots
without an explicit layer name continue to follow the glyph's active layer.
Changing that active layer also affects other following slots of that glyph.
Read native master positions for intermediate layers; keep layers without
complete coordinates.
In a Font window, axis mode changes the current font master. Layer order needs
a Glyph window. Missing or ambiguous targets produce named kept rows. No
outlines, metrics, preferences or font history are written.

Why: Native Layer > Next (Alt+.) and Layer > Previous (Alt+,) navigate the
active glyph only and skip locked layers.
This panel adds selection-only synchronization, axis filtering, reverse travel
and per-slot results. Master Switcher chooses a named master; this tool finds
the next related coordinate instead. Display Next Layer and Display Previous
Layer cycle each glyph's backups separately within one master.

Usage: Open a font. Run the tool, select glyph slots in a Glyph window, choose
Layer order or an axis, then click Previous or Next. Each click reads the live
selection. After changing fonts, click Use Current Font. The result area lists
every changed or kept slot. Close releases the panel's signal connections.

Benefit: Compare matching drawings while keeping explicit unselected slots fixed.

Credit: Alex Slobzheninov, https://github.com/slobzheninov/Glyphs-Scripts,
Apache-2.0, copyright 2020 Alex Slobzheninov. Independent behaviour rewrite of
App/Next Layer in Selection.py, Previous Layer in Selection.py, Toggle Axis
1.py through Toggle Axis 4.py, Toggle Italic.py and ToggleAxis.py. No source
code, identifiers or comments were copied beyond public API names.
"""

from math import isfinite
from time import monotonic
from typing import Any

TITLE = "Selection Layer Navigator"
KEY = "masters_selection_layer_navigator"
SECONDS = 2.0


def ordered_target(names: list[str], current: str, step: int) -> str:
    """Choose a neighbour in native layer order; reject ambiguous names."""
    if step not in (-1, 1) or len(names) < 2 or len(set(names)) != len(names):
        raise ValueError("Need two distinct layer names and a direction of -1 or 1.")
    if current not in names:
        raise ValueError(f"Layer '{current}' has no eligible neighbour.")
    return names[(names.index(current) + step) % len(names)]


def axis_target(
    rows: list[tuple[str, tuple[float, ...]]], current: str, axis: int, step: int
) -> str:
    """Sort only locations on the same axis line; refuse coordinate ties."""
    values = dict(rows)
    if current not in values or len(values) != len(rows):
        raise ValueError(f"Layer '{current}' has no unique axis location.")
    origin = values[current]
    if not 0 <= axis < len(origin):
        raise ValueError("The requested axis is missing.")
    if any(len(v) != len(origin) or not all(map(isfinite, v)) for v in values.values()):
        raise ValueError("Axis locations must be complete and finite.")
    related = [
        (v[axis], n)
        for n, v in rows
        if all(v[i] == origin[i] for i in range(len(origin)) if i != axis)
    ]
    if len({v for v, _ in related}) != len(related):
        raise ValueError("Multiple layers share a location on this axis line.")
    return ordered_target([n for _, n in sorted(related)], current, step)


def axis_index(package: Any, mode: str) -> int:
    """Resolve font axis short names, or the first Italic/Slant tag."""
    for index, axis in enumerate(package.axes):
        if (mode == "italic" and str(axis.tag) in ("ital", "slnt")) or (
            mode != "italic" and str(axis.shortName) == mode
        ):
            return index
    raise ValueError("The requested axis is not in the current font.")


def body_layers(glyph: Any, *, skip_locked: bool = False) -> list[Any]:
    """Keep body layers; layer-order navigation also skips locked drawings."""
    return [
        layer
        for layer in glyph.layers
        if not (layer.isNull or layer.isMaskLayer or layer.isService)
        and not (skip_locked and layer.isLocked)
    ]


def positioned(package: Any, layers: list[Any]) -> list[tuple[str, tuple[float, ...]]]:
    """Use native layer positions; do not guess absent intermediate coordinates."""
    rows = []
    keys = [str(axis.shortName) for axis in package.axes]
    for layer in layers:
        name = str(layer.name)
        location = (
            package.location(name)
            if name in package.masters
            else layer.getMasterPosition()
        )
        if location is not None and all(key in location for key in keys):
            rows.append((name, tuple(float(location[key]) for key in keys)))
    return rows


def display_slot(selection: Any, occurrence: Any, target: str, deadline: float) -> None:
    """Change only the selected slot; verify context and read the result back."""
    import fly.ap.layer_selection as layer_selection
    import fly.ap.qtsafe as qtsafe

    if layer_selection.document_context(deadline) != selection.context:
        raise ValueError("Document changed; select the glyphs again.")
    blocks = qtsafe.qt_list(selection.carriers[0].textBlocks)
    block = next((b for b in blocks if int(b.id) == occurrence.block_id), None)
    if block is None:
        raise ValueError("The selected text block changed.")
    info = block.getGlyphAt(occurrence.index)
    if info is None or int(info.glyph.id) != occurrence.glyph_id:
        raise ValueError("The selected glyph slot changed.")
    shown = str(info.symbol.layerName) or str(info.glyph.activeLayer.name)
    if shown != occurrence.layer_name or not (info.isSelected or info.isActive):
        raise ValueError("The selected layer or selection changed.")
    try:
        explicit = bool(str(info.symbol.layerName))
        if explicit:
            info.symbol.layerName = target
        else:
            occurrence.glyph.findLayer(target).setActive()
        block.changed()
        shown = (
            str(block.getGlyphAt(occurrence.index).symbol.layerName)
            if explicit
            else str(occurrence.glyph.updateActiveLayer(False).name)
        )
        if shown != target:
            raise RuntimeError("FontLab did not display the requested layer.")
    except (ValueError, RuntimeError, TimeoutError) as error:
        raise RuntimeError(
            f"{error} Display may have changed; choose a layer again."
        ) from error


def navigate(mode: str | None, step: int, expected_id: int | None) -> list[str]:
    """Plan from current data; keep individual refusals and continue the selection."""
    import fly.ap.layer_selection as layer_selection
    import fly.ap.master_switcher as master_switcher
    import fly.ap.scripting as scripting

    package = scripting.current_package()
    if package is None:
        raise ValueError("Open a font first.")
    if int(package.id) != expected_id:
        raise ValueError("The current font changed. Click Use Current Font.")
    deadline = monotonic() + SECONDS
    selection = layer_selection.capture(deadline)
    index = axis_index(package, mode) if mode is not None else None
    if selection.context[:2] != (int(package.id), str(package.master)):
        raise ValueError("The current font or master changed; try again.")
    if selection.context[2] == "font":
        if index is None:
            raise ValueError("Layer order needs a Glyph window.")
        try:
            rows = [
                (
                    str(name),
                    tuple(
                        float(package.location(name)[a.shortName]) for a in package.axes
                    ),
                )
                for name in package.masters
            ]
        except (KeyError, TypeError) as error:
            raise ValueError(
                "A font master has an incomplete axis location."
            ) from error
        target = axis_target(rows, str(package.master), index, step)
        try:
            master_switcher.switch(package, target)
            if str(package.master) != target:
                raise RuntimeError("FontLab did not switch to the requested master.")
        except (ValueError, RuntimeError, TimeoutError) as error:
            raise RuntimeError(f"{error} Current master may have changed.") from error
        return [f"Current master: {target}"]
    if not selection.occurrences:
        raise ValueError("Select a glyph in a Glyph window first.")
    if layer_selection.document_context(deadline) != selection.context:
        raise ValueError("Document changed; select the glyphs again.")
    shared = None
    reference_errors: dict[int, str] = {}
    if index is None:
        for number, reference in enumerate(selection.occurrences):
            try:
                shared = ordered_target(
                    [
                        str(layer.name)
                        for layer in body_layers(reference.glyph, skip_locked=True)
                    ],
                    reference.layer_name,
                    step,
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                reference_errors[number] = f"reference cannot choose a layer: {error}"
            else:
                break
    messages = []
    for number, occurrence in enumerate(selection.occurrences):
        if number in reference_errors:
            messages.append(f"kept {occurrence.glyph_name}: {reference_errors[number]}")
            continue
        if monotonic() >= deadline:
            messages.append(f"kept {occurrence.glyph_name}: navigation time limit.")
            continue
        try:
            layers = body_layers(occurrence.glyph, skip_locked=index is None)
            target = (
                shared
                if index is None
                else axis_target(
                    positioned(package, layers), occurrence.layer_name, index, step
                )
            )
            if target not in [str(layer.name) for layer in layers]:
                raise ValueError(f"Layer '{target}' is not available.")
            display_slot(selection, occurrence, target, deadline)
            messages.append(
                f"{occurrence.glyph_name}: {occurrence.layer_name} -> {target}"
            )
        except RuntimeError as error:
            messages.append(f"{occurrence.glyph_name}: {error}")
        except (KeyError, TypeError, ValueError, TimeoutError) as error:
            messages.append(f"kept {occurrence.glyph_name}: {error}")
    return messages


def panel_type() -> type:
    """Build a small modeless panel with native colours and owned signals."""
    import fly.ap.scripting as scripting
    from fly import qt

    class Navigator(qt.QtGui.QDialog):
        """Read fresh selection per click; bind the font only on explicit request."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent)
            self._connections: list = []
            self.bound_id: int | None = None
            self.options: list[str | None] = []
            self.setWindowTitle(TITLE)
            self.setModal(False)
            self.resize(430, 260)
            root = qt.QtGui.QVBoxLayout(self)
            self.mode_box = qt.QtGui.QComboBox()
            root.addWidget(self.mode_box)
            self.results = qt.QtGui.QPlainTextEdit()
            self.results.setReadOnly(True)
            root.addWidget(self.results)
            self.status = qt.QtGui.QLabel("Each click reads the live selection.")
            root.addWidget(self.status)
            buttons = qt.QtGui.QHBoxLayout()
            for title, callback in (
                ("Use Current Font", lambda *a: self.bind_font()),
                ("Previous", lambda *a: self.travel(-1)),
                ("Next", lambda *a: self.travel(1)),
                ("Close", lambda *a: self.close()),
            ):
                button = qt.QtGui.QPushButton(title)
                buttons.addWidget(button)
                scripting.connect_guarded(self, button.clicked, callback)
            root.addLayout(buttons)
            self.bind_font()

        def bind_font(self) -> None:
            """Populate the current font's axes after explicit user intent."""
            package = scripting.current_package()
            self.mode_box.clear()
            self.options = [None]
            self.mode_box.addItem("Layer order — same name in selection")
            self.bound_id = None if package is None else int(package.id)
            if package is not None:
                for axis in package.axes:
                    self.options.append(str(axis.shortName))
                    self.mode_box.addItem(f"Axis {axis.tag} ({axis.shortName})")
                self.options.append("italic")
                self.mode_box.addItem("Italic / Slant axis")
            self.results.setPlainText(
                "Open a font first."
                if package is None
                else "Select glyph slots, choose a mode, then Previous or Next."
            )

        def travel(self, step: int) -> None:
            """Report every slot, including refusals, without closing the panel."""
            try:
                self.results.setPlainText(
                    "\n".join(
                        navigate(
                            self.options[int(self.mode_box.currentIndex)],
                            step,
                            self.bound_id,
                        )
                    )
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.results.setPlainText(str(error))

        def closeEvent(self, event: Any) -> None:
            scripting.close_script_dialog(self, event, KEY)

    return Navigator


def main() -> Any:
    """Show one retained navigator through the shared App lifecycle."""
    import fly.ap.scripting as scripting

    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
