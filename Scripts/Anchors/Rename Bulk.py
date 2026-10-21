# this_file: Scripts/Anchors/Rename Bulk.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Rename Bulk
"""Find and replace anchor names across glyphs and masters.

What: Renames anchors by plain text or by regular expression. Scope: the
selected glyphs or the whole font; the current master or all masters.
Example: find "^(top|bottom)$", replace "\\1_alt".

How: The table updates with each key press. It lists every rename and flags
a blocked row in red. Rename writes all renames as one Undo step.
Position, style and expressions of each anchor stay as they are.

Why: A rename is blocked, not guessed, when the new name is empty, already in
use on the layer, or the target of two old names. This avoids silent
merges of anchors. A bad pattern shows its error and changes nothing.

Use: Select glyphs. Run the script. Type Find and Replace. Check the table.
Press Rename. Press Reload selection after you change the selection.

Benefit: One consistent anchor vocabulary in all masters, in one step, with a
complete preview.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads the result back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Edit > Undo restores the font. The one-step write, the automatic-layer rule
and the pending-update check are shared with other scripts (fly.ap.history,
fly.ap.edit_guards); the planner and the panel belong to this script.

Source: the author's own FontLab sample
anchors_rename_bulk.py, Apache-2.0.
Independent rewrite for the current FontLab 9 API.
"""

import math
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

import fly.ap.edit_guards as edit_guards  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import ap, qt
from fly.ap import scripting

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
TITLE = "Rename Anchors in Bulk"
KEY = "anchors_rename_bulk"

# ---------------------------------------------------------------- shared kernel
# Private copy: the same planner kernel serves all anchor writers of this folder.
# The one-step write, the auto-layer policy and the pending-update check are
# the shared fly.ap.history and fly.ap.edit_guards.
Edit = tuple[str, str, Any]
# Edit = (operation, anchor name, value).
#   ("set", name, (x, y))   move the anchor; add it when missing
#   ("remove", name, None)  delete every anchor with this name
#   ("rename", name, new)   rename every anchor with this name
Work = list[tuple[Any, Any, list[Edit]]]  # (glyph, layer, edits)

# Name-derived pin appearance. FontLab infers it only on Redo or reopen,
# so a new pin gets it now (related: fl#8527).
APPEARANCE: dict[str, int] = {
    "top": 5,
    "_bottom": 5,
    "bottom": 6,
    "_top": 6,
    "left": 7,
    "_left": 7,
    "right": 8,
    "_right": 8,
    "center": 1,
    "_center": 1,
}
ORIGIN_ERROR = (
    "FontLab cannot Redo an existing anchor moved to 0, 0. "
    "Choose other values or other glyphs."
)
MAX_ROWS = 500  # preview rows shown; the edit itself is never truncated
EPSILON = 1e-6


@dataclass(frozen=True)
class Change:
    """One preview row. `edit` None: shown only. `problem` set: blocks Apply."""

    name: str
    old: str
    new: str
    edit: Edit | None = None
    problem: str = ""


@dataclass
class Plan:
    """Everything one Apply would do, plus the reasons it may not."""

    work: Work = field(default_factory=list)
    rows: list[tuple[str, Change]] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)

    @property
    def anchors(self) -> int:
        return sum(len(edits) for _, _, edits in self.work)


Planner = Callable[[Any, str, Any], list[Change]]  # (glyph, master, layer)


def half_up(value: float) -> int:
    """Round half up: 14.5 -> 15 and -14.5 -> -14, on every platform."""
    return math.floor(value + 0.5)


def plural(count: int, word: str) -> str:
    """'1 layer', '2 layers'."""
    return f"{count} {word}{'' if count == 1 else 's'}"


def fmt(value: float) -> str:
    """Whole numbers without decimals: 700.0 -> 700."""
    return f"{value:g}"


def layer_of(glyph: Any, master: str) -> Any | None:
    """Existing master layer, or None. Never creates a layer."""
    layer = glyph.findLayer(master)
    return None if layer is None or layer.isNull else layer


def raw_point(pin: Any) -> tuple[float, float]:
    """Stored anchor position, unrounded."""
    return float(pin.point.x()), float(pin.point.y())


def anchor_points(layer: Any) -> dict[str, tuple[float, float]]:
    """{name: (x, y)} of the layer. Duplicate names: the last one wins."""
    return {pin.name: raw_point(pin) for pin in layer.anchors}


