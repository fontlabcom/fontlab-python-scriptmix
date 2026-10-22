# this_file: Scripts/Masters/Selection To All Backgrounds.py
# SPDX-License-Identifier: Apache-2.0
"""Copy the selected contours into the background of every glyph.

What it does:
    Take the selected contours of the shown glyph layer. Replace the background
    (mask layer) of the current-master layer of EVERY glyph in the font with
    copies of them. Use it to put one guide shape, such as a grid or a
    reference
    skeleton, behind all glyphs.

How it works:
    A contour counts as selected when all its nodes are selected (select a
    contour with a double click, or drag a box around it). A panel first
    shows what will happen: contour count, glyph count, backgrounds to be
    replaced and glyphs to be skipped. The panel stays open. Switch to the
    Font window, then press "Replace backgrounds". It reads the planned
    contours and the font again and stops if anything changed. Then it
    removes the old background shapes, creates missing backgrounds, and adds
    clones of the selected contours. One notification covers the whole
    font: one Undo step in the Font window. The shared module
    fly.ap.history decides which glyphs
    are skipped and does the one-step write. Read-back checks every target
    background for the planned contour count and no components. A mismatch
    is reported with the Edit > Undo hint.

Why this design:
    - The change spans the whole font and overwrites backgrounds. So there is a
      preview and an explicit button; there is no silent run.
    - The write runs only while the Font window is active. While a Glyph
      window is active, FontLab records the Undo step for the shown glyph
      only: Edit > Undo then restores that glyph and leaves the other
      backgrounds changed (measured on FontLab 9.0.9790). Edit > Undo in a
      Glyph window after the write also undoes only the shown glyph.
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
    Switch to the Font window. Click "Replace backgrounds". Use Edit > Undo in
    the Font window to revert.

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
FONT_WINDOW = (
    "Switch to the Font window, then press Replace backgrounds. From a Glyph "
    "window, FontLab would undo only the shown glyph."
)


class WrongWindow(ValueError):
    """The write was refused because the Font window is not active. Keep the plan."""


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
            + "\nSwitch to the Font window, then press Replace backgrounds."
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


def _valid(layer: Any) -> bool:
    """True for a real native layer object."""
    return layer is not None and not layer.isNull and layer.isValid


def make_plan() -> Plan:
    """Read the selection of the Glyph window and the font. Change nothing. Raise ValueError."""
    from fly.ap.layer_selection import capture
    from fly.ap.scripting import current_package

    deadline = monotonic() + PLAN_SECONDS
    selection = capture(deadline)
    package = current_package()
    if selection.context[2] != "editor" or package is None or not selection.occurrences:
        raise ValueError("Open a Glyph window and select contours first.")
    source = selection.occurrences[0]
    return plan_for(package, source.glyph, source.layer, deadline)


def replan(shown: Plan) -> Plan:
    """Read the planned contours of `shown` and the font again. Change nothing.

    Works in any window. The Glyph window shows the source layer through
    another wrapper (another id and its own node selection), so the source
    layer is found by glyph and layer name, and the contours by the planned
    shape and contour indexes. Their node coordinates and types are part of
    the signature: an edited source no longer matches. Raise ValueError when
    the font, the source glyph or its layer is gone.
    """
    from fly.ap.scripting import current_package

    changed = ValueError("The selection or the font changed. Close the panel and run again.")
    package = current_package()
    if package is None or int(package.id) != shown.signature[0]:
        raise changed
    glyph = package.findName(shown.glyph)
    if glyph is None or glyph.isNull or int(glyph.id) != shown.signature[1]:
        raise changed
    layer = next((x for x in glyph.layers if str(x.name) == shown.signature[2]), None)
    if layer is None:
        raise changed
    chosen = {index: keep for index, _, keep, _ in shown.signature[3]}
    return plan_for(package, glyph, layer, monotonic() + PLAN_SECONDS, chosen)


def outline(contour: Any) -> tuple[Any, ...]:
    """Node coordinates and types of a contour, for the plan signature."""
    return tuple((round(float(n.x), 3), round(float(n.y), 3), str(n.type)) for n in contour.nodes())


def plan_for(
    package: Any, glyph: Any, layer: Any, deadline: float, chosen: dict[int, tuple[int, ...]] | None = None,
) -> Plan:
    """Plan from contours of `layer` (in `glyph`). Change nothing. Raise ValueError.

    Without `chosen`, take the fully selected contours. With `chosen`
    ({shape index: contour indexes}), take those contours.
    """
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    from fly import ap

    if layer.isMaskLayer or layer.isService:
        raise ValueError("Select contours on a body layer, not on a background.")
    pieces, signature = [], []
    for index, shape in enumerate(layer.shapes):
        if shape.isComponent:
            continue
        contours = list(shape.contours)
        if chosen is None:
            keep = selected_indexes([tuple(bool(n.selected) for n in c.nodes()) for c in contours])
        else:
            keep = [i for i in chosen.get(index, ()) if i < len(contours)]
        if keep:
            pieces.append((shape, tuple(keep)))
            signature.append((index, len(contours), tuple(keep), tuple(outline(contours[i]) for i in keep)))
    if not pieces:
        raise ValueError("No fully selected contour. Select whole contours first.")
    master = str(package.master)
    facts = history.scan_auto_facts(package)
    targets, replaced, created, skipped = [], 0, 0, []
    for record in ap.fontlab.CurrentFont().glyphs:
        if monotonic() >= deadline:
            raise ValueError("Reading the font took too long; try again.")
        other = package.findName(record.name)
        target = None if other is None or other.isNull else other.findLayer(master)
        if (
            not _valid(target)
            or target.isLocked
            or history.refusal(facts, str(other.name), "geometry")
            or any(x.autoLayer for x in other.layers)
        ):
            skipped.append(str(record.name))
            continue
        if _valid(target.getMaskLayer(False)):
            replaced += 1
        else:
            created += 1
        targets.append((other, target))
    if not targets:
        raise ValueError(f"No glyph has a usable layer for master '{master}'.")
    return Plan(
        glyph=str(glyph.name),
        master=master,
        contours=sum(len(keep) for _, keep in pieces),
        signature=(int(package.id), int(glyph.id), str(layer.name), tuple(signature), master,
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
    import fly.ap.contour_copy as contour_copy

    clone = shape.clone()
    for index, contour in reversed(list(enumerate(tuple(clone.contours)))):
        if index not in keep:
            clone.removeContour(contour)
    if len(clone.contours) != len(keep):
        raise RuntimeError("FontLab changed the contour count while cloning.")
    contour_copy.restore_shape(shape, clone, indexes=keep)
    return clone


def replace_backgrounds(shown: Plan, *, disclosure: dict[str, Any] | None = None) -> str:
    """Apply `shown` after proof that the font and selection still match it.

    Raise WrongWindow (a ValueError) before reading the font when the Font
    window of the font is not active.
    """
    import fly.ap.edit_guards as guards
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    try:
        guards.require_selection_window(shown.signature[0])
    except ValueError as error:
        raise WrongWindow(FONT_WINDOW) from error
    current = replan(shown)
    if current.signature != shown.signature:
        raise ValueError("The selection or the font changed. Close the panel and run again.")
    deadline = monotonic() + WRITE_SECONDS
    existing, owners = [], [glyph for glyph, _ in current.targets]
    for _, target in current.targets:
        mask = target.getMaskLayer(False)
        if _valid(mask):
            existing.append(mask)

    retain = [obj for mask in existing for shape in mask.shapes
              for obj in history.component_history(shape)]

    def mutate() -> Sequence[Any]:
        made = []
        for glyph, target in current.targets:
            if monotonic() >= deadline:
                raise RuntimeError(f"Stopped at '{glyph.name}': time limit reached.")
            mask = target.getMaskLayer(False)
            if _valid(mask):
                for old in list(mask.shapes):
                    mask.removeShape(old)
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

    def read_back() -> list[str]:
        mismatches = []
        for glyph, target in current.targets:
            mask = target.getMaskLayer(False)
            if not _valid(mask):
                mismatches.append(f"{glyph.name}: missing background")
                continue
            contours = sum(len(shape.contours) for shape in mask.shapes if not shape.isComponent)
            if contours != current.contours:
                mismatches.append(f"{glyph.name}: background has {contours} contours, planned {current.contours}")
            components = sum(1 for shape in mask.shapes if shape.isComponent)
            if components:
                mismatches.append(f"{glyph.name}: background still has {components} component(s), planned 0")
        return mismatches

    done = history.commit(
        TITLE, existing, owners, mutate, operation="geometry", facts=current.facts,
        retain=retain, read_back=read_back,
    )
    import fly.ap.edit_guards as _guards
    _guards.disclose(done, disclosure)
    if done.mismatches:
        raise history.unstored_error(done.mismatches, history.UNDO_HINT)
    return _guards.append_note(f"Background set in {len(owners)} glyph(s).", done)


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
            """Read the selection again and show what a click would do.

            Outside a Glyph window, re-read the planned contours of the last plan.
            """
            previous = self.plan
            try:
                try:
                    self.plan = make_plan()
                except ValueError:
                    if previous is None:
                        raise
                    self.plan = replan(previous)
                self.preview.setText(self.plan.summary())
                self.status.setText("")
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.plan = None
                self.preview.setText("")
                self.status.setText(str(error))
            self.go.setEnabled(self.plan is not None)

        def replace(self) -> None:
            """Apply the previewed plan once."""
            import fly.ap.edit_guards as result_guards
            disclosure = {"pending_updates": (), "pending_note": ""}
            if self.plan is None:
                return
            shown, self.plan = self.plan, None
            self.go.setEnabled(False)  # one attempt per preview, even after a failure
            try:
                self.status.setText(result_guards.append_note(replace_backgrounds(shown, disclosure=disclosure), disclosure))
            except WrongWindow as error:  # nothing was read or written: keep the preview
                self.plan = shown
                self.go.setEnabled(True)
                self.status.setText(str(error))
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(result_guards.append_note(str(error), disclosure))

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
