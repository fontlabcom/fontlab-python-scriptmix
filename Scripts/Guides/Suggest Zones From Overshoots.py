# this_file: Scripts/Guides/Suggest Zones From Overshoots.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Guides · Suggest Zones From Overshoots
"""Suggest alignment zones from the overshoots of H, O, x and o, then apply them.

What it does:
    For each chosen master, measures H and O at the baseline and the cap
    height, and x and o at the x-height. A zone starts at the edge of the flat
    letter (H or x). Its width is the distance that the round letter (O or o)
    passes that edge: upward for the cap-height and x-height zones, downward
    for the baseline zone. The table shows every suggested zone and the zone
    that it replaces. Apply writes the previewed zones of all chosen masters
    as one Undo step. This tool reads the four glyphs and does not edit them.

How it works:
    A suggested zone replaces the existing zone of the same kind at the same
    position; otherwise the zone with the same name; otherwise it is added.
    A replaced zone keeps its name, tags and lock. All other zones stay. The
    zones are written through the shared native zone backend, the route of
    Metrics > Alignment Zones. Apply first measures the four glyphs again and
    refuses when they changed since the preview. The extents come from the
    outline geometry (nodes and exact curve extremes, components placed),
    because FontLab's cached glyph box can be stale after an edit (fl#8575).

Why this design:
    The preview shows the exact zones before any write, and one shared zone
    writer keeps the refusals and the Undo step the same in every zone tool.

How to use:
    Open a font, activate its Font window and run Guides > Suggest Zones From
    Overshoots. Choose the current master or all masters, review the table and
    press Apply. Press Refresh after you edit the glyphs or the zones. Use
    Edit > Undo in the Font window to revert the whole Apply.

Benefit:
    Set zones that match the real overshoots of every master in one reviewed
    step.

Limitations:
    - A missing glyph or layer, or a layer with no height, gives no zone for
      the rules that need it. The status line names them.
    - A glyph whose outline cannot be read (for example a segment with one
      cubic control) is listed as not measured, with the reason; the other
      glyphs are still measured.
    - Stroke thickness is not counted: zones measure the outline.
    - The Undo step is named "Alignment Zones", like the zone panel's.
    - Apply needs the Font window of this font as the active window. It
      refuses while a Glyph window is the active canvas.
    - Apply re-creates every zone guide of a changed master (new ids,
      x-centre 0, font guideline style), as Font Info does.
    - FontLab defect fl#8574: after Edit > Undo or Redo, the metric guides
      show 3 of 9 lines until you reopen the font. The saved file is correct.

Credit:
    Adapted from zones_from_glyphs.py, the author's own FontLab sample,
    Apache-2.0.
"""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from typing import Any, NamedTuple

import fly.ap.alignment_zones as alignment_zones  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.font_history as font_history  # noqa: PLR0402 - same reason
import fly.ap.outline_extent as outline_extent  # noqa: PLR0402 - same reason
import fly.ap.zone_editor as zone_editor  # noqa: PLR0402 - same reason
import fly.ap.zone_native as zone_native  # noqa: PLR0402 - same reason
import fly.ap.zone_rows as zone_rows  # noqa: PLR0402 - same reason
from fly import qt
from fly.ap.scripting import font_info_dialog_type, show_script_dialog
from fly.ap.zone_data import Zone, Zones

QtGui = qt.QtGui

TITLE = "Suggest Zones From Overshoots"
KEY = "zones_from_glyphs"
#: (zone name, flat glyph, round glyph, top zone) in table order.
RULES = (
    ("baseline", "H", "O", False),
    ("x-height", "x", "o", True),
    ("caps", "H", "O", True),
)
#: The glyphs that one master's measurement reads.
GLYPHS = ("H", "O", "x", "o")


class Suggestion(NamedTuple):
    """One measured zone: its name, kind, position and outward width."""

    name: str
    top: bool
    position: int
    width: int


# ---------------------------------------------------------------- core
def overshoot_zone(flat: float, curved: float, top: bool) -> tuple[int, int]:
    """Return ``(position, width)``: the flat edge and the overshoot beyond it."""
    width = curved - flat if top else flat - curved
    return round(flat), max(0, round(width))


