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
The edit is recorded as one Undo step. The plan, the safety checks, the one-step
write and the panel base are shared with the other anchor scripts
(fly.ap.anchor_writer, fly.ap.anchor_panel); the planner and the controls
belong to this script.

Source: the author's own FontLab sample
anchors_rename_bulk.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

import re
from collections.abc import Callable
from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
import fly.ap.scripting as scripting

QtCore, QtGui = qt.QtCore, qt.QtGui
TITLE = "Rename Anchors in Bulk"
KEY = "anchors_rename_bulk"

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


def rename_changes(
    layer: Any, rename: Callable[[str], str]
) -> list[anchor_writer.Change]:
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
    changes: list[anchor_writer.Change] = []
    for old, new in changed.items():
        problem = ""
        if not new:
            problem = "the new name is empty"
        elif new in existing:
            problem = f"{new} is already used on this layer"
        elif targets[new] > 1:
            problem = f"several anchors would become {new}"
        edit = None if problem else ("rename", old, new)
        changes.append(anchor_writer.Change(old, old, new or "–", edit, problem))
    return changes


class RenameBulk(anchor_panel.panel_type()):
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

    def planner(self) -> anchor_writer.Planner:
        rename = renamer(self.find.text, self.replace.text, self.regex.isChecked())
        return lambda glyph, master, layer: rename_changes(layer, rename)


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(RenameBulk, KEY)


if __name__ == "__main__":
    main()
