# this_file: Scripts/Masters/Selection To All Backgrounds.py
# SPDX-License-Identifier: Apache-2.0
"""Copy the selected contours into the background of every glyph.

What it does:
    Take the selected contours of the shown glyph layer. Replace the background
    (mask layer) of the current-master layer of EVERY glyph in the font with
    copies of them. Use it to put one guide shape, such as a grid or a reference
    skeleton, behind all glyphs.

How it works:
    A contour counts as selected when all its nodes are selected (select a
    contour with a double click, or drag a box around it). A panel first
    shows what will happen: contour count, glyph count, backgrounds to be
    replaced and glyphs to be skipped. "Replace backgrounds" checks again that
    nothing changed, then removes the old background shapes, creates missing
    backgrounds, and adds clones of the selected contours. One notification covers
    the whole font: one Undo step. The shared App helper fly.ap.history decides
    which glyphs are skipped and does the one-step write.

Why this design:
    - The change spans the whole font and overwrites backgrounds. So there is a
      preview and an explicit button; there is no silent run.
    - The panel works only on the current master. Other masters keep their
      backgrounds.
    - Glyphs with an automatic layer, glyphs that are a base of one (also
      through manual composites), glyphs with a locked master layer and glyphs
      without a layer for the current master are skipped and counted. An
      automatic layer must never be notified: it would rebuild every automatic
      glyph. In a font with many recipes, most base letters are skipped.
    - FontLab clone() drops shape notes and names and the raw state and name of
      nodes. The script copies them back, except selection bits.
    - Only contours move. Components in the selection are not copied.

How to use:
    Open a Glyph window. Select the contours. Run the script. Read the summary.
    Click "Replace backgrounds". Use Edit > Undo to revert.

Benefit:
    One reference shape behind the whole font in one step.

Credit:
    Behaviour after Pedro Arilla's Glyphs script "Selection to all the
    backgrounds" (Apache-2.0). Independent rewrite. No source code was copied.
    Known limit: clone() recalculates smooth flags (fl#8516); the script
    restores node states.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from time import monotonic
from typing import Any

TITLE = "Selection To All Backgrounds"
KEY = "masters_selection_to_all_backgrounds"
PLAN_SECONDS = 60.0  # reading a big font takes time; this is a GUI-thread guard
WRITE_SECONDS = 120.0
MAX_LISTED = 10  # skipped glyph names shown in the preview


@dataclass(frozen=True)
class Plan:
    """What the script would do. Native handles do not take part in equality."""

    glyph: str
    master: str
    contours: int
    signature: tuple[Any, ...]
    replaced: int
    created: int
    skipped: int
    skipped_names: tuple[str, ...] = ()
    pieces: tuple[tuple[Any, tuple[int, ...]], ...] = field(default=(), compare=False, repr=False)
    targets: tuple[tuple[Any, Any], ...] = field(default=(), compare=False, repr=False)
    facts: Any = field(default=None, compare=False, repr=False)  # App auto-layer facts

    def summary(self) -> str:
        """Return the preview text of the panel."""
        return (
            f"Copy {self.contours} selected contour(s) of '{self.glyph}' into the "
            f"background of {len(self.targets)} glyph(s), master '{self.master}'.\n"
            f"{self.replaced} existing background(s) will be replaced, "
            f"{self.created} will be created. {self.skipped} glyph(s) are skipped "
            "(automatic, locked or missing master layer)."
            + self.skipped_text()
        )

    def skipped_text(self) -> str:
        """Name up to MAX_LISTED skipped glyphs; count the rest."""
        if not self.skipped_names:
            return ""
        shown = ", ".join(self.skipped_names[:MAX_LISTED])
        more = len(self.skipped_names) - MAX_LISTED
        return f"\nSkipped: {shown}" + (f" and {more} more." if more > 0 else ".")


def selected_indexes(contours: Sequence[Sequence[bool]]) -> list[int]:
    """Return the indexes of contours whose nodes are all selected.

    `contours` holds one tuple of node-selected flags per contour.
    A contour without nodes is never selected.
    """
    return [i for i, flags in enumerate(contours) if flags and all(flags)]


SELECTED = 0x0020  # node state bit: selected


def restore_shape(old: Any, new: Any, indexes: Sequence[int]) -> None:
    """Copy back what FontLab's clone() drops (fl#8516, fl#8538).

    Restore shape note and name, and the raw state and name of every node of
    the kept contours `indexes`. Selection bits and shape flags stay as the
    clone has them: a background must not look selected.
    """
    new.shapeData.note, new.shapeData.name = old.shapeData.note, old.shapeData.name
    kept = [list(old.contours)[i] for i in indexes]
    for before, after in zip(kept, new.contours, strict=True):
        for source, target in zip(before.nodes(), after.nodes(), strict=True):
            target.nodeState = (source.nodeState & ~SELECTED) | (target.nodeState & SELECTED)
            target.name = source.name


def _valid(layer: Any) -> bool:
    """True for a real native layer object."""
    return layer is not None and not layer.isNull and layer.isValid


def make_plan() -> Plan:
    """Read the selection and the font. Change nothing. Raise ValueError."""
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    from fly import ap
    from fly.ap.layer_selection import capture
    from fly.ap.scripting import current_package

    deadline = monotonic() + PLAN_SECONDS
    selection = capture(deadline)
    package = current_package()
    if selection.context[2] != "editor" or package is None or not selection.occurrences:
        raise ValueError("Open a Glyph window and select contours first.")
    source = selection.occurrences[0]
    layer = source.layer
    if layer.isMaskLayer or layer.isService:
        raise ValueError("Select contours on a body layer, not on a background.")
    pieces, signature = [], []
    for shape in layer.shapes:
        if shape.isComponent:
            continue
        flags = [tuple(bool(n.selected) for n in c.nodes()) for c in shape.contours]
        keep = selected_indexes(flags)
        if keep:
            pieces.append((shape, tuple(keep)))
            signature.append((int(shape.id), tuple(keep)))
    if not pieces:
        raise ValueError("No fully selected contour. Select whole contours first.")
    master = str(package.master)
    facts = history.scan_auto_facts(package)
    targets, replaced, created, skipped = [], 0, 0, []
    for record in ap.fontlab.CurrentFont().glyphs:
        if monotonic() >= deadline:
            raise ValueError("Reading the font took too long; try again.")
        glyph = package.findName(record.name)
        target = None if glyph is None or glyph.isNull else glyph.findLayer(master)
        if (
            not _valid(target)
            or target.isLocked
            or history.refusal(facts, str(glyph.name), "geometry")
            or any(x.autoLayer for x in glyph.layers)
        ):
            skipped.append(str(record.name))
            continue
        if _valid(target.getMaskLayer(False)):
            replaced += 1
        else:
            created += 1
        targets.append((glyph, target))
    if not targets:
        raise ValueError(f"No glyph has a usable layer for master '{master}'.")
    return Plan(
        glyph=source.glyph_name,
        master=master,
        contours=sum(len(keep) for _, keep in pieces),
        signature=(int(source.glyph_id), int(source.layer_id), tuple(signature), master,
                   tuple(int(g.id) for g, _ in targets)),
        replaced=replaced,
        created=created,
        skipped=len(skipped),
        skipped_names=tuple(skipped),
        pieces=tuple(pieces),
        targets=tuple(targets),
        facts=facts,
    )


def selected_clone(shape: Any, keep: Sequence[int]) -> Any:
    """Clone `shape` and remove every contour that is not in `keep`."""
    clone = shape.clone()
    for index, contour in reversed(list(enumerate(tuple(clone.contours)))):
        if index not in keep:
            clone.removeContour(contour)
    if len(clone.contours) != len(keep):
        raise RuntimeError("FontLab changed the contour count while cloning.")
    restore_shape(shape, clone, keep)
    return clone


def replace_backgrounds(shown: Plan) -> str:
    """Apply `shown` after proof that the font and selection still match it."""
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    current = make_plan()
    if current.signature != shown.signature:
        raise ValueError("The selection or the font changed. Close the panel and run again.")
    deadline = monotonic() + WRITE_SECONDS
    existing, owners = [], [glyph for glyph, _ in current.targets]
    for _, target in current.targets:
        mask = target.getMaskLayer(False)
        if _valid(mask):
            existing.append(mask)

    def mutate() -> Sequence[Any]:
        made = []
        for glyph, target in current.targets:
            if monotonic() >= deadline:
                raise RuntimeError(f"Stopped at '{glyph.name}': time limit reached.")
            mask = target.getMaskLayer(False)
            if _valid(mask):
                mask.removeAllShapes()
            else:
                mask = target.getMaskLayer(True)
                if not _valid(mask):
                    raise RuntimeError(f"FontLab could not create a background for '{glyph.name}'.")
                made.append(mask)
            for shape, keep in current.pieces:
                mask.addShape(selected_clone(shape, keep))
            mask.changed()
            if mask.update() is False:
                raise RuntimeError(f"FontLab could not update the background of '{glyph.name}'.")
        return made

    history.commit(TITLE, existing, owners, mutate, operation="geometry", facts=current.facts)
    return f"Background set in {len(owners)} glyph(s)."


def muted(widget: Any, QtGui: Any) -> str:
    """CSS colour for secondary text in the current palette."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


