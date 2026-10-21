# this_file: Scripts/Names/Mark Color Palette.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from the archived Apache-2.0 FontLab samples
# (rescued/samples/names_mark_color_palette.py); provenance in NOTICE.
# FLM: Names · Mark Color Palette
"""Click a colour swatch to mark the selected glyphs with that colour.

WHAT: A non-modal panel shows ten swatches (none, eight hues, grey). Each
swatch shows how many glyphs in the font, and in the selection, carry that
mark. One click writes the mark to every selected glyph.

HOW: FontLab stores a mark as hue + 1 (1 to 360), grey as 1000 + level, and 0
for none. The script rescans the font, plans the change, and writes it as one
Undo step with the App history order (see commit). It then reads each mark
back and compares it with the plan.

WHY: FontLab rebuilds all auto layers when an auto layer is notified. Undo
does not restore the rebuilt layers. So the script REFUSES glyphs that own an
auto layer and never puts an auto layer in the notify list. A base glyph of
an auto composite may be marked: its mark does not reach the composites
(native check pending). The script never reads flGlyph.fgGlyph, never calls
UpdateAll (fl#8537) and refuses to write when native updates are pending.
Swatch colours come from plain HLS arithmetic, so the colour logic works and
is testable without Qt.

USE: Select glyphs in the Font window. Run the script. Click a swatch. Press
Reload selection after you change the selection.

BENEFIT: Colour marks sort work (done, check, kerning needed) and show in the
Font window. One Edit > Undo reverts one click.

Credit: archived Apache-2.0 FontLab samples. Native acceptance pending.
"""

import colorsys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

TITLE = "Mark Color Palette"
KEY = "names_mark_color_palette"
PRESETS: list[tuple[str, int]] = [
    ("None", 0),
    ("Red", 1),
    ("Orange", 31),
    ("Yellow", 56),
    ("Green", 121),
    ("Teal", 171),
    ("Blue", 211),
    ("Purple", 271),
    ("Pink", 321),
    ("Grey", 1128),
]
LIGHTNESS = 150  # of 255; the lightness FontLab uses for mark colours
SATURATION = 200  # of 255


# ------------------------------------------------------------------ shared
# This block is identical in all seven Names editors. Reason: each menu script
# stays one file. A shared App helper could replace it later.
@dataclass(frozen=True)
class Entry:
    """One glyph. RECORD is the FontGate glyph (rename, Unicode). GLYPH is the FontLab glyph."""

    name: str
    record: Any
    glyph: Any


@dataclass(frozen=True)
class Facts:
    """Whole-font snapshot. Never patched: a stale snapshot is rescanned."""

    package: Any
    package_id: int
    entries: dict[str, Entry]
    autos: frozenset[str]
    bases: dict[str, tuple[str, ...]]


def scan(native: Any) -> Facts:
    """Read every glyph and every auto-layer dependency of the current font.

    Use font-owned records and package.findFgId. Never read flGlyph.fgGlyph:
    on build 9784 that getter can clear a fresh note mirror.
    """
    package = native.flWorkspace.instance().currentPackage
    font = native.CurrentFont()
    if package is None or package.isNull or font is None:
        raise ValueError("Open a font first.")
    entries: dict[str, Entry] = {}
    autos: set[str] = set()
    users: dict[str, set[str]] = {}
    for record in font.glyphs:
        glyph = package.findFgId(int(record.id))
        if (
            glyph is None
            or glyph.isNull
            or glyph.name != record.name
            or int(glyph.fgGlyphId) != int(record.id)
        ):
            raise ValueError("Native glyph mapping is inconsistent; reload the font.")
        entries[str(record.name)] = Entry(str(record.name), record, glyph)
        for layer in glyph.layers:
            if not layer.autoLayer:
                continue
            autos.add(str(record.name))
            for shape in layer.shapes:
                if shape.isComponent:
                    base = str(shape.shapeData.componentGlyph)
                    users.setdefault(base, set()).add(str(record.name))
    bases = {base: tuple(sorted(names)) for base, names in users.items()}
    return Facts(package, int(package.id), entries, frozenset(autos), bases)


