# this_file: Scripts/Masters/Copy Layer Between Masters.py
# SPDX-License-Identifier: Apache-2.0
"""Copy the outline, anchors and advance width from one master to others.

What it does:
    For each selected glyph, replace the contours of the target master
    layers with copies of the contours of the source master layer.
    Optionally move same-named anchors to the source positions and set the
    source advance width. Components of the targets stay; components of
    the source are not copied.

How it works:
    A non-modal panel has a "From" master, checked target masters, and two
    options: Anchors and Advance width. The table
    shows, per target layer, contours now and after, width now and after.
    Copy reads the font again and writes every target in one Undo step
    through the shared module fly.ap.history. The old outline shapes of a
    target are removed (empty ones too) and repaired clones of the source
    outline shapes are added. After the write the script reads contour
    counts, widths and anchor positions back and reports any difference.

Why this design:
    - The target loses its outline shapes, it never edits them. A shape that
      other glyphs share stays intact for them.
    - FontLab clone() drops shape notes and names and the raw state and name
      of nodes (fl#8516, fl#8538). The script copies them back, clears
      selection bits, and stops when a clone has another contour count.
    - Only same-named anchors move; missing anchors are listed, never added.
      Two anchors with one name make the layer ambiguous: it is skipped. An
      existing anchor that would move to 0, 0 is skipped too: FontLab does
      not Redo that move (fl#8527).
    - Skipped and listed: automatic layers, glyphs with automatic layers,
      bases of automatic composites (also through manual composites),
      locked layers, layers with a metrics link or expression, and a source
      without outline. Apply discloses queued ids and their possible date
      changes. The panel binds to the font that was current when it opened.

How to use:
    Select glyphs in the Font window. Run the script. Pick the source master
    and the targets. Changing the source checks all other masters again.
    Check the table. Press Copy. Then check the masters for
    compatibility: the targets now have the point structure of the source.

Benefit:
    Start the outlines of a new master from an existing one, or resync the
    outlines of a broken master, in
    one step and one Undo.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (masters_copy_layer.py, "Copy Layer Between Masters").
    Known limit: node.clone loses explicit corner smoothness and other
    scalar node properties (fl#8569); a shape clone may lose them too.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

TITLE = "Copy Layer Between Masters"
KEY = "masters_copy_layer"
LINK_FIELDS = ("metricsLeft", "metricsRight", "metricsWidth")
MAX_NAMES = 8  # glyph names shown in the subtitle

Move = tuple[str, float, float]


@dataclass(frozen=True)
class Pair:
    """One source/target layer pair and its plan.

    ``moves``: (anchor name, x, y) for each target anchor that moves.
    ``missing``: source anchor names the target lacks. ``note`` is empty for
    a pair that will be copied; else it says why the pair is skipped.
    """

    glyph: Any
    master: str
    source: Any
    target: Any
    contours_now: int
    contours_after: int
    width_now: float
    width_after: float
    moves: tuple[Move, ...] = ()
    missing: tuple[str, ...] = ()
    note: str = ""


def _valid(layer: Any) -> bool:
    """True for a real native layer object."""
    return layer is not None and not layer.isNull


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
    """Return (moves, missing names, problem) for same-named anchors.

    ``problem`` is empty, or says why the layer must be skipped.
    """
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


def plan_pair(glyph: Any, master: str, source: Any, target: Any, anchors: bool, width: bool, reason: str) -> Pair:
    """Plan one pair. ``reason`` is the geometry refusal of the glyph, or ""."""
    now, after = contours_in(target), contours_in(source)
    base = Pair(glyph, master, source, target, now, after, target.advanceWidth,
                source.advanceWidth if width else target.advanceWidth)
    note = ""
    if source.autoLayer or target.autoLayer:
        note = "auto layer (skipped)"
    elif reason:
        note = f"{reason} (skipped)"
    elif target.isLocked:
        note = "locked layer (skipped)"
    elif has_metrics_link(target):
        note = "metrics link or expression (skipped)"
    elif not outline_shapes(source):
        note = "source has no outline (skipped)"
    if note:
        return Pair(glyph, master, source, target, now, now, target.advanceWidth, target.advanceWidth, note=note)
    if not anchors:
        return base
    moves, missing, problem = plan_anchors(source, target)
    if problem:
        return Pair(glyph, master, source, target, now, now, target.advanceWidth, target.advanceWidth, note=problem)
    return Pair(base.glyph, master, source, target, now, after, base.width_now, base.width_after, moves, missing)


def survey(
    package: Any, names: Sequence[str], source_master: str, targets: Sequence[str],
    anchors: bool, width: bool, facts: Any,
) -> list[Pair]:  # fmt: skip
    """Plan every glyph and target master. Change nothing.

    A glyph without a source layer or without a target layer gives no row.
    """
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    pairs: list[Pair] = []
    for name in names:
        glyph = package.findName(name)
        if glyph is None or glyph.isNull:
            continue
        source = glyph.findLayer(source_master)
        if not _valid(source):
            continue
        reason = history.refusal(facts, str(glyph.name), "geometry")
        for master in targets:
            target = glyph.findLayer(master)
            if master != source_master and _valid(target):
                pairs.append(plan_pair(glyph, master, source, target, anchors, width, reason))
    return pairs


def copy_pairs(pairs: Sequence[Pair], facts: Any) -> dict[str, Any]:
    """Write the planned pairs as ONE Undo step and read them back.

    Return ``{"layers", "glyphs", "contours", "missing", "mismatches"}``.
    Nothing to do returns zeros and makes no history call. A refusal raises
    ValueError; a failure after history started raises RuntimeError with
    the Undo hint.
    """
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    from fly import qt

    todo = [p for p in pairs if not p.note]
    missing = sorted({n for p in todo for n in p.missing})
    if not todo:
        return {"pending_updates": (), "pending_note": "", "layers": 0, "glyphs": 0, "contours": 0, "missing": missing, "mismatches": []}
    glyphs = list({str(p.glyph.name): p.glyph for p in todo}.values())

    def mutate() -> None:
        for pair in todo:
            replace_outline(pair.source, pair.target)
            pins = {str(pin.name): pin for pin in pair.target.anchors}
            for name, x, y in pair.moves:
                pins[name].point = qt.QtCore.QPointF(x, y)
            if pair.width_after != pair.width_now:
                pair.target.advanceWidth = pair.width_after
            pair.target.changed()
            if pair.target.update() is False:
                raise RuntimeError(f"FontLab could not update '{pair.glyph.name}' in '{pair.master}'.")

    def read_back() -> list[str]:
        found = []
        for pair in todo:
            label = f"{pair.glyph.name} · {pair.master}"
            count = contours_in(pair.target)
            if count != pair.contours_after:
                found.append(f"{label}: {count} contours, planned {pair.contours_after}")
            if pair.target.advanceWidth != pair.width_after:
                found.append(f"{label}: width {pair.target.advanceWidth:g}, planned {pair.width_after:g}")
            stored = {str(pin.name): _point(pin) for pin in pair.target.anchors}
            found.extend(
                f"{label}: anchor {name} at {stored.get(name)}, planned {(x, y)}"
                for name, x, y in pair.moves
                if stored.get(name) != (x, y)
            )
        return found

    done = history.commit(
        TITLE, [p.target for p in todo], glyphs, mutate, operation="geometry", facts=facts, read_back=read_back
    )
    return {"pending_note": done.pending_note, 
        "pending_updates": done.pending_updates,
        "layers": len(todo),
        "glyphs": len(glyphs),
        "contours": sum(p.contours_after for p in todo),
        "missing": missing,
        "mismatches": list(done.mismatches),
    }


def plural(count: int, word: str) -> str:
    """Return "1 layer" or "2 layers"."""
    return f"{count} {word}{'' if count == 1 else 's'}"


def panel_type() -> type:
    """Build the panel class once Qt is available (inside FontLab)."""
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.scripting as scripting  # noqa: PLR0402
    from fly import qt

    QtGui, QtCore = qt.QtGui, qt.QtCore

    class CopyLayerPanel(QtGui.QDialog):
        """From, To, options, preview table, status, Use selection, Close, Copy."""

        def __init__(self, parent: Any = None) -> None:
            QtGui.QDialog.__init__(self, parent)
            self._connections: list[Any] = []
            self.pairs: list[Pair] = []
            self.names: list[str] = []
            self.masters: list[str] = []
            self.package_id: int | None = None
            self.last_result: dict[str, Any] = {}
            self.setWindowTitle(TITLE)
            self.setMinimumWidth(560)
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
            self.source = QtGui.QComboBox()
            self.target_checks: dict[str, Any] = {}
            self.targets_scroll = QtGui.QScrollArea()
            self.targets_scroll.setWidgetResizable(True)
            self.targets_scroll.setMaximumHeight(150)
            targets_widget = QtGui.QWidget()
            self.targets_box = QtGui.QVBoxLayout(targets_widget)
            self.targets_scroll.setWidget(targets_widget)
            self.anchors = QtGui.QCheckBox("Anchors")
            self.anchors.setChecked(True)
            self.copy_width = QtGui.QCheckBox("Advance width")
            self.copy_width.setChecked(True)
            grid.addWidget(QtGui.QLabel("From"), 0, 0)
            grid.addWidget(self.source, 0, 1, 1, 2)
            grid.addWidget(QtGui.QLabel("To"), 1, 0)
            grid.addWidget(self.targets_scroll, 1, 1, 1, 2)
            grid.addWidget(QtGui.QLabel("Also"), 2, 0)
            grid.addWidget(self.anchors, 2, 1)
            grid.addWidget(self.copy_width, 2, 2)
            grid.setColumnStretch(2, 1)
            root.addLayout(grid)
            self.table = QtGui.QTableWidget(0, 5)
            self.table.setHorizontalHeaderLabels(
                ["Glyph · target", "Contours now", "Contours after", "Width now", "Width after"]
            )
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
            try:
                package = scripting.current_package()
                if package is not None:
                    self.package_id = package.id
                    self.masters = [str(m) for m in package.masters]
                    self.names = scripting.names_selected_names()
                    for master in self.masters:
                        self.source.addItem(master)
                    if str(package.master) in self.masters:
                        self.source.setCurrentIndex(self.masters.index(str(package.master)))
                    for master in self.masters:
                        check = QtGui.QCheckBox(master)
                        check.setChecked(master != self.source.currentText)
                        self.target_checks[master] = check
                        self.targets_box.addWidget(check)
                        scripting.connect_guarded(self, check.toggled, lambda *a: self.refresh())
                    self.fill_targets()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))
            for signal, slot in (
                (self.source.currentIndexChanged, lambda *a: self.source_changed()),
                (self.anchors.toggled, lambda *a: self.refresh()),
                (self.copy_width.toggled, lambda *a: self.refresh()),
                (self.selection_button.clicked, lambda *a: self.reselect()),
                (self.apply_button.clicked, lambda *a: self.apply()),
                (self.close_button.clicked, lambda *a: self.close()),
            ):
                scripting.connect_guarded(self, signal, slot)
            self.refresh()

        def fill_targets(self) -> None:
            """Disable the source checkbox; preserve the other checked choices."""
            for master, check in self.target_checks.items():
                source = master == self.source.currentText
                check.setEnabled(not source)

        def source_changed(self) -> None:
            """A source master cannot also be a target."""
            for check in self.target_checks.values():
                check.blockSignals(True)
                check.setChecked(True)
                check.blockSignals(False)
            self.fill_targets()
            self.refresh()

        def chosen_targets(self) -> list[str]:
            """Return the checked subset, in font order, excluding the source."""
            return [master for master, check in self.target_checks.items()
                    if master != self.source.currentText and check.isChecked()]

        def font_package(self) -> Any:
            """Return the bound font. Refuse a closed or switched font."""
            if self.package_id is None:
                raise ValueError("Open a font and select glyphs. Then run this script again.")
            package = scripting.current_package()
            if package is None or package.id != self.package_id:
                raise ValueError("The font changed. Run this script again.")
            return package

        def plan(self) -> list[Pair]:
            """Plan from the live font with fresh auto-layer facts."""
            package = self.font_package()
            if not self.names:
                raise ValueError("Select glyphs in the Font window. Then press Use selection.")
            return survey(package, self.names, self.source.currentText, self.chosen_targets(),
                          self.anchors.isChecked(), self.copy_width.isChecked(),
                          history.scan_auto_facts(package))

        def refresh(self) -> None:
            """Recompute the preview. A refusal disables Copy and shows its reason."""
            try:
                self.pairs = self.plan()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.pairs = []
                self.table.setRowCount(0)
                self.subtitle.setText(str(error))
                self.apply_button.setEnabled(False)
                return
            shown = ", ".join(self.names[:MAX_NAMES]) + (" …" if len(self.names) > MAX_NAMES else "")
            self.subtitle.setText(f"{plural(len(self.names), 'glyph')}: {shown}")
            self.table.setRowCount(len(self.pairs))
            for number, pair in enumerate(self.pairs):
                label = f"{pair.glyph.name} · {pair.master}"
                cells = [label, pair.note] if pair.note else [
                    label, str(pair.contours_now), str(pair.contours_after),
                    f"{pair.width_now:g}", f"{pair.width_after:g}"]
                for column, text in enumerate(cells):
                    item = QtGui.QTableWidgetItem(text)
                    if column:
                        item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                    self.table.setItem(number, column, item)
            todo = [p for p in self.pairs if not p.note]
            self.apply_button.setEnabled(bool(todo))
            self.status.setText(
                f"{plural(len(todo), 'layer')} will be replaced from {self.source.currentText}"
                if todo else "Nothing to copy"
            )

        def reselect(self) -> None:
            """Take the glyph selection from the Font window again."""
            self.font_package()
            self.names = scripting.names_selected_names()
            self.refresh()

        def apply(self) -> None:
            """Plan again from the live font, then write. One Undo step."""
            import fly.ap.edit_guards as result_guards
            try:
                pairs = self.plan()
                result = copy_pairs(pairs, history.scan_auto_facts(self.font_package()))
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.refresh()
                self.status.setText(str(error))
                return
            self.last_result = result
            self.refresh()
            text = f"Replaced {plural(result['layers'], 'layer')} in {plural(result['glyphs'], 'glyph')}"
            if result["missing"]:
                text += " · anchors missing in targets: " + ", ".join(result["missing"])
            if result["mismatches"]:
                text += " · did not read back as planned: " + "; ".join(result["mismatches"][:5])
            self.status.setText(result_guards.append_note(text, result))

        def closeEvent(self, event: Any) -> None:
            """Disconnect owned signals, then delete the panel."""
            scripting.close_script_dialog(self, event, KEY)

    return CopyLayerPanel


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
