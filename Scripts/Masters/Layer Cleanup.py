# this_file: Scripts/Masters/Layer Cleanup.py
# SPDX-License-Identifier: Apache-2.0
"""List the extra layers of the selected glyphs and delete the ticked ones.

What it does:
    Fonts collect masks, backups, alternates and experiment layers. The
    panel lists every non-master layer of the selected glyphs with its kind
    and contour count. Tick rows one by one, or tick a whole kind with one
    button. "Delete Ticked" removes the ticked layers.

How it works:
    The kind comes from the layer role, fly.ap.masters.associated_master,
    and the same backup resolver as Restore Backup Layer: "mask" for a
    background; "backup" for <master> backup <suffix> and legacy @ or
    space-prefixed backups; "alternate" for <master>#... layers, such as bracket
    layers; "other" for every other layer. Master layers, service layers,
    image layers and temporary "|temp|" layers are never listed. The delete
    runs in one Undo step through the shared module fly.ap.history. FontLab
    records the step only for layers plus their glyph, so the notification
    holds a layer that stays: the body layer of a deleted mask, else the
    first master layer. The script then checks by layer id that every
    ticked layer is gone.

Why this design:
    - Nothing is ticked at the start. A delete is explicit.
    - The shown (active) layer of a glyph and locked layers are listed but
      cannot be ticked: FontLab would have to pick another shown layer, and
      a lock is a deliberate "keep".
    - Glyphs with automatic layers and bases of automatic composites (also
      through manual composites) are listed but cannot be ticked. A
      notification there makes FontLab rebuild the automatic glyphs, and
      Undo does not restore them.
    - A deleted body layer leaves its mask. The mask has its own row: tick
      both to remove both.
    - The components of the deleted layers (shape, shape data, builder) are
      read before the edit and retained in the notification. The deletion
      is recorded as one Undo step. Edit > Undo of removed components depends on FontLab (fl#7641).
    - To clear the backgrounds of the whole font, use Cleaning > Clear All
      Layer Backgrounds or Clear Master Backgrounds: they check the whole
      font mapping first. This panel is for mixed cleanup of a selection.
    - Delete is refused while FontLab has pending glyph updates. The panel
      binds to the font that was current when it opened.

How to use:
    Select glyphs in the Font window (Select All for the whole font). Run
    the script. Tick rows or press a kind button. Press Delete Ticked. The
    deletion is recorded as one Undo step.

Benefit:
    A clean Layers panel and a smaller file, without clicking through every
    glyph.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (masters_layer_cleanup.py, "Layer Cleanup").
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

TITLE = "Layer Cleanup"
KEY = "masters_layer_cleanup"
KINDS = ("mask", "backup", "alternate", "other")
TEMP_PREFIX = "|temp|"
MAX_NAMES = 8  # glyph names shown in the subtitle


@dataclass(frozen=True)
class Entry:
    """One extra layer. ``note`` is empty when the layer may be deleted."""

    glyph: Any
    layer: Any
    name: str
    kind: str
    contours: int
    note: str = ""


def _backup_master(name: str, masters: Sequence[str]) -> str | None:
    """Resolve backups by the longest master prefix; keep legacy @ names.

    New names use <master> backup <suffix>, then optional collision (n).
    Exact master names, bracket names and temporary names are never backups.
    """
    if "#" in name or "|temp|" in name or name.casefold() in {m.casefold() for m in masters}:
        return None
    if "@" in name:
        prefix = name.split("@", 1)[0]
        return prefix if prefix in masters else None
    return next((m for m in sorted(masters, key=len, reverse=True) if name.startswith(m + " ")), None)


def kind(layer: Any, masters: Sequence[str]) -> str | None:
    """Return the kind of an extra layer, or None for a layer that is never listed."""
    from fly.ap.masters import associated_master

    name = str(layer.name)
    if layer.isMaskLayer:
        return "mask"
    if layer.isService or layer.isImgLayer or name.startswith(TEMP_PREFIX):
        return None
    if name.lower() in {str(m).lower() for m in masters}:
        return None
    if _backup_master(name, masters) is not None:
        return "backup"
    if associated_master(name, masters) is not None:
        return "alternate"
    return "other"


def _contours(layer: Any) -> int:
    """Return the number of contours in the non-component shapes of ``layer``."""
    return sum(len(s.contours) for s in layer.shapes if not s.isComponent)


def survey(package: Any, names: Sequence[str], masters: Sequence[str], facts: Any) -> list[Entry]:
    """List the extra layers of ``names`` in glyph order. Change nothing.

    Notes, in this order: a glyph the geometry policy refuses, a locked
    layer, the shown layer.
    """
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    entries: list[Entry] = []
    for name in names:
        glyph = package.findName(name)
        if glyph is None or glyph.isNull:
            continue
        reason = history.refusal(facts, str(glyph.name), "geometry")
        active = glyph.updateActiveLayer(False)
        shown = int(active.id) if active is not None and not active.isNull else None
        for layer in glyph.layers:
            what = kind(layer, masters)
            if what is None:
                continue
            note = ""
            if reason:
                note = f"{reason} (kept)"
            elif layer.isLocked:
                note = "locked layer (kept)"
            elif int(layer.id) == shown:
                note = "shown layer (kept)"
            entries.append(Entry(glyph, layer, str(layer.name), what, _contours(layer), note))
    return entries


def undo_layers(glyph: Any, doomed: set[int], masters: Sequence[str]) -> list[Any]:
    """Return the surviving body layers that carry the Undo step of a deletion.

    FontLab records an Undo step only for a list of layers plus their glyph;
    a glyph alone adds no step. Take the body layer of each deleted mask;
    else the first master layer that stays. ``doomed`` holds layer ids.
    Raise ValueError when no such layer is left.
    """
    found = []
    for layer in glyph.layers:
        if int(layer.id) in doomed or layer.isMaskLayer or layer.autoLayer:
            continue
        mask = layer.getMaskLayer(False)
        if mask is not None and not mask.isNull and int(mask.id) in doomed:
            found.append(layer)
    if not found:
        for master in masters:
            layer = glyph.findLayer(master)
            if layer is not None and not layer.isNull and int(layer.id) not in doomed and not layer.autoLayer:
                found.append(layer)
                break
    if not found:
        raise ValueError(f"'{glyph.name}' has no layer left to record the Undo step.")
    return found


def delete_layers(entries: Sequence[Entry], masters: Sequence[str], facts: Any) -> dict[str, Any]:
    """Delete ``entries`` as ONE Undo step and check that they are gone.

    A kept entry raises ValueError before any change. Return
    ``{"layers", "glyphs", "deleted", "mismatches"}``.
    """
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    kept = [f"{e.glyph.name}/{e.name}: {e.note}" for e in entries if e.note]
    if kept:
        raise ValueError("Refused: " + "; ".join(kept[:3]))
    if not entries:
        return {"layers": 0, "glyphs": 0, "deleted": [], "mismatches": []}
    glyphs = list({str(e.glyph.name): e.glyph for e in entries}.values())
    doomed = {int(e.layer.id) for e in entries}
    carriers = [layer for glyph in glyphs for layer in undo_layers(glyph, doomed, masters)]
    # Read before any removal: a builder read after detachment can be too late (fl#7641).
    retain = [obj for e in entries for shape in e.layer.shapes for obj in history.component_history(shape)]
    labels = [f"{e.glyph.name}/{e.name}" for e in entries]  # read before the layers go

    def mutate() -> None:
        for entry in entries:
            entry.glyph.removeLayer(entry.layer)

    def read_back() -> list[str]:
        return [
            f"{e.glyph.name}: layer '{e.name}' is still there"
            for e in entries
            if int(e.layer.id) in {int(x.id) for x in e.glyph.layers}
        ]

    done = history.commit(
        TITLE, carriers, glyphs, mutate, operation="geometry", facts=facts, read_back=read_back, retain=retain
    )
    return {"layers": len(entries), "glyphs": len(glyphs), "deleted": labels, "mismatches": list(done.mismatches)}


def plural(count: int, word: str) -> str:
    """Return "1 layer" or "2 layers"."""
    return f"{count} {word}{'' if count == 1 else 's'}"


def panel_type() -> type:
    """Build the panel class once Qt is available (inside FontLab)."""
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.scripting as scripting  # noqa: PLR0402
    from fly import qt

    QtGui, QtCore = qt.QtGui, qt.QtCore

    class CleanupPanel(QtGui.QDialog):
        """Kind buttons, a table with tick boxes, status, Use selection, Close, Delete Ticked."""

        def __init__(self, parent: Any = None) -> None:
            QtGui.QDialog.__init__(self, parent)
            self._connections: list[Any] = []
            self.entries: list[Entry] = []
            self.names: list[str] = []
            self.package_id: int | None = None
            self.last_result: dict[str, Any] = {}
            self.setWindowTitle(TITLE)
            self.setMinimumWidth(540)
            root = QtGui.QVBoxLayout(self)
            root.setContentsMargins(20, 18, 20, 16)
            root.setSpacing(12)
            heading = QtGui.QLabel(TITLE)
            font = heading.font
            font.setPointSizeF(font.pointSizeF() * 1.35)
            font.setBold(True)
            heading.setFont(font)
            root.addWidget(heading)
            self.subtitle = QtGui.QLabel("")
            self.subtitle.setWordWrap(True)
            root.addWidget(self.subtitle)
            row = QtGui.QHBoxLayout()
            row.addWidget(QtGui.QLabel("Tick"))
            self.kind_buttons: dict[str, Any] = {}
            for label in (*KINDS, "none"):
                button = QtGui.QPushButton(f"all {label}s" if label != "none" else "none")
                button.setAutoDefault(False)  # Enter belongs to Delete Ticked
                row.addWidget(button)
                self.kind_buttons[label] = button
            row.addStretch(1)
            root.addLayout(row)
            self.table = QtGui.QTableWidget(0, 4)
            self.table.setHorizontalHeaderLabels(["Glyph", "Layer", "Kind", "Contours"])
            self.table.verticalHeader().setVisible(False)
            self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
            self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            self.table.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
            self.table.setMinimumHeight(280)
            root.addWidget(self.table, 1)
            footer = QtGui.QHBoxLayout()
            self.status = QtGui.QLabel("")
            self.status.setWordWrap(True)
            footer.addWidget(self.status, 1)
            self.selection_button = QtGui.QPushButton("Use selection")
            self.close_button = QtGui.QPushButton("Close")
            self.apply_button = QtGui.QPushButton("Delete Ticked")
            self.apply_button.setDefault(True)
            for button in (self.selection_button, self.close_button, self.apply_button):
                footer.addWidget(button)
            root.addLayout(footer)
            for label, button in self.kind_buttons.items():
                scripting.connect_guarded(self, button.clicked, lambda *a, label=label: self.tick_kind(label))
            for signal, slot in (
                (self.table.itemChanged, lambda *a: self.update_status()),
                (self.selection_button.clicked, lambda *a: self.reselect()),
                (self.apply_button.clicked, lambda *a: self.apply()),
                (self.close_button.clicked, lambda *a: self.close()),
            ):
                scripting.connect_guarded(self, signal, slot)
            try:
                package = scripting.current_package()
                if package is not None:
                    self.package_id = package.id
                    self.names = scripting.names_selected_names()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))
            self.refresh()

        def font_package(self) -> Any:
            """Return the bound font. Refuse a closed or switched font."""
            if self.package_id is None:
                raise ValueError("Open a font and select glyphs. Then run this script again.")
            package = scripting.current_package()
            if package is None or package.id != self.package_id:
                raise ValueError("The font changed. Run this script again.")
            return package

        def plan(self) -> list[Entry]:
            """List the extra layers from the live font with fresh auto-layer facts."""
            package = self.font_package()
            if not self.names:
                raise ValueError("Select glyphs in the Font window. Then press Use selection.")
            masters = [str(m) for m in package.masters]
            return survey(package, self.names, masters, history.scan_auto_facts(package))

        def refresh(self) -> None:
            """Fill the table. Every tick box starts empty."""
            try:
                self.entries = self.plan()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.entries = []
                self.table.setRowCount(0)
                self.subtitle.setText(str(error))
                self.apply_button.setEnabled(False)
                return
            shown = ", ".join(self.names[:MAX_NAMES]) + (" …" if len(self.names) > MAX_NAMES else "")
            self.subtitle.setText(f"{plural(len(self.names), 'glyph')}: {shown}")
            self.table.blockSignals(True)
            self.table.setRowCount(len(self.entries))
            for number, entry in enumerate(self.entries):
                cells = [str(entry.glyph.name), entry.name, entry.kind, entry.note or str(entry.contours)]
                for column, text in enumerate(cells):
                    item = QtGui.QTableWidgetItem(text)
                    if column == 1 and not entry.note:
                        item.setFlags(int(item.flags() | QtCore.Qt.ItemIsUserCheckable))
                        item.setCheckState(QtCore.Qt.Unchecked)
                    self.table.setItem(number, column, item)
            self.table.blockSignals(False)
            self.update_status()

        def ticked(self) -> list[Entry]:
            """Return the ticked entries, in table order."""
            return [
                entry for number, entry in enumerate(self.entries)
                if not entry.note and self.table.item(number, 1).checkState() == QtCore.Qt.Checked
            ]  # fmt: skip

        def tick_kind(self, label: str) -> None:
            """Tick every free row of one kind and clear the others; "none" clears all."""
            self.table.blockSignals(True)
            for number, entry in enumerate(self.entries):
                if not entry.note:
                    state = QtCore.Qt.Checked if entry.kind == label else QtCore.Qt.Unchecked
                    self.table.item(number, 1).setCheckState(state)
            self.table.blockSignals(False)
            self.update_status()

        def update_status(self) -> None:
            """Count the ticks. Delete needs at least one."""
            count = len(self.ticked())
            self.apply_button.setEnabled(count > 0)
            self.status.setText(f"{plural(len(self.entries), 'extra layer')} · {count} ticked for deletion")

        def reselect(self) -> None:
            """Take the glyph selection from the Font window again."""
            self.font_package()
            self.names = scripting.names_selected_names()
            self.refresh()

        def apply(self) -> None:
            """Delete the ticked layers, read from a fresh survey. One Undo step."""
            wanted = {(int(e.glyph.id), int(e.layer.id)) for e in self.ticked()}
            try:
                fresh = [e for e in self.plan() if (int(e.glyph.id), int(e.layer.id)) in wanted]
                if len(fresh) != len(wanted):
                    raise ValueError("The layers changed. Check the table and tick again.")
                package = self.font_package()
                masters = [str(m) for m in package.masters]
                result = delete_layers(fresh, masters, history.scan_auto_facts(package))
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.refresh()
                self.status.setText(str(error))
                return
            self.last_result = result
            self.refresh()
            text = f"Deleted {plural(result['layers'], 'layer')} from {plural(result['glyphs'], 'glyph')}"
            if result["mismatches"]:
                text += " · did not read back as planned: " + "; ".join(result["mismatches"][:5])
            self.status.setText(text)

        def closeEvent(self, event: Any) -> None:
            """Disconnect owned signals, then delete the panel."""
            scripting.close_script_dialog(self, event, KEY)

    return CleanupPanel


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