def refusal(facts: Facts, name: str, *, bases: bool = True) -> str:
    """Return why NAME must not be edited, or "" when it may be.

    FontLab rebuilds every auto layer when an auto layer or the base of an
    auto composite is notified, and Undo does not restore the result.
    Glyphs that own an auto layer are always refused. With BASES false, a base
    of an auto composite is allowed: use that for metadata (tags, marks, notes)
    that does not reach the composites. Renames and Unicode keep BASES true.
    """
    entry = facts.entries.get(name)
    if entry is None:
        return "not in font"
    if not tuple(entry.glyph.layers):
        return "has no layers"
    if name in facts.autos:
        return "has auto layers"
    users = facts.bases.get(name)
    if bases and users:
        return "base of auto " + ", ".join(users[:2]) + ("…" if len(users) > 2 else "")
    return ""


def editable(
    facts: Facts, names: list[str], *, bases: bool = True
) -> tuple[list[str], dict[str, str]]:
    """Split NAMES into (names that may be edited, {refused name: reason})."""
    refused = {n: r for n in names if (r := refusal(facts, n, bases=bases))}
    return [n for n in names if n not in refused], refused


def fresh_facts(native: Any, package_id: int) -> Facts:
    """Rescan just before a write. Refuse a switched font or pending host updates."""
    facts = scan(native)
    if facts.package_id != package_id:
        raise ValueError("The scanned font is no longer current; reload.")
    if tuple(native.flGlyph.updatedFgGlyphs()):
        raise ValueError(
            "Native glyph updates are pending; finish the current edit first."
        )
    return facts


def commit(
    native: Any,
    qtcore: Any,
    title: str,
    entries: list[Entry],
    mutate: Callable[[list[Entry]], Any],
) -> Any:
    """Run MUTATE as one Undo step, in the order the App writers use.

    1. checkInitHistoryState(0) on every layer and glyph, before any change.
    2. MUTATE(attempted). It appends each entry to ATTEMPTED before it changes it.
    3. One notifyChangesApplied([layers..., glyphs...]) for ATTEMPTED entries only.
    4. Same UTC lastModified stamp on every attempted glyph, before and after the notify.
    Finalise even when MUTATE fails, so a partial edit stays on the Undo stack.
    Glyphs that MUTATE never reached get no stamp and no notify.
    """
    stamp = qtcore.QDateTime.currentDateTimeUtc()
    work = {id(e): (e.glyph, tuple(e.glyph.layers)) for e in entries}
    for glyph, layers in work.values():
        for item in (*layers, glyph):
            item.checkInitHistoryState(0)
    errors: list[Exception] = []
    attempted: list[Entry] = []
    result = None
    try:
        result = mutate(attempted)
    except Exception as error:  # noqa: BLE001 - finalise history first
        errors.append(error)
    done = [work[id(e)] for e in attempted]
    if done:
        objects = [layer for _, layers in done for layer in layers]
        objects += [glyph for glyph, _ in done]
        try:
            for glyph, _ in done:
                glyph.lastModified = stamp
            native.flItems().notifyChangesApplied(title, objects)
        except Exception as error:  # noqa: BLE001 - never report a failed notify
            errors.append(error)
        finally:
            for glyph, _ in done:
                try:
                    glyph.lastModified = stamp
                except Exception as error:  # noqa: BLE001 - keep every observer error
                    errors.append(error)
    if errors:
        raise RuntimeError(
            f"{title} did not finish cleanly ({errors[0]!r}); check Edit > Undo."
        ) from errors[0]
    return result


# ------------------------------------------------------------------ core
def valid_mark(mark: int) -> bool:
    """Return True for none (0), a hue mark (1 to 360) or a grey mark (1001 to 1255)."""
    return mark == 0 or 1 <= mark <= 360 or 1000 < mark <= 1255


