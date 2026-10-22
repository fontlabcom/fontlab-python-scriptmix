# this_file: Scripts/Metrics/Copy Metrics From Reference.py
# SPDX-License-Identifier: Apache-2.0
"""Give the selected glyphs the sidebearings or the advance width of a reference
glyph.

What it does: copies the metrics of one reference glyph to the selected glyphs,
on the current master or on all masters. Four modes are available: "LSB and
RSB", "LSB only", "RSB only" and "Advance width (centred)". An optional offset
is added to each copied value.

How it works: each master takes the reference values of the same master, so a
multi-master family keeps its progression. Sidebearings are read from the
outline edges in whole units. In the sidebearing modes the outline moves in
place by the LSB change (anchors move with it) and the advance width becomes
LSB + outline width + RSB. In "Advance width (centred)" the advance becomes
the reference advance plus the offset; the change is shared by both sides, and
the right side takes the odd unit. The reference glyph itself is never edited.
A master without a reference layer, a reference without outline (sidebearing
modes) and a layer without outline are listed and skipped. A result with a
negative width is refused for that layer.

Why: related glyphs share their spacing: n, m, h and u take the sidebearings of
n; H, I and N take those of H; figures take one tabular width. Copying values
by
hand in every master is slow and error prone.

How to use: select the glyphs to change in the Font window. Type the reference
glyph name; the completer lists the glyphs of the font. Choose the mode, the
offset and the current master or all masters. Check the table. Press Apply. The
panel stays open. Press "Use selection" to read the Font window selection and
the glyph list again.

Safety: each Apply is recorded as one Undo step. Auto layers are listed and
never edited. A
glyph that owns an auto layer is listed and skipped as a whole. Layers with a
metrics link or expression are listed and skipped. A base of auto glyphs is
refused, because FontLab rebuilds the auto glyphs and may lose their anchors
and locks (FontLab issue 8512). Tick "Edit bases of auto glyphs anyway" to go
on. Apply discloses queued ids and their possible date changes. After the write
the script reads advance and outline back and reports any mismatch. A failure
after the write started says so and asks you to use Edit > Undo. It does not
call UpdateAll (FontLab issue 8537).

Shared parts: the panel, the plan model, the one-step write and the read-back
come from the App module fly.ap.metrics_panel. This script holds its own
maths, its planner and its controls.

Benefit: consistent spacing groups in all masters in one step, with a preview.

Credit: adapted from metrics_copy_from_reference.py, the author's own FontLab
sample, Apache-2.0.
"""

from typing import Any

import fly.ap.metrics_panel as metrics_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap.scripting import names_font_glyphs, show_script_dialog

QtCore, QtGui = qt.QtCore, qt.QtGui
MetricsPanel = metrics_panel.panel_type()

MODES = [
    ("LSB and RSB", "both"),
    ("LSB only", "lsb"),
    ("RSB only", "rsb"),
    ("Advance width (centred)", "width"),
]
OFFSET_RANGE = (-1000, 1000)  # Units added to each copied value.


# ---------------------------------------------------------------- core
def units(layer: Any) -> tuple[int, int, int, int] | None:
    """Return (lsb, rsb, width, ink width) in whole units, or None for an empty layer."""
    edges = metrics_panel.ink_edges(layer)
    if edges is None:
        return None
    left, right = metrics_panel.unit(edges[0]), metrics_panel.unit(edges[1])
    width = metrics_panel.unit(layer.advanceWidth)
    return left, width - right, width, right - left


def copied(
    own: tuple[int, int, int, int],
    reference: tuple[int | None, int | None, int],
    mode: str,
    offset: int,
) -> tuple[int, int, int]:
    """Return the new (lsb, rsb, width).

    own is (lsb, rsb, width, ink width) of the layer to change. reference is
    (lsb, rsb, width) of the reference layer; its sides may be None in mode
    "width", which uses only the reference width.
    """
    lsb, rsb, width, ink = own
    if mode == "width":
        new_width = reference[2] + offset
        change = new_width - width
        left = int(change / 2)  # Toward zero: the right side takes the odd unit.
        return lsb + left, rsb + change - left, new_width
    new_lsb = reference[0] + offset if mode in ("both", "lsb") else lsb
    new_rsb = reference[1] + offset if mode in ("both", "rsb") else rsb
    return new_lsb, new_rsb, new_lsb + ink + new_rsb