def duplicated(layer: Any, names: Iterable[str]) -> list[str]:
    """Names in `names` that several anchors of the layer carry."""
    counts: dict[str, int] = {}
    for pin in layer.anchors:
        counts[pin.name] = counts.get(pin.name, 0) + 1
    return sorted(n for n in set(names) if counts.get(n, 0) > 1)


def refusal(names: Iterable[str]) -> list[Change]:
    """One blocking row: the edit would be ambiguous."""
    return [
        Change(n, "", "", problem=f"several anchors named {n}; use Duplicates Finder")
        for n in names
    ]


def parse_names(text: str) -> list[str]:
    """'top, bottom;ogonek' -> ['top', 'bottom', 'ogonek']."""
    return [n.strip() for n in text.replace(";", ",").split(",") if n.strip()]


def collect(glyphs: Iterable[Any], masters: Iterable[str], planner: Planner) -> Plan:
    """Run `planner` on every editable layer. Auto layers are listed, never edited."""
    plan = Plan()
    for glyph in glyphs:
        for master in masters:
            layer = layer_of(glyph, master)
            changes = planner(glyph, master, layer) if layer is not None else []
            if not changes:
                continue
            label = f"{glyph.name} · {master}"
            if layer.autoLayer:
                plan.skipped.append(f"{glyph.name}/{master}")
                note = Change(plural(len(changes), "anchor"), "", "auto layer, skipped")
                plan.rows.append((label, note))
                continue
            plan.rows.extend((label, change) for change in changes)
            blocked = [c.problem for c in changes if c.problem]
            plan.problems.extend(f"{label}: {text}" for text in blocked)
            edits = [c.edit for c in changes if c.edit is not None]
            if edits and not blocked:
                plan.work.append((glyph, layer, edits))
    return plan


def shown(names: list[str]) -> str:
    """'a, b, c …' for long lists."""
    return ", ".join(names[:8]) + (" …" if len(names) > 8 else "")


def blocked_rows(work: Work, facts: history.AutoFacts) -> list[tuple[str, Change]]:
    """One blocking row per edited glyph that the geometry policy refuses.

    A glyph that owns an auto layer, or is a base of one (also through other
    composites), is refused: FontLab rebuilds the auto composite and Undo does
    not restore it.
    """
    names = [glyph.name for glyph, _, _ in work]
    found = history.refusals(facts, names, "geometry")
    return [
        (name, Change("blocked", "", "", problem=why)) for name, why in found.items()
    ]


def require_safe(work: Work, facts: history.AutoFacts) -> None:
    """Refuse the whole batch before any history exists, when Undo or Redo would fail.

    1. Queued glyph updates: a later edit would deliver them as real updates
       and change unrelated glyph dates (fl#8537). The queue is never cleared.
    2. An existing anchor moved to 0, 0 does not Redo (fl#8527).
    3. A glyph that owns an auto layer or is a base of one (blocked_rows).
    """
    edit_guards.require_settled(fontlab)
    for _, layer, edits in work:
        existing = {pin.name for pin in layer.anchors}
        for operation, name, value in edits:
            if operation == "set" and name in existing and tuple(value) == (0, 0):
                raise ValueError(ORIGIN_ERROR)
    found = blocked_rows(work, facts)
    if found:
        reasons = [f"{name}: {change.problem}" for name, change in found]
        raise ValueError(
            f"FontLab cannot undo edits to these glyphs: {shown(reasons)}. "
            "Choose other glyphs."
        )


def prepare(layer: Any, edits: list[Edit]) -> list[tuple[str, Any, Any]]:
    """Build every native pin and point BEFORE history opens.

    Returns [(step, pin, value)]. A new pin gets its name-derived appearance.
    An existing pin keeps its own style and expressions.
    """
    pins = list(layer.anchors)
    steps: list[tuple[str, Any, Any]] = []
    for operation, name, value in edits:
        same = [pin for pin in pins if pin.name == name]
        if operation == "set":
            point = QtCore.QPointF(float(value[0]), float(value[1]))
            if same:
                steps.append(("move", same[0], point))
            else:
                pin = fontlab.flPinPoint(point)
                pin.name, pin.anchor = name, True
                pin.appearance = APPEARANCE.get(name.lower(), 0)
                steps.append(("add", None, pin))
        elif operation == "remove":
            steps.extend(("remove", pin, None) for pin in same)
        elif operation == "rename":
            steps.extend(("rename", pin, value) for pin in same)
    return steps