def mark_rgb(mark: int, lightness: int = LIGHTNESS) -> tuple[int, int, int] | None:
    """Return the RGB FontLab shows for MARK, or None for no mark.

    Hue marks use HSL (hue = mark - 1 degrees, S 200/255). Grey marks use a
    grey level of half the lightness plus half the level above 1000.
    """
    if mark <= 0:
        return None
    if mark <= 360:
        red, green, blue = colorsys.hls_to_rgb(
            (mark - 1) / 360, lightness / 255, SATURATION / 255
        )
        return round(red * 255), round(green * 255), round(blue * 255)
    grey = min(255, lightness // 2 + max(0, mark - 1000) // 2)
    return grey, grey, grey


def hex_of(rgb: tuple[int, int, int], factor: float = 1.0) -> str:
    """Return #rrggbb for RGB, scaled darker by FACTOR (1.0 keeps it)."""
    red, green, blue = (min(255, round(part * factor)) for part in rgb)
    return f"#{red:02x}{green:02x}{blue:02x}"


def ink_for(rgb: tuple[int, int, int]) -> str:
    """Return the readable text colour for a swatch: dark on light, white on dark."""
    return "#111111" if (max(rgb) + min(rgb)) / 2 > 140 else "#ffffff"


def mark_counts(facts: Facts, names: list[str] | None = None) -> dict[int, int]:
    """Return {mark: glyph count} over the whole font, or only over NAMES."""
    wanted = None if names is None else set(names)
    counts: dict[int, int] = {}
    for name, entry in facts.entries.items():
        if wanted is None or name in wanted:
            mark = int(entry.glyph.mark or 0)
            counts[mark] = counts.get(mark, 0) + 1
    return counts


def apply_mark(
    native: Any, qtcore: Any, package_id: int, names: list[str], mark: int
) -> list[str]:
    """Set MARK on NAMES. One Undo step. Return the names whose mark changed.

    Refused glyphs are skipped. Glyphs that already carry MARK are untouched.
    Raise ValueError for an empty selection, an unknown mark, a switched font
    or pending host updates.
    """
    if not names:
        raise ValueError("Select at least one glyph.")
    if not valid_mark(mark):
        raise ValueError(f"Mark {mark} is outside 0, 1-360 and 1001-1255.")
    facts = fresh_facts(native, package_id)
    allowed, _ = editable(facts, names, bases=False)
    todo = [
        facts.entries[n]
        for n in allowed
        if int(facts.entries[n].glyph.mark or 0) != mark
    ]
    if not todo:
        return []

    def mutate(attempted: list[Entry]) -> None:
        for entry in todo:
            attempted.append(entry)
            entry.glyph.mark = mark
            if int(entry.glyph.mark or 0) != mark:
                raise RuntimeError(
                    f"Native mark of {entry.name} differs from the plan."
                )

    commit(native, qtcore, TITLE, todo, mutate)
    return [entry.name for entry in todo]


def swatch_style(mark: int, border_idle: str) -> str:
    """Return the Qt style sheet of one swatch button. Dashed outline for none."""
    rgb = mark_rgb(mark)
    base = "border-radius: 8px; padding: 8px; text-align: left;"
    if rgb is None:
        return f"QPushButton {{ border: 1px dashed {border_idle}; {base} }}"
    return (
        f"QPushButton {{ background: {hex_of(rgb)}; color: {ink_for(rgb)};"
        f" border: 1px solid {hex_of(rgb, 0.83)}; {base} }}"
        f" QPushButton:pressed {{ background: {hex_of(rgb, 0.87)}; }}"
    )


# ------------------------------------------------------------------ panel
def _dialog_type() -> type:
    """Build the panel class lazily. Import Qt and App code only inside FontLab."""
    from fly import ap, qt
    from fly.ap.scripting import names_dialog_type, names_selected_names

    native = ap.fontlab
    QtCore, QtGui = qt.QtCore, qt.QtGui

    def dot_icon(mark: int, size: int = 12) -> Any:
        """Paint a small colour dot. Always end the painter."""
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(QtGui.QColor(0, 0, 0, 0))
        rgb = mark_rgb(mark)
        painter = QtGui.QPainter(pixmap)
        try:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            if rgb is None:
                painter.setPen(
                    QtGui.QPen(QtGui.QBrush(QtGui.QColor(128, 128, 128)), 1.0)
                )
                painter.drawEllipse(1, 1, size - 2, size - 2)
            else:
                painter.setPen(QtCore.Qt.NoPen)
                painter.setBrush(QtGui.QBrush(QtGui.QColor(*rgb)))
                painter.drawEllipse(0, 0, size, size)
        finally:
            painter.end()
        return QtGui.QIcon(pixmap)

    class MarkPalette(names_dialog_type()):
        """Modeless palette that marks the selected glyphs."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent, TITLE, KEY)
            self.resize(560, 420)
            self.setMinimumWidth(500)
            self.facts: Facts | None = None
            self.names: list[str] = []
            self.targets: list[str] = []
            self.refused: dict[str, str] = {}
            grid = QtGui.QGridLayout()
            grid.setSpacing(8)
            self.swatches: dict[int, Any] = {}
            idle = self.palette.color(QtGui.QPalette.Mid).name()
            for index, (label, mark) in enumerate(PRESETS):
                button = QtGui.QPushButton(label)
                button.setMinimumHeight(48)
                button.setStyleSheet(swatch_style(mark, idle))
                button.setToolTip(f"Mark value {mark}")
                grid.addWidget(button, index // 5, index % 5)
                self.swatches[mark] = button
                self._connect(button.clicked, lambda *a, m=mark: self.apply(m))
            self.root.addLayout(grid)
            caption = QtGui.QLabel("Selection")
            bold = caption.font
            bold.setBold(True)
            caption.setFont(bold)
            self.root.addWidget(caption)
            self.list = QtGui.QListWidget()
            self.list.setViewMode(QtGui.QListView.IconMode)
            self.list.setFlow(QtGui.QListView.LeftToRight)
            self.list.setWrapping(True)
            self.list.setResizeMode(QtGui.QListView.Adjust)
            self.list.setSpacing(4)
            self.list.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            self.list.setMinimumHeight(90)
            self.list.setIconSize(QtCore.QSize(14, 14))
            self.root.addWidget(self.list, 1)
            footer = QtGui.QHBoxLayout()
            self.status = QtGui.QLabel()
            self.status.setWordWrap(True)
            footer.addWidget(self.status, 1)
            self.reload_button = QtGui.QPushButton("Reload selection")
            self.close_button = QtGui.QPushButton("Close")
            footer.addWidget(self.reload_button)
            footer.addWidget(self.close_button)
            self.root.addLayout(footer)
            self._connect(self.reload_button.clicked, lambda *a: self.reload())
            self._connect(self.close_button.clicked, lambda *a: self.close())
            self.reload()

        def invalidate(self) -> None:
            """Also disable every swatch when the snapshot is stale."""
            super().invalidate()
            for button in getattr(self, "swatches", {}).values():
                button.setEnabled(False)

        def reload(self, message: str = "") -> None:
            """Rescan the font, re-read the selection, redraw the panel."""
            try:
                self.facts = scan(native)
                self.names = [
                    n for n in names_selected_names() if n in self.facts.entries
                ]
                self.targets, self.refused = editable(
                    self.facts, self.names, bases=False
                )
            except ValueError as error:
                self.facts, self.names, self.targets, self.refused = None, [], [], {}
                message = message or str(error)
            self.refresh(message)

        def refresh(self, message: str = "") -> None:
            """Show counts on the swatches and the selected glyphs with their marks."""
            facts = self.facts
            in_font = mark_counts(facts) if facts else {}
            in_selection = mark_counts(facts, self.targets) if facts else {}
            for label, mark in PRESETS:
                button = self.swatches[mark]
                button.setText(
                    f"{label}\n{in_font.get(mark, 0)} · {in_selection.get(mark, 0)} sel"
                )
                button.setEnabled(bool(self.targets))
            count = len(self.targets)
            if facts is None:
                self.subtitle.setText("Open a font first.")
            elif not self.names:
                self.subtitle.setText(
                    "Select glyphs in the Font window, then press Reload selection."
                )
            else:
                self.subtitle.setText(
                    f"Click a swatch to mark {count} glyph{'s' if count != 1 else ''}. "
                    "Numbers: glyphs in the font · in the selection."
                )
            self.list.clear()
            for name in self.targets:
                mark = int(facts.entries[name].glyph.mark or 0) if facts else 0
                self.list.addItem(QtGui.QListWidgetItem(dot_icon(mark), name))
            text = message or f"{len(facts.entries) if facts else 0} glyphs in font"
            if self.refused and not message:
                first = next(iter(self.refused.items()))
                text += f" · {len(self.refused)} refused ({first[0]}: {first[1]})"
            self.status.setText(text)

        def apply(self, mark: int) -> None:
            """Write MARK to the selected glyphs. One Undo step."""
            changed = apply_mark(
                native,
                QtCore,
                self.facts.package_id if self.facts else -1,
                self.targets,
                mark,
            )
            self.last_result = {"mark": mark, "changed": changed}
            label = {m: name for name, m in PRESETS}.get(mark, str(mark))
            noun = "glyph" if len(changed) == 1 else "glyphs"
            self.reload(f"{label}: changed {len(changed)} {noun}")

    return MarkPalette


def main() -> Any:
    """Open or replace the Mark Color Palette panel."""
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(_dialog_type(), KEY)


if __name__ == "__main__":
    main()
