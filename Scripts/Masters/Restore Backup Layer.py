# this_file: Scripts/Masters/Restore Backup Layer.py
# SPDX-License-Identifier: Apache-2.0
"""Restore a backup layer into the master layer it belongs to.

What it does:
    Choose a backup layer name, such as "Regular@ 14:05:09, 21/10/26". For
    every selected glyph that has a layer with this name, replace the
    contours of the master layer with copies of the backup contours, move
    same-named anchors to the backup positions and set the backup advance
    width. Optionally delete the backup layer and its mask afterwards.

How it works:
    The script discovers plain "Regular backup" layers and old "Regular@
    backup"
    layers. The longest matching master name chooses the restore target;
    no new @ layer is created. Bracket layers ("#") and
    temporary layers are never offered. A non-modal panel shows, per glyph,
    the master, contours and width (master now → after). Restore reads the
    font again and writes all master layers in one Undo step through the
    shared module fly.ap.history, then reads contours, widths, anchors and
    deleted layers back.

Why this design:
    - The master layer object stays. Its components, guides, hints and
      other properties are kept; only outline, anchors and width come back.
      "Use Layer As Master" instead swaps two whole layers in one glyph.
    - The old outline shapes of the master are removed, never edited, so a
      shape that other glyphs share stays intact for them. FontLab clone()
      drops shape notes and names and the raw state and name of nodes
      (fl#8516, fl#8538): the script copies them back and stops when a clone
      has another contour count.
    - Missing anchors are listed, never added. Two anchors with one name, or
      an existing anchor that would move to 0, 0 (FontLab cannot Redo it,
      fl#8527), skip the glyph.
    - Skipped and listed: automatic master layers, glyphs with automatic
      layers, bases of automatic composites (also through manual
      composites), locked master layers, master layers with a metrics link
      or expression, and an empty backup. A backup that is the shown layer
      of its glyph, or that is locked or has a locked mask, is not deleted.
      Apply discloses queued ids and their possible date changes.
    - A deleted backup usually holds components. Their shape, shape data
      and builder are read before the edit and retained in the notification.
      The restore is recorded as one Undo step. Edit > Undo of removed
      components depends on FontLab (fl#7641).

How to use:
    Make backups with "Duplicate Current Layer". Later select the glyphs in
    the Font window. Run the script, choose the backup, tick "Delete the
    backup" if you want, check the table and press Restore.

Benefit:
    Undo a failed redesign of many glyphs at once, long after Edit > Undo
    has lost the steps.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (masters_restore_backup.py, "Restore Backup Layer").
    Known limit: node.clone loses explicit corner smoothness and other
    scalar node properties (fl#8569); a shape clone may lose them too.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

TITLE = "Restore Backup Layer"
KEY = "masters_restore_backup"
LINK_FIELDS = ("metricsLeft", "metricsRight", "metricsWidth")
TEMP_PREFIX = "|temp|"
MAX_NAMES = 8  # glyph names shown in the subtitle
NO_BACKUP = "No backup layers in these glyphs. Make some with Duplicate Current Layer."

Move = tuple[str, float, float]


@dataclass(frozen=True)
class Job:
    """One glyph: its backup layer, its master layer and the plan.

    ``note`` is empty for a glyph that will be restored; else it says why
    the glyph is skipped. ``mask`` is the mask layer of the backup, or None.
    """

    glyph: Any
    backup: Any
    master: str
    target: Any
    mask: Any
    contours_now: int
    contours_after: int
    width_now: float
    width_after: float
    moves: tuple[Move, ...] = ()
    missing: tuple[str, ...] = ()
    note: str = ""


def backup_master(name: str, masters: Sequence[str]) -> str | None:
    """Resolve backup layers through the shared App rule."""
    import fly.ap.masters as masters_api

    return masters_api.backup_master(name, masters)


def _valid(layer: Any) -> bool:
    """True for a real native layer object."""
    return layer is not None and not layer.isNull


def backup_names(glyphs: Sequence[Any], masters: Sequence[str]) -> list[str]:
    """Return the sorted unique backup layer names of ``glyphs``."""
    found = {
        str(layer.name)
        for glyph in glyphs
        for layer in glyph.layers
        if not layer.isMaskLayer and not layer.isService and not layer.autoLayer
        and backup_master(str(layer.name), masters)
    }
    return sorted(found)


def outline_shapes(layer: Any) -> list[Any]:
    """Return the non-component shapes of ``layer`` that hold contours."""
    return [s for s in layer.shapes if not s.isComponent and len(s.contours)]


def contours_in(layer: Any) -> int:
    """Return the number of contours in the non-component shapes of ``layer``."""
    return sum(len(s.contours) for s in layer.shapes if not s.isComponent)


def clone_shape(shape: Any) -> Any:
    """Return a repaired clone of ``shape``. Raise RuntimeError on a lost contour."""
    import fly.ap.contour_copy as contour_copy

    copy = shape.clone()
    if len(copy.contours) != len(shape.contours):
        raise RuntimeError("FontLab clone changed the contour count of a shape.")
    contour_copy.restore_shape(shape, copy)
    return copy


def replace_outline(source: Any, target: Any) -> None:
    """Remove the non-component shapes of ``target``; add clones of the source outline."""
    for shape in [s for s in target.shapes if not s.isComponent]:
        target.removeShape(shape)
    for shape in outline_shapes(source):
        target.addShape(clone_shape(shape))


def _point(pin: Any) -> tuple[float, float]:
    """Stored anchor position, unrounded."""
    return float(pin.point.x()), float(pin.point.y())


def plan_anchors(source: Any, target: Any) -> tuple[tuple[Move, ...], tuple[str, ...], str]:
    """Return (moves, missing names, problem) for same-named anchors."""
    for layer in (source, target):
        names = [str(pin.name) for pin in layer.anchors]
        twice = sorted({n for n in names if names.count(n) > 1})
        if twice:
            return (), (), f"several anchors named {', '.join(twice)} (skipped)"
    own = {str(pin.name): _point(pin) for pin in target.anchors}
    moves, missing = [], []
    for pin in source.anchors:
        name, where = str(pin.name), _point(pin)
        if name not in own:
            missing.append(name)
        elif own[name] != where:
            if where == (0.0, 0.0):
                return (), (), f"anchor {name} would move to 0, 0; FontLab cannot redo it (fl#8527)"
            moves.append((name, *where))
    return tuple(moves), tuple(missing), ""


def has_metrics_link(layer: Any) -> bool:
    """True when a sidebearing or the width holds a link or an expression."""
    return any(str(getattr(layer, field)) for field in LINK_FIELDS)


def _plan(glyph: Any, backup: Any, masters: Sequence[str], reason: str) -> Job:
    """Plan one glyph. ``reason`` is the geometry refusal of the glyph, or ""."""
    master = backup_master(str(backup.name), masters) or ""
    target = glyph.findLayer(master) if master else None
    mask = backup.getMaskLayer(False)
    mask = mask if _valid(mask) else None
    if not _valid(target):
        return Job(glyph, backup, master, None, mask, 0, 0, 0, 0, note="no master layer")
    now, width = contours_in(target), target.advanceWidth
    note = ""
    if target.autoLayer:
        note = "auto layer (skipped)"
    elif reason:
        note = f"{reason} (skipped)"
    elif target.isLocked:
        note = "locked layer (skipped)"
    elif has_metrics_link(target):
        note = "metrics link or expression (skipped)"
    elif not outline_shapes(backup):
        note = "backup has no outline (skipped)"
    if not note:
        moves, missing, note = plan_anchors(backup, target)
    if note:
        return Job(glyph, backup, master, target, mask, now, now, width, width, note=note)
    return Job(glyph, backup, master, target, mask, now, contours_in(backup), width, backup.advanceWidth,
               moves, missing)


def survey(package: Any, names: Sequence[str], chosen: str, facts: Any) -> list[Job]:
    """Plan the restore of backup ``chosen`` for every glyph in ``names``. Change nothing."""
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    masters = [str(m) for m in package.masters]
    jobs: list[Job] = []
    for name in names:
        glyph = package.findName(name)
        if glyph is None or glyph.isNull:
            continue
        backup = next((x for x in glyph.layers if str(x.name) == chosen and not x.isMaskLayer), None)
        if backup is None:
            jobs.append(Job(glyph, None, "", None, None, 0, 0, 0, 0, note="no layer with this name"))
            continue
        jobs.append(_plan(glyph, backup, masters, history.refusal(facts, str(glyph.name), "geometry")))
    return jobs


def restore(jobs: Sequence[Job], delete: bool, facts: Any) -> dict[str, Any]:
    """Restore the planned jobs as ONE Undo step; optionally delete the backups.

    Return ``{"layers", "glyphs", "deleted", "kept", "mismatches"}``. A
    backup that is the shown layer, or a locked backup or backup mask, is
    kept and counted. The components of deleted layers are retained in the
    notification (fl#7641). Nothing to do returns
    zeros and makes no history call.
    """
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    from fly import qt

    todo = [j for j in jobs if not j.note]
    if not todo:
        return {"pending_updates": (), "pending_note": "", "layers": 0, "glyphs": 0, "deleted": 0, "kept": 0, "mismatches": []}
    glyphs = list({str(j.glyph.name): j.glyph for j in todo}.values())
    doomed: list[tuple[Any, Any, str]] = []  # (glyph, layer, name): backup, then its mask
    kept = 0
    for job in todo if delete else ():
        active = job.glyph.updateActiveLayer(False)
        shown = _valid(active) and int(active.id) == int(job.backup.id)
        locked = job.backup.isLocked or (job.mask is not None and job.mask.isLocked)
        if shown or locked:
            kept += 1
            continue
        doomed.append((job.glyph, job.backup, str(job.backup.name)))
        if job.mask is not None:
            doomed.append((job.glyph, job.mask, str(job.mask.name)))
    # Read before any removal: a builder read after detachment can be too late (fl#7641).
    retain = [obj for _, layer, _ in doomed for shape in layer.shapes for obj in history.component_history(shape)]

    def mutate() -> None:
        for job in todo:
            replace_outline(job.backup, job.target)
            pins = {str(pin.name): pin for pin in job.target.anchors}
            for name, x, y in job.moves:
                pins[name].point = qt.QtCore.QPointF(x, y)
            if job.width_after != job.width_now:
                job.target.advanceWidth = job.width_after
            job.target.changed()
            if job.target.update() is False:
                raise RuntimeError(f"FontLab could not update '{job.glyph.name}' in '{job.master}'.")
        for glyph, layer, _ in reversed(doomed):  # the mask first, then its backup
            glyph.removeLayer(layer)

    def read_back() -> list[str]:
        found = []
        for job in todo:
            label = f"{job.glyph.name} · {job.master}"
            if contours_in(job.target) != job.contours_after:
                found.append(f"{label}: {contours_in(job.target)} contours, planned {job.contours_after}")
            if job.target.advanceWidth != job.width_after:
                found.append(f"{label}: width {job.target.advanceWidth:g}, planned {job.width_after:g}")
        for glyph, layer, name in doomed:
            if int(layer.id) in {int(x.id) for x in glyph.layers}:
                found.append(f"{glyph.name}: layer '{name}' is still there")
        return found

    done = history.commit(
        TITLE, [j.target for j in todo], glyphs, mutate, operation="geometry", facts=facts, read_back=read_back,
        retain=retain,
    )
    return {"pending_note": done.pending_note, 
        "pending_updates": done.pending_updates,
        "layers": len(todo),
        "glyphs": len(glyphs),
        "deleted": len(doomed),
        "kept": kept,
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

    class RestorePanel(QtGui.QDialog):
        """Backup choice, delete option, preview table, status, buttons."""

        def __init__(self, parent: Any = None) -> None:
            QtGui.QDialog.__init__(self, parent)
            self._connections: list[Any] = []
            self.jobs: list[Job] = []
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
            self.backup = QtGui.QComboBox()
            self.delete_after = QtGui.QCheckBox("Delete the backup layer and its mask after restoring")
            grid.addWidget(QtGui.QLabel("Backup"), 0, 0)
            grid.addWidget(self.backup, 0, 1)
            grid.addWidget(self.delete_after, 1, 1)
            grid.setColumnStretch(1, 1)
            root.addLayout(grid)
            self.table = QtGui.QTableWidget(0, 4)
            self.table.setHorizontalHeaderLabels(["Glyph", "Into master", "Contours", "Width"])
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
            self.apply_button = QtGui.QPushButton("Restore")
            self.apply_button.setDefault(True)
            for button in (self.selection_button, self.close_button, self.apply_button):
                footer.addWidget(button)
            root.addLayout(footer)
            try:
                package = scripting.current_package()
                if package is not None:
                    self.package_id = package.id
                    self.names = scripting.names_selected_names()
                self.fill_backups()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))
            for signal, slot in (
                (self.backup.currentIndexChanged, lambda *a: self.refresh()),
                (self.selection_button.clicked, lambda *a: self.reselect()),
                (self.apply_button.clicked, lambda *a: self.apply()),
                (self.close_button.clicked, lambda *a: self.close()),
            ):
                scripting.connect_guarded(self, signal, slot)
            self.refresh()

        def font_package(self) -> Any:
            """Return the bound font. Refuse a closed or switched font."""
            if self.package_id is None:
                raise ValueError("Open a font and select glyphs. Then run this script again.")
            package = scripting.current_package()
            if package is None or package.id != self.package_id:
                raise ValueError("The font changed. Run this script again.")
            return package

        def fill_backups(self) -> None:
            """List the backup names of the selected glyphs; keep the current choice."""
            package = self.font_package()
            glyphs = [g for g in (package.findName(n) for n in self.names) if g is not None and not g.isNull]
            chosen = self.backup.currentText
            names = backup_names(glyphs, [str(m) for m in package.masters])
            self.backup.blockSignals(True)
            self.backup.clear()
            for name in names:
                self.backup.addItem(name)
            if chosen in names:
                self.backup.setCurrentIndex(names.index(chosen))
            self.backup.blockSignals(False)

        def plan(self) -> list[Job]:
            """Plan from the live font with fresh auto-layer facts."""
            package = self.font_package()
            if not self.names:
                raise ValueError("Select glyphs in the Font window. Then press Use selection.")
            if self.backup.count == 0:
                raise ValueError(NO_BACKUP)
            return survey(package, self.names, self.backup.currentText, history.scan_auto_facts(package))

        def refresh(self) -> None:
            """Recompute the preview. A refusal disables Restore and shows its reason."""
            try:
                self.jobs = self.plan()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.jobs = []
                self.table.setRowCount(0)
                self.apply_button.setEnabled(False)
                (self.status if str(error) == NO_BACKUP else self.subtitle).setText(str(error))
                return
            shown = ", ".join(self.names[:MAX_NAMES]) + (" …" if len(self.names) > MAX_NAMES else "")
            self.subtitle.setText(f"{plural(len(self.names), 'glyph')}: {shown}")
            self.table.setRowCount(len(self.jobs))
            for number, job in enumerate(self.jobs):
                cells = [job.glyph.name, job.note] if job.note else [
                    job.glyph.name, job.master, f"{job.contours_now} → {job.contours_after}",
                    f"{job.width_now:g} → {job.width_after:g}"]
                for column, text in enumerate(cells):
                    item = QtGui.QTableWidgetItem(text)
                    if column > 1:
                        item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                    self.table.setItem(number, column, item)
            todo = [j for j in self.jobs if not j.note]
            self.apply_button.setEnabled(bool(todo))
            self.status.setText(
                f"{plural(len(todo), 'glyph')} will get “{self.backup.currentText}” back · cells read now → after"
                if todo else "Nothing to restore"
            )

        def reselect(self) -> None:
            """Take the glyph selection from the Font window again."""
            self.font_package()
            self.names = scripting.names_selected_names()
            self.fill_backups()
            self.refresh()

        def apply(self) -> None:
            """Plan again from the live font, then write. One Undo step."""
            import fly.ap.edit_guards as result_guards
            try:
                jobs = self.plan()
                facts = history.scan_auto_facts(self.font_package())
                result = restore(jobs, self.delete_after.isChecked(), facts)
                self.fill_backups()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.refresh()
                self.status.setText(str(error))
                return
            self.last_result = result
            self.refresh()
            text = (
                f"Restored {plural(result['layers'], 'master layer')} in {plural(result['glyphs'], 'glyph')}"
            )
            if result["deleted"]:
                text += f" · deleted {plural(result['deleted'], 'layer')}"
            if result["kept"]:
                text += f" · kept {result['kept']} shown backup(s)"
            if result["mismatches"]:
                text += " · did not read back as planned: " + "; ".join(result["mismatches"][:5])
            self.status.setText(result_guards.append_note(text, result))

        def closeEvent(self, event: Any) -> None:
            """Disconnect owned signals, then delete the panel."""
            scripting.close_script_dialog(self, event, KEY)

    return RestorePanel


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