def write(layer: Any, steps: list[tuple[str, Any, Any]]) -> None:
    """Touch only the planned pins. Existing pin objects are edited in place."""
    for step, pin, value in steps:
        if step == "add":
            layer.addAnchor(value)
        elif step == "move":
            pin.point = value
        elif step == "remove":
            layer.removeAnchor(pin)
        elif step == "rename":
            pin.name = value


def unstored(work: Work, before: list[dict[str, tuple[float, float]]]) -> list[str]:
    """Edits FontLab did not keep (a strong rounding preference drops fractions).

    `before` holds each layer's points from before the write. Only a
    coordinate that the edit changed is checked. An untouched coordinate may
    legitimately be rounded by FontLab, and that is not an error here.
    """
    missed: list[str] = []
    for (glyph, layer, edits), old_points in zip(work, before, strict=True):
        points = anchor_points(layer)
        names = {pin.name for pin in layer.anchors}
        for operation, name, value in edits:
            if operation == "set":
                point, old = points.get(name), old_points.get(name)
                ok = point is not None and all(
                    abs(point[axis] - value[axis]) < EPSILON
                    for axis in (0, 1)
                    if old is None or abs(old[axis] - value[axis]) >= EPSILON
                )
            elif operation == "remove":
                ok = name not in names
            else:
                ok = name not in names and value in names
            if not ok:
                missed.append(f"{glyph.name}/{name}")
    return missed


def apply_work(work: Work, title: str, facts: history.AutoFacts) -> dict[str, int]:
    """Write all edits as ONE native Undo step through history.commit.

    Auto layers are never in `work`; `facts` is a fresh history.scan_auto_facts.
    No rollback is attempted. A failure after history has started raises
    history.PartialWriteError ("... use Edit > Undo"). Afterwards every value
    is read back; a value FontLab did not keep raises RuntimeError.
    """
    prepared = [(layer, prepare(layer, edits)) for _, layer, edits in work]
    glyphs = list({glyph.name: glyph for glyph, _, _ in work}.values())
    layers = [layer for _, layer, _ in work]
    if not layers:
        return {"anchors": 0, "layers": 0}
    before = [anchor_points(layer) for layer in layers]

    def mutate() -> None:
        for layer, steps in prepared:
            write(layer, steps)

    def read_back() -> list[str]:
        return unstored(work, before)

    done = history.commit(
        title,
        layers,
        glyphs,
        mutate,
        operation="geometry",
        facts=facts,
        read_back=read_back,
    )
    if done.mismatches:
        missed = done.mismatches
        raise RuntimeError(
            f"FontLab did not store {len(missed)} change(s): {', '.join(missed[:6])}. "
            "Check Preferences > Rounding. Edit > Undo restores the font."
        )
    # Count native operations: one removed pin is one, also for duplicates.
    return {"anchors": sum(len(steps) for _, steps in prepared), "layers": len(work)}


# ---------------------------------------------------------------- shared panel
# Private copy: the same panel base serves all anchor writers of this folder.
ERROR_COLOR = "#d33"


def ink() -> Any:
    """Brush for item text. FontLab palette Text can be pale in item views."""
    palette = fontlab.MainWindow().palette
    return QtGui.QBrush(QtGui.QColor(palette.color(QtGui.QPalette.WindowText)))