def panel_type(QtGui: Any) -> Any:
    """Build the preview panel class once Qt is available."""
    from fly import ap

    class Panel(QtGui.QDialog):
        """Preview text, one action button, one status line."""

        def __init__(self, parent: Any = None) -> None:
            QtGui.QDialog.__init__(self, parent)
            self._connections: list[Any] = []
            self.plan: Plan | None = None
            self.setWindowTitle(TITLE)
            self.setMinimumWidth(460)
            root = QtGui.QVBoxLayout(self)
            root.setContentsMargins(20, 18, 20, 16)
            root.setSpacing(12)
            heading = QtGui.QLabel(TITLE)
            font = heading.font
            font.setPointSizeF(font.pointSizeF() * 1.35)
            font.setBold(True)
            heading.setFont(font)
            root.addWidget(heading)
            self.preview = QtGui.QLabel("")
            self.preview.setWordWrap(True)
            root.addWidget(self.preview)
            self.status = QtGui.QLabel("")
            self.status.setWordWrap(True)
            self.status.setStyleSheet(f"color: {muted(self, QtGui)};")
            root.addWidget(self.status)
            row = QtGui.QHBoxLayout()
            self.go = QtGui.QPushButton("Replace backgrounds")
            self.refresh_button = QtGui.QPushButton("Refresh")
            self.close_button = QtGui.QPushButton("Close")
            for button in (self.go, self.refresh_button, self.close_button):
                row.addWidget(button)
            root.addLayout(row)
            ap.scripting.connect_guarded(self, self.go.clicked, lambda *a: self.replace())
            ap.scripting.connect_guarded(self, self.refresh_button.clicked, lambda *a: self.refresh())
            ap.scripting.connect_guarded(self, self.close_button.clicked, lambda *a: self.close())
            self.refresh()

        def refresh(self) -> None:
            """Read the selection again and show what a click would do."""
            try:
                self.plan = make_plan()
                self.preview.setText(self.plan.summary())
                self.status.setText("")
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.plan = None
                self.preview.setText("")
                self.status.setText(str(error))
            self.go.setEnabled(self.plan is not None)

        def replace(self) -> None:
            """Apply the previewed plan once."""
            if self.plan is None:
                return
            shown, self.plan = self.plan, None
            self.go.setEnabled(False)  # one attempt per preview, even after a failure
            try:
                self.status.setText(replace_backgrounds(shown))
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

        def closeEvent(self, event: Any) -> None:
            """Release owned signals and delete the panel."""
            ap.scripting.close_script_dialog(self, event, KEY)

    return Panel


def main() -> Any:
    """Open the preview panel (one instance, reused through the shared registry)."""
    from fly import ap, qt

    return ap.scripting.show_script_dialog(panel_type(qt.QtGui), KEY)


if __name__ == "__main__":
    main()