def copy_planner(reference: Any, mode: str, offset: int) -> metrics_panel.Planner:
    """Return the planner that copies from the reference glyph's layer of each master."""

    def plan(layer: Any, master: str) -> metrics_panel.LayerPlan | str:
        source = reference.findLayer(master)
        if source is None or source.isNull:
            return "no reference layer in this master"
        found = units(layer)
        if found is None:
            return "empty (no outline)"
        ref = units(source)
        if ref is None:
            if mode != "width":
                return "reference has no outline"
            ref_values = (None, None, metrics_panel.unit(source.advanceWidth))
        else:
            ref_values = ref[:3]
        new_lsb, new_rsb, new_width = copied(found, ref_values, mode, offset)
        if new_width < 0:
            return "negative width (skipped)"
        lsb, rsb, width, _ = found
        cells = tuple(str(v) for v in (lsb, rsb, width, new_lsb, new_rsb, new_width))
        if (new_lsb, new_rsb, new_width) == (lsb, rsb, width):
            new_width = layer.advanceWidth  # Same values: keep a fractional width.
        return metrics_panel.make_plan(layer, new_lsb - lsb, new_width, cells)

    return plan


# ---------------------------------------------------------------- panel
class CopyMetricsFromReference(MetricsPanel):
    """Copy metrics from a reference glyph: reference, mode, offset, masters."""

    TITLE = "Copy Metrics From Reference"
    KEY = "metrics_copy_from_reference"
    HEADERS = ("LSB", "RSB", "Width", "New LSB", "New RSB", "New width")
    ACCENT = (4, 5, 6)
    MIN_WIDTH = 620

    def build(self) -> None:
        """Create the reference field with its completer, the mode and the offset."""
        self.reference = QtGui.QLineEdit()
        self.completer = QtGui.QCompleter(self)
        self.completion_model = QtGui.QStringListModel(self.completer)
        self.completer.setModel(self.completion_model)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setFilterMode(QtCore.Qt.MatchContains)
        self.reference.setCompleter(self.completer)
        self.copy_mode = QtGui.QComboBox()
        for label, _ in MODES:
            self.copy_mode.addItem(label)
        self.offset = self.spin(*OFFSET_RANGE, 0, " units")
        self.form.addWidget(QtGui.QLabel("Reference"), 1, 0)
        self.form.addWidget(self.reference, 1, 1, 1, 3)
        self.form.addWidget(QtGui.QLabel("Copy"), 2, 0)
        self.form.addWidget(self.copy_mode, 2, 1)
        self.form.addWidget(QtGui.QLabel("Offset"), 2, 2)
        self.form.addWidget(self.offset, 2, 3)
        self.watch(self.reference.textChanged)
        self.watch(self.copy_mode.currentIndexChanged)
        self.fill_names()

    def fill_names(self) -> None:
        """Give the completer the glyph names of the current font, in font order.

        A failed read leaves the completer empty. The reason stays visible as
        the field's placeholder, because refresh() rewrites the status line.
        """
        try:
            names = [name for name, _ in names_font_glyphs()]
            hint = "Glyph name, e.g. H or n"
        except (ValueError, RuntimeError, TimeoutError) as error:
            names = []
            hint = f"Glyph list not read ({error}); type a glyph name"
        self.reference.setPlaceholderText(hint)
        self.completion_model.setStringList(names)

    def reselect(self) -> None:
        """Read the glyph list and the Font window selection again."""
        self.fill_names()
        MetricsPanel.reselect(self)

    def reference_name(self) -> str:
        """The typed reference name without surrounding spaces."""
        return str(self.reference.text).strip()

    def target_glyphs(self, package: Any) -> list[Any]:
        """The captured selection without the reference glyph itself."""
        name = self.reference_name()
        return [g for g in MetricsPanel.target_glyphs(self, package) if g.name != name]

    def empty_message(self) -> str:
        """Ask for glyphs other than the reference."""
        return (
            "Select the glyphs to change (not the reference) in the Font window. "
            "Then press Use selection."
        )

    def subtitle_hint(self) -> str:
        """Describe the current settings."""
        count = len({e.glyph.name for e in self.entries})
        label = MODES[self.copy_mode.currentIndex][0]
        return (
            f"{count} glyph{'s' if count != 1 else ''} take {label} of "
            f"{self.reference_name()}, master by master."
        )

    def planner(self, package: Any, glyphs: list[Any]) -> metrics_panel.Planner:
        """Planner for the typed reference. A missing name is refused (ValueError)."""
        name = self.reference_name()
        if not name:
            raise ValueError("Type the name of the reference glyph.")
        reference = package.findName(name)
        if reference is None or reference.isNull:
            raise ValueError(f"No glyph named {name} in this font.")
        mode = MODES[self.copy_mode.currentIndex][1]
        return copy_planner(reference, mode, self.offset.value)


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(CopyMetricsFromReference, CopyMetricsFromReference.KEY)


if __name__ == "__main__":
    main()