def muted(widget: Any) -> str:
    """Secondary text colour, derived from the live theme."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


def readable_palette(widget: Any) -> None:
    """Per colour group keep the better of Text and WindowText against Base."""
    palette = widget.palette
    for group in (QtGui.QPalette.Active, QtGui.QPalette.Inactive):
        base = QtGui.QColor(palette.color(group, QtGui.QPalette.Base)).lightness()
        candidates = (
            QtGui.QColor(palette.color(group, QtGui.QPalette.Text)),
            QtGui.QColor(palette.color(group, QtGui.QPalette.WindowText)),
        )
        best = max(candidates, key=lambda c: abs(c.lightness() - base))
        palette.setColor(group, QtGui.QPalette.Text, best)
    widget.setPalette(palette)


class AnchorPanel(QtGui.QDialog):
    """Non-modal panel: controls, live preview table, Reload, Close, Apply.

    Subclasses set TITLE, KEY, ACTION, HEADERS and override build_controls()
    and planner(). The preview recomputes on every control change and shows
    exactly what Apply would write. Apply stays off while any row is blocked.
    """

    TITLE = ""
    KEY = ""
    ACTION = "Apply"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Anchor", "Current", "New")
    WIDTH = 580

    def __init__(self, parent: Any = None) -> None:
        QtGui.QDialog.__init__(self, parent)
        readable_palette(self)
        self._connections: list[Any] = []  # filled by scripting.connect_guarded
        self.timers: list[Any] = []  # stopped when the panel closes
        self.slot_error = ""
        self.last_result: dict[str, Any] = {}
        self.glyphs: list[Any] = []
        self.facts = history.auto_facts(())
        self.scopes: list[Any] = []
        self.rows = 0
        self.read_font()
        self.setWindowTitle(self.TITLE)
        self.setMinimumWidth(self.WIDTH)
        self.build()
        self.reload()

    # -- layout
    def build(self) -> None:
        """Create every widget before any font data is read."""
        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(self.TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)
        self.form = QtGui.QGridLayout()
        self.form.setHorizontalSpacing(10)
        self.form.setVerticalSpacing(8)
        self.form.setColumnStretch(1, 1)
        root.addLayout(self.form)
        self.build_controls()
        self.table = QtGui.QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(list(self.HEADERS))
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(220)
        root.addWidget(self.table, 1)
        bar = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        bar.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Reload selection")
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton(self.ACTION)
        self.apply_button.setDefault(True)
        for button in (self.reload_button, self.close_button, self.apply_button):
            bar.addWidget(button)
        root.addLayout(bar)
        self.watch(self.reload_button.clicked, self.reload)
        self.watch(self.close_button.clicked, self.close)
        self.watch(self.apply_button.clicked, self.apply)

    def build_controls(self) -> None:
        """Subclass hook: add widgets to self.form and self.watch() their signals."""

    def watch(self, signal: Any, callback: Callable[..., Any] | None = None) -> None:
        """Connect through the guard: an exception in a PythonQt slot can exit FontLab."""
        action = callback or self.refresh
        scripting.connect_guarded(self, signal, lambda *args: action())

    def spin(self, low: int, high: int, value: int, suffix: str = "") -> Any:
        """Right-aligned integer box with readable text."""
        box = QtGui.QSpinBox()
        box.setStyleSheet(f"color: {ink().color().name()};")
        box.setRange(low, high)
        box.setValue(value)
        box.setSuffix(suffix)
        box.setAlignment(QtCore.Qt.AlignRight)
        return box

    def scope_box(self) -> Any:
        """Combo: current master or all masters."""
        box = QtGui.QComboBox()
        box.addItem("")
        box.addItem("")
        self.scopes.append(box)
        self.relabel()
        return box

    def relabel(self) -> None:
        """Keep the scope combos in step with the font."""
        for box in self.scopes:
            box.setItemText(0, f"Current master ({self.current_master})")
            box.setItemText(1, f"All masters ({len(self.masters)})")

    # -- data
    def planner(self) -> Planner:
        """Subclass hook: return the per-layer planner. Raise ValueError on bad input."""
        raise NotImplementedError

    def chosen_masters(self) -> list[str]:
        return list(self.masters)

    def read_font(self) -> None:
        """Bind to the current font and its masters."""
        self.package = scripting.current_package()
        self.package_id = self.package.id if self.package is not None else None
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""

    def reload(self) -> None:
        """Scan again. A failure shows in the status line and blocks Apply."""
        try:
            self.scan()
        except Exception as error:  # noqa: BLE001 - the first scan runs in the constructor
            self.slot_error = repr(error)
            self.glyphs, self.facts = [], history.auto_facts(())
            self.refresh()
            self.status.setText(f"Error: {error}")

    def scan(self) -> None:
        """Read font, selection and the auto-composite map again."""
        self.read_font()
        self.relabel()
        self.glyphs, self.facts = [], history.auto_facts(())
        if self.package is not None:
            found = (self.package.findName(n) for n in self.glyph_names())
            self.glyphs = [glyph for glyph in found if glyph is not None]
            self.facts = history.scan_auto_facts(self.package)
        self.on_reload()
        self.refresh()

    def glyph_names(self) -> list[str]:
        """Glyphs the panel works on: the Font window selection, or the current glyph."""
        return scripting.names_selected_names()

    def on_reload(self) -> None:
        """Subclass hook: refresh control contents that depend on the font."""

    def intro(self) -> str:
        """Subtitle text. Names the glyphs, or says what is missing."""
        if self.package is None:
            return "Open a font first."
        if not self.glyphs:
            return "Select glyphs in the Font window, then press Reload selection."
        count = len(self.glyphs)
        names = ", ".join(g.name for g in self.glyphs[:8]) + (" …" if count > 8 else "")
        return f"{count} glyph{'s' if count != 1 else ''}: {names}"

    def refresh(self) -> None:
        """Recompute the plan; fill the table; enable Apply only when it is safe."""
        self.subtitle.setText(self.intro())
        plan, problem = Plan(), ""
        if self.package is not None and self.glyphs:
            try:
                plan = collect(self.glyphs, self.chosen_masters(), self.planner())
            except ValueError as error:
                problem = str(error)
        if plan.problems:
            problem = plan.problems[0]
        if plan.work:
            plan.rows[:0] = blocked_rows(plan.work, self.facts)
            if not problem:
                try:
                    require_safe(plan.work, self.facts)
                except ValueError as error:
                    problem = str(error)
        self.fill(plan)
        self.apply_button.setEnabled(bool(plan.work) and not problem)
        self.status.setText(
            problem
            or f"{plural(plan.anchors, 'anchor change')} on "
            f"{plural(len(plan.work), 'layer')}"
        )

    def fill(self, plan: Plan) -> None:
        """Show the first MAX_ROWS rows.

        Blocked rows red, changes in the accent colour, notes (auto layers
        that are skipped) in the muted colour.
        """
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        alarm = QtGui.QColor(ERROR_COLOR)
        quiet = QtGui.QColor(muted(self))
        shown = plan.rows[:MAX_ROWS]
        self.rows = len(shown)
        self.table.setRowCount(len(shown))
        for row, (label, change) in enumerate(shown):
            cells = self.cells(label, change)
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                item.setForeground(ink())
                if column == len(cells) - 1:
                    if change.problem:
                        color = alarm
                    else:
                        color = accent if change.edit is not None else quiet
                    item.setForeground(QtGui.QBrush(color))
                self.table.setItem(row, column, item)

    def cells(self, label: str, change: Change) -> list[str]:
        """Row texts for 3 columns (glyph, anchor, result) or 4 (with current)."""
        last = change.problem or change.new
        if len(self.HEADERS) == 3:
            return [label, change.name, last]
        return [label, change.name, change.old, last]

    # -- action
    def apply(self) -> None:
        """Plan again from live data, re-check safety, write once."""
        try:
            package = scripting.current_package(self.package_id)
            if package is None:
                raise ValueError("The font changed; press Reload selection.")
            if package.master != self.current_master:
                raise ValueError("Master changed; Reload selection.")
            glyphs = [package.findName(glyph.name) for glyph in self.glyphs]
            if any(glyph is None or glyph.isNull for glyph in glyphs):
                raise ValueError("Glyphs changed; Reload selection.")
            edit_guards.require_settled(fontlab)
            plan = collect(glyphs, self.chosen_masters(), self.planner())
            if plan.problems:
                raise ValueError(plan.problems[0])
            facts = history.scan_auto_facts(package)
            require_safe(plan.work, facts)
            self.last_result = apply_work(plan.work, self.TITLE, facts)
            self.last_result["skipped"] = plan.skipped
        finally:
            self.refresh()
        result = self.last_result
        skipped = len(result["skipped"])
        note = f" · {plural(skipped, 'auto layer')} skipped" if skipped else ""
        self.status.setText(
            f"Changed {plural(result['anchors'], 'anchor')} "
            f"on {plural(result['layers'], 'layer')}{note}"
        )

    def closeEvent(self, event: Any) -> None:
        scripting.close_script_dialog(self, event, self.KEY, timers=self.timers)


# ---------------------------------------------------------------- rename logic
TYPING_PAUSE_MS = 250  # whole-font scope: replan this long after the last key


def renamer(find: str, replace: str, regex: bool) -> Callable[[str], str]:
    """Return old name -> new name. Raise ValueError for a bad pattern.

    Plain mode replaces every occurrence of `find`. Regex mode uses re.sub.
    An empty `find` changes nothing.
    """
    if not find:
        return lambda name: name
    if not regex:
        return lambda name: name.replace(find, replace)

    def substitute(name: str) -> str:
        try:
            return re.sub(find, replace, name)
        except (re.error, IndexError) as error:
            raise ValueError(f"Pattern error: {error}") from error

    substitute("")  # a bad pattern or template fails now, not at the first match
    return substitute


def rename_changes(layer: Any, rename: Callable[[str], str]) -> list[Change]:
    """Rows for the anchors whose name changes. Blocked rows carry a problem.

    Blocked: empty new name; new name already on the layer; two old names
    with the same new name. Chains (a to b, b to c) are blocked too.
    """
    existing = {pin.name for pin in layer.anchors}
    renamed = {old: rename(old) for old in sorted(existing)}
    changed = {old: new for old, new in renamed.items() if new != old}
    targets: dict[str, int] = {}
    for new in changed.values():
        targets[new] = targets.get(new, 0) + 1
    changes: list[Change] = []
    for old, new in changed.items():
        problem = ""
        if not new:
            problem = "the new name is empty"
        elif new in existing:
            problem = f"{new} is already used on this layer"
        elif targets[new] > 1:
            problem = f"several anchors would become {new}"
        edit = None if problem else ("rename", old, new)
        changes.append(Change(old, old, new or "–", edit, problem))
    return changes


class RenameBulk(AnchorPanel):
    """Find, Replace, Regex, glyph scope and master scope."""

    TITLE, KEY, ACTION = TITLE, KEY, "Rename"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Anchor", "New name")

    def build_controls(self) -> None:
        self.find = QtGui.QLineEdit()
        self.find.setPlaceholderText("e.g. top  or  ^(top|bottom)$")
        self.replace = QtGui.QLineEdit()
        self.replace.setPlaceholderText("e.g. top_alt  or  \\1.case")
        self.regex = QtGui.QCheckBox("Regular expression")
        self.glyph_scope = QtGui.QComboBox()
        self.glyph_scope.addItem("Selected glyphs")
        self.glyph_scope.addItem("Whole font")
        self.scope = self.scope_box()
        self.form.addWidget(QtGui.QLabel("Find"), 0, 0)
        self.form.addWidget(self.find, 0, 1)
        self.form.addWidget(self.regex, 0, 2)
        self.form.addWidget(QtGui.QLabel("Replace"), 1, 0)
        self.form.addWidget(self.replace, 1, 1, 1, 2)
        self.form.addWidget(QtGui.QLabel("Glyphs"), 2, 0)
        self.form.addWidget(self.glyph_scope, 2, 1, 1, 2)
        self.form.addWidget(QtGui.QLabel("Masters"), 3, 0)
        self.form.addWidget(self.scope, 3, 1, 1, 2)
        self.timer = QtCore.QTimer()  # one-shot: replans after typing pauses
        self.timer.setSingleShot(True)
        self.timers.append(self.timer)
        self.watch(self.timer.timeout)
        for signal in (self.find.textChanged, self.replace.textChanged):
            self.watch(signal, self.typed)
        for signal in (self.regex.toggled, self.scope.currentIndexChanged):
            self.watch(signal)
        self.watch(self.glyph_scope.currentIndexChanged, self.reload)

    def typed(self) -> None:
        """Whole-font plans are slow: wait for a pause in typing. Else plan now."""
        if self.glyph_scope.currentIndex == 1:
            self.apply_button.setEnabled(False)
            self.timer.start(TYPING_PAUSE_MS)
        else:
            self.refresh()

    def glyph_names(self) -> list[str]:
        if self.glyph_scope.currentIndex == 1:
            return [name for name, _ in scripting.names_font_glyphs()]
        return scripting.names_selected_names()

    def chosen_masters(self) -> list[str]:
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def planner(self) -> Planner:
        rename = renamer(self.find.text, self.replace.text, self.regex.isChecked())
        return lambda glyph, master, layer: rename_changes(layer, rename)


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(RenameBulk, KEY)


if __name__ == "__main__":
    main()
