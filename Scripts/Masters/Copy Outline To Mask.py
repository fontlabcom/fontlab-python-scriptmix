# this_file: Scripts/Masters/Copy Outline To Mask.py
# SPDX-License-Identifier: Apache-2.0
"""Copy the outline of each selected glyph into the mask of its master layer.

What it does:
    For each selected glyph and chosen master, put a copy of the contours of
    the master layer into its mask (background) layer. The mask is created
    when it is missing. "Replace mask" removes what the mask holds first;
    "Add to mask" keeps it. The master layer does not change.

How it works:
    A non-modal panel lists every glyph and master with three numbers:
    contours in the outline, contours in the mask now (plus its components,
    which "Replace mask" also removes), contours in the mask after the copy.
    Apply reads the font again, then writes all masks in one Undo step
    through the shared module fly.ap.history. Existing masks join the
    history list before the edit; new masks join the notification as
    created objects. "Replace mask" removes the old mask shapes one by one.
    The shape, shape data and builder of each removed component are read
    before the edit and retained in the notification. The removal is
    recorded as one Undo step. After the write the script counts
    the mask contours again, checks that no old component is left, and
    reports any difference.

Why this design:
    - Only contours are copied. Components stay in the body: a mask is a
      drawing reference, and a component in a mask would follow later edits
      of its base glyph.
    - Each outline shape is cloned whole, so its own transform stays. FontLab
      clone() drops shape notes and names and the raw state and name of
      nodes (fl#8516, fl#8538). The script copies them back, and clears
      selection bits: a mask must not look selected. A clone with another
      contour count stops the run.
    - Edit > Undo of removed components depends on FontLab (fl#7641).
    - Automatic layers, glyphs with automatic layers, bases of automatic
      composites (also through manual composites) and locked layers are
      listed and skipped. A notification there makes FontLab rebuild the
      automatic glyphs, and Undo does not restore them.
    - Apply is refused while FontLab has pending glyph updates. The panel
      binds to the font that was current when it opened.

How to use:
    Select glyphs in the Font window. Run the script. Choose the current
    master or all masters, and the mode. Check the table. Press Copy. The
    panel stays open; press "Use selection" after you select other glyphs.

Benefit:
    A reference copy of the current drawing behind every glyph, before a
    redesign, in one step and one Undo.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (masters_copy_to_mask.py, "Copy Outline to Mask").
    Known limit: node.clone loses explicit corner smoothness and other
    scalar node properties (fl#8569); a shape clone may lose them too.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

TITLE = "Copy Outline To Mask"
KEY = "masters_copy_to_mask"
MODES = ("Replace mask", "Add to mask")
SELECTED = 0x0020  # node state bit: selected
MAX_NAMES = 8  # glyph names shown in the subtitle


@dataclass(frozen=True)
class Row:
    """One glyph/master layer and its planned mask.

    ``note`` is empty for a layer that will be copied; else it says why the
    layer is skipped. Counts are contours; ``mask_components`` counts the
    component shapes in the mask now ("Replace mask" removes them too).
    """

    glyph: Any
    master: str
    layer: Any
    outline: int
    mask_now: int
    mask_after: int
    mask_components: int = 0
    note: str = ""


def outline_shapes(layer: Any) -> list[Any]:
    """Return the non-component shapes of ``layer`` that hold contours."""
    return [s for s in layer.shapes if not s.isComponent and len(s.contours)]


def contours_in(shapes: Sequence[Any]) -> int:
    """Return the number of contours in ``shapes``."""
    return sum(len(s.contours) for s in shapes)


def _valid(layer: Any) -> bool:
    """True for a real native layer object."""
    return layer is not None and not layer.isNull


def restore_shape(old: Any, new: Any) -> None:
    """Copy back what FontLab's clone() drops (fl#8516, fl#8538).

    Restore shape note and name, and the raw state and name of every node.
    Selection bits stay as the clone has them.
    """
    new.shapeData.note, new.shapeData.name = old.shapeData.note, old.shapeData.name
    for before, after in zip(old.contours, new.contours, strict=True):
        for source, target in zip(before.nodes(), after.nodes(), strict=True):
            target.nodeState = (source.nodeState & ~SELECTED) | (target.nodeState & SELECTED)
            target.name = source.name


def clone_shape(shape: Any) -> Any:
    """Return a repaired clone of ``shape``. Raise RuntimeError on a lost contour."""
    copy = shape.clone()
    if len(copy.contours) != len(shape.contours):
        raise RuntimeError("FontLab clone changed the contour count of a shape.")
    restore_shape(shape, copy)
    return copy


def _mask_contours(layer: Any) -> int:
    """Return the contours in the mask of ``layer`` (0 without a mask)."""
    mask = layer.getMaskLayer(False)
    return contours_in([s for s in mask.shapes if not s.isComponent]) if _valid(mask) else 0


def _mask_components(layer: Any) -> int:
    """Return the component shapes in the mask of ``layer`` (0 without a mask)."""
    mask = layer.getMaskLayer(False)
    return sum(1 for s in mask.shapes if s.isComponent) if _valid(mask) else 0


def mask_cell(row: Row) -> str:
    """Return the "Mask now" table text: contours, plus components when present."""
    if not row.mask_components:
        return str(row.mask_now)
    word = "component" if row.mask_components == 1 else "components"
    return f"{row.mask_now} + {row.mask_components} {word}"


def survey(package: Any, names: Sequence[str], masters: Sequence[str], replace: bool, facts: Any) -> list[Row]:
    """Plan every glyph/master. Change nothing.

    Skip notes, in this order: no layer, automatic layer, a glyph the
    geometry policy refuses, locked layer, no outline.
    """
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    rows: list[Row] = []
    for name in names:
        glyph = package.findName(name)
        if glyph is None or glyph.isNull:
            continue
        reason = history.refusal(facts, str(glyph.name), "geometry")
        for master in masters:
            layer = glyph.findLayer(master)
            if not _valid(layer):
                rows.append(Row(glyph, master, None, 0, 0, 0, note="no layer in this master"))
                continue
            note = ""
            if layer.autoLayer:
                note = "auto layer (skipped)"
            elif reason:
                note = f"{reason} (skipped)"
            elif layer.isLocked:
                note = "locked layer (skipped)"
            outline = contours_in(outline_shapes(layer)) if not note else 0
            if not note and not outline:
                note = "no outline (skipped)"
            if note:
                rows.append(Row(glyph, master, layer, 0, 0, 0, note=note))
                continue
            now, parts = _mask_contours(layer), _mask_components(layer)
            rows.append(Row(glyph, master, layer, outline, now, outline + (0 if replace else now), parts))
    return rows


def copy_to_masks(rows: Sequence[Row], replace: bool, facts: Any) -> dict[str, Any]:
    """Copy the planned outlines into the masks as ONE Undo step.

    Return ``{"layers", "glyphs", "contours", "created", "mismatches"}``.
    Nothing to do returns zeros and makes no history call. A refusal raises
    ValueError; a failure after history started raises RuntimeError with
    the Undo hint.
    """
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    todo = [r for r in rows if not r.note]
    if not todo:
        return {"layers": 0, "glyphs": 0, "contours": 0, "created": 0, "mismatches": []}
    existing = [m for m in (r.layer.getMaskLayer(False) for r in todo) if _valid(m)]
    glyphs = list({str(r.glyph.name): r.glyph for r in todo}.values())
    # Read before any removal: a builder read after detachment can be too late (fl#7641).
    retain = [
        obj for mask in (existing if replace else ())
        for shape in mask.shapes for obj in history.component_history(shape)
    ]  # fmt: skip

    def mutate() -> list[Any]:
        made = []
        for row in todo:
            mask = row.layer.getMaskLayer(False)
            if _valid(mask):
                if replace:
                    for old in list(mask.shapes):
                        mask.removeShape(old)
            else:
                mask = row.layer.getMaskLayer(True)
                if not _valid(mask):
                    raise RuntimeError(f"FontLab could not create the mask of '{row.glyph.name}'.")
                made.append(mask)
            for shape in outline_shapes(row.layer):
                mask.addShape(clone_shape(shape))
            mask.changed()
            if mask.update() is False:
                raise RuntimeError(f"FontLab could not update the mask of '{row.glyph.name}'.")
        return made

    def read_back() -> list[str]:
        found = []
        for row in todo:
            label = f"{row.glyph.name} · {row.master}"
            count = _mask_contours(row.layer)
            if count != row.mask_after:
                found.append(f"{label}: mask has {count} contours, planned {row.mask_after}")
            left = _mask_components(row.layer)
            if replace and left:
                found.append(f"{label}: mask still has {left} component(s), planned 0")
        return found

    done = history.commit(
        TITLE, existing, glyphs, mutate, operation="geometry", facts=facts, read_back=read_back, retain=retain
    )
    return {
        "layers": len(todo),
        "glyphs": len(glyphs),
        "contours": sum(r.outline for r in todo),
        "created": len(done.created),
        "mismatches": list(done.mismatches),
    }


def plural(count: int, word: str) -> str:
    """Return "1 glyph" or "2 glyphs"."""
    return f"{count} {word}{'' if count == 1 else 's'}"


def panel_type() -> type:
    """Build the panel class once Qt is available (inside FontLab)."""
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.scripting as scripting  # noqa: PLR0402
    from fly import qt

    QtGui, QtCore = qt.QtGui, qt.QtCore

    class CopyOutlinePanel(QtGui.QDialog):
        """Masters, mode, preview table, status, Use selection, Close, Copy."""

        def __init__(self, parent: Any = None) -> None:
            QtGui.QDialog.__init__(self, parent)
            self._connections: list[Any] = []
            self.rows: list[Row] = []
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
            grid = QtGui.QGridLayout()
            grid.setHorizontalSpacing(10)
            self.scope = QtGui.QComboBox()
            self.scope.addItem("Current master")
            self.scope.addItem("All masters")
            self.mode = QtGui.QComboBox()
            for label in MODES:
                self.mode.addItem(label)
            grid.addWidget(QtGui.QLabel("Masters"), 0, 0)
            grid.addWidget(self.scope, 0, 1)
            grid.addWidget(QtGui.QLabel("Mode"), 1, 0)
            grid.addWidget(self.mode, 1, 1)
            grid.setColumnStretch(1, 1)
            root.addLayout(grid)
            self.table = QtGui.QTableWidget(0, 4)
            self.table.setHorizontalHeaderLabels(["Glyph · master", "Outline", "Mask now", "Mask after"])
            self.table.verticalHeader().setVisible(False)
            self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
            self.table.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
            self.table.setMinimumHeight(240)
            root.addWidget(self.table, 1)
            footer = QtGui.QHBoxLayout()
            self.status = QtGui.QLabel("")
            self.status.setWordWrap(True)
            footer.addWidget(self.status, 1)
            self.selection_button = QtGui.QPushButton("Use selection")
            self.close_button = QtGui.QPushButton("Close")
            self.apply_button = QtGui.QPushButton("Copy")
            self.apply_button.setDefault(True)
            for button in (self.selection_button, self.close_button, self.apply_button):
                footer.addWidget(button)
            root.addLayout(footer)
            for signal, slot in (
                (self.scope.currentIndexChanged, lambda *a: self.refresh()),
                (self.mode.currentIndexChanged, lambda *a: self.refresh()),
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

        def replace(self) -> bool:
            """True when the mode is "Replace mask"."""
            return self.mode.currentIndex == 0

        def plan(self) -> list[Row]:
            """Plan from the live font with fresh auto-layer facts."""
            package = self.font_package()
            if not self.names:
                raise ValueError("Select glyphs in the Font window. Then press Use selection.")
            masters = [package.master] if self.scope.currentIndex == 0 else list(package.masters)
            return survey(package, self.names, masters, self.replace(), history.scan_auto_facts(package))

        def refresh(self) -> None:
            """Recompute the preview. A refusal disables Copy and shows its reason."""
            try:
                self.rows = self.plan()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.rows = []
                self.table.setRowCount(0)
                self.subtitle.setText(str(error))
                self.apply_button.setEnabled(False)
                return
            shown = ", ".join(self.names[:MAX_NAMES]) + (" …" if len(self.names) > MAX_NAMES else "")
            self.subtitle.setText(f"{plural(len(self.names), 'glyph')}: {shown}")
            self.table.setRowCount(len(self.rows))
            for number, row in enumerate(self.rows):
                label = f"{row.glyph.name} · {row.master}"
                cells = [label, row.note] if row.note else [
                    label, str(row.outline), mask_cell(row), str(row.mask_after)]
                for column, text in enumerate(cells):
                    item = QtGui.QTableWidgetItem(text)
                    if column:
                        item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                    self.table.setItem(number, column, item)
            todo = [r for r in self.rows if not r.note]
            self.apply_button.setEnabled(bool(todo))
            self.status.setText(
                f"{plural(len(todo), 'layer')} will get a mask copy" if todo else "Nothing to copy"
            )

        def reselect(self) -> None:
            """Take the glyph selection from the Font window again."""
            self.font_package()
            self.names = scripting.names_selected_names()
            self.refresh()

        def apply(self) -> None:
            """Plan again from the live font, then write. One Undo step."""
            try:
                rows = self.plan()
                result = copy_to_masks(rows, self.replace(), history.scan_auto_facts(self.font_package()))
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.refresh()
                self.status.setText(str(error))
                return
            self.last_result = result
            self.refresh()
            text = (
                f"Copied {result['contours']} contours into {plural(result['layers'], 'mask')} "
                f"of {plural(result['glyphs'], 'glyph')}"
            )
            if result["created"]:
                text += f" · {result['created']} new"
            if result["mismatches"]:
                text += " · did not read back as planned: " + "; ".join(result["mismatches"][:5])
            self.status.setText(text)

        def closeEvent(self, event: Any) -> None:
            """Disconnect owned signals, then delete the panel."""
            scripting.close_script_dialog(self, event, KEY)

    return CopyOutlinePanel


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