def suggestions(extents: Mapping[str, alignment_zones.Extent]) -> list[Suggestion]:
    """Return the zones that the extents of H, O, x and o support, in rule order.

    ``extents`` maps a glyph name to its ``(bottom, top)`` or ``None``. A rule
    whose flat or round glyph is ``None`` or absent gives no zone.
    """
    found = []
    for name, flat, curved, top in RULES:
        pair = extents.get(flat), extents.get(curved)
        if None in pair:
            continue
        edge = 1 if top else 0
        position, width = overshoot_zone(pair[0][edge], pair[1][edge], top)
        found.append(Suggestion(name, top, position, width))
    return found


def missing(extents: Mapping[str, alignment_zones.Extent]) -> list[str]:
    """Return the rule names that ``suggestions`` skips for ``extents``."""
    return [
        name
        for name, flat, curved, _top in RULES
        if extents.get(flat) is None or extents.get(curved) is None
    ]


def _at(position: int) -> Callable[[Zone], bool]:
    """Return a test for a zone whose rounded position is ``position``."""
    return lambda zone: round(zone.position) == position


def _named(name: str) -> Callable[[Zone], bool]:
    """Return a test for a zone called ``name``."""
    return lambda zone: zone.name == name


def merge(zones: Zones, proposed: Sequence[Suggestion]) -> tuple[Zones, list[Zone | None]]:
    """Return ``zones`` with ``proposed`` merged in, and the zone each one replaced.

    A suggestion replaces the zone of its kind at the same position, else the
    one with the same name, else it is added. A replaced zone keeps its name
    and, so, its source identity (tags and lock). A zone is replaced once.
    """
    kinds = {True: list(zones.top), False: list(zones.bottom)}
    replaced: list[Zone | None] = []
    for item in proposed:
        pool = kinds[item.top]
        old = next(
            (z for test in (_at(item.position), _named(item.name)) for z in pool if test(z)),
            None,
        )
        new = Zone(item.position, item.width, item.name)
        if old is not None:
            pool.remove(old)
            new = replace(new, name=old.name or item.name)
            if new.name == old.name:
                new = replace(new, origin=old.origin)
        pool.append(new)
        replaced.append(old)
    return Zones(tuple(kinds[True]), tuple(kinds[False])), replaced


def measure(
    package: Any, master: str, unreadable: dict[str, str] | None = None
) -> dict[str, alignment_zones.Extent]:
    """Return the vertical extent of each of ``GLYPHS`` in ``master``; reads only.

    The extent comes from the outline nodes, not from FontLab's cached
    ``boundingBox``, which can be stale after a node move (fl#8575). A glyph
    whose outline cannot be read gets ``None``; its reason goes into
    ``unreadable`` (glyph name to message) when that dict is given.
    """
    found = {}
    for name in GLYPHS:
        glyph = package.findName(name)
        absent = glyph is None or getattr(glyph, "isNull", False)
        layer = None if absent else glyph.findLayer(master)
        if layer is None or layer.isNull:
            found[name] = None
            continue
        try:
            span = outline_extent.vertical_extent(layer)
        except ValueError as error:
            found[name] = None
            if unreadable is not None:
                unreadable[name] = str(error)
            continue
        found[name] = None if span is None else alignment_zones.extent(span[0], span[1] - span[0])
    return found


def stage(editor: Any, master: str, zones: Zones) -> Any:
    """Return ``editor`` with ``zones`` staged for ``master``."""
    return editor.stage(master, zone_rows.rows(zones), origins=zone_rows.origins(zones))


def preview_row(master: str, item: Suggestion, old: Zone | None) -> list:
    """Return one table row: master, zone, position, signed width and the replaced zone."""
    width = f"+{item.width}" if item.top else f"-{item.width}"
    if old is None:
        return [master, item.name, item.position, width, "nothing: added"]
    label = old.name or "no name"
    return [master, item.name, item.position, width, f"{label} at {round(old.position)}, width {round(old.width)}"]


# ---------------------------------------------------------------- GUI
FontInfoDialog = font_info_dialog_type()


class Dialog(FontInfoDialog):
    """A preview of the suggested zones; Apply writes exactly that preview."""

    def __init__(self, parent: Any = None) -> None:
        """Open the shared preview panel with this tool's controls."""
        FontInfoDialog.__init__(
            self,
            parent,
            title=TITLE,
            subtitle=(
                "Each zone starts at the edge of H or x and covers the overshoot of "
                "O or o. Matching zones are replaced; all other zones are kept."
            ),
            key=KEY,
        )

    def setup(self) -> None:
        """Build the scope and Refresh controls and connect them."""
        self._locked = False
        self._backend = self._editor = self._snapshot = None
        self._measured: dict[str, dict] = {}
        masters = list(self.package.masters) if self.package else []
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.preview_master or '–'})")
        self.scope.addItem(f"All masters ({len(masters)})")
        self.refresh_button = QtGui.QPushButton("Refresh")
        self.form.addWidget(QtGui.QLabel("Masters"), 0, 0)
        self.form.addWidget(self.scope, 0, 1)
        self.form.addWidget(self.refresh_button, 0, 2)
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.refresh_button.clicked, lambda *a: self.refresh())

    def chosen_masters(self) -> list[str]:
        """Return the masters of the chosen scope, in font order."""
        if self.scope.currentIndex:
            return [master.name for master in self._snapshot.masters]
        return [self._snapshot.current_master]

    def refresh(self) -> None:
        """Read the zones, measure the glyphs and show the complete preview."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self._locked:
            raise ValueError("Zones may be partly written; check every master and reopen this tool.")
        if self.package is None:
            return
        self.ensure_font()
        backend = zone_native.backend(self.package_id)
        self._snapshot = backend.capture()
        editor = alignment_zones.Editor(self._snapshot)
        rows, skipped, self._measured = [], [], {}
        for master in self.chosen_masters():
            unreadable: dict[str, str] = {}
            extents = measure(self.package, master, unreadable)
            self._measured[master] = extents
            skipped += [f"{name} in {master} ({reason})" for name, reason in unreadable.items()]
            proposed = suggestions(extents)
            zones, replaced = merge(editor.zones(master), proposed)
            editor = stage(editor, master, zones)
            rows += [preview_row(master, *pair) for pair in zip(proposed, replaced, strict=True)]
            skipped += [f"{name} in {master}" for name in missing(extents)]
        self._editor, self._backend = editor, backend
        self.rows(["Master", "Zone", "Position", "Width", "Replaces"], rows)
        changes = editor.plan()
        note = f" · not measured: {', '.join(skipped)}" if skipped else ""
        same = "" if changes or not rows else " · the zones already match"
        self.status.setText(
            f"{len(rows)} suggested zone{'s' if len(rows) != 1 else ''}{same}{note}"
        )
        self._preview_valid = True
        self.apply_button.setEnabled(bool(changes))

    def apply(self) -> None:
        """Write the previewed zones as one Undo step; refuse a stale preview."""
        self.ensure_preview()
        snapshot, editor = self._snapshot, self._editor
        if any(measure(self.package, m) != e for m, e in self._measured.items()):
            self._preview_valid = False
            raise ValueError("H, O, x or o changed since the preview; press Refresh.")
        try:  # the guard comes before check(), which switches masters
            font_history.require_font_window(self.package)
        except ValueError as error:
            self.status.setText(str(error))
            return
        try:
            self._backend.check(snapshot)
        except ValueError as error:
            self._preview_valid = False
            raise ValueError("The font, its masters or its zones changed; press Refresh.") from error
        changes = editor.plan()
        try:
            after = self._backend.apply(snapshot, changes)
        except ValueError as error:  # every refusal comes before the write
            self.status.setText(str(error))
            return
        except BaseException:  # PartialWriteError, a read-back gap, an interrupt
            self._lock()  # the masters can be partly written
            raise
        try:
            zone_editor.check_result(snapshot, changes, after)
        except Exception:
            self._lock()
            raise
        self._written(changes)

    def _lock(self) -> None:
        """Refuse further previews; the font can hold part of the write."""
        self._locked = True
        self._preview_valid = False

    def _written(self, changes: tuple) -> None:
        """Report a completed write, also when the new preview then fails."""
        zones = sum(len(c.after.top) + len(c.after.bottom) for c in changes)
        self.last_result = {"masters": len(changes), "zones": zones}
        done = f"Wrote the zones of {len(changes)} master{'s' if len(changes) != 1 else ''}"
        self.status.setText(done)
        try:
            self.refresh()
        except Exception as error:  # noqa: BLE001 - keep the success visible
            self.status.setText(f"{done}; the new preview failed: {error}")
            return
        self.status.setText(done)


def main() -> Any:
    """Replace this tool's owned panel using the shared script registry."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
