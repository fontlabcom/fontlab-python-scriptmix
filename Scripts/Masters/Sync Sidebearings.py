# this_file: Scripts/Masters/Sync Sidebearings.py
# SPDX-License-Identifier: Apache-2.0
"""Copy sidebearings from a reference master to the other masters.

What it does:
    For each selected glyph, give the layers of the other masters the left
    and right sidebearings of the reference master. "Proportional to ink
    width" scales the reference sidebearings by the ratio of the ink widths
    (target / reference), so bolder masters keep the same rhythm. "Same
    values" copies them unchanged. The outline, components and anchors move
    together, and the advance width follows.

How it works:
    The ink edges are the outline bounding box. New LSB and RSB are rounded
    half up to whole units. The script moves the layer by the LSB change and
    sets the advance width to new LSB + ink width + new RSB. The panel is the
    shared Metrics panel (fly.ap.metrics_panel): a live preview table, the
    masters choice (the current master or all masters; the reference itself
    is never a target), one Undo step per Apply and a read-back of advance
    and outline edge.

Why this design:
    - The shared panel moves outlines in place (applyTransform), never
      through a clone, so node flags and shape notes stay (fl#8516, fl#8538).
    - Automatic layers and glyphs that own one are listed and skipped.
      Layers with a metrics link or expression are listed and skipped: the
      link would undo the change. A base of automatic composites needs the
      "Edit bases of auto glyphs anyway" tick, because FontLab rebuilds the
      automatic glyphs and may lose their anchors and locks. Apply is
      refused while FontLab has pending glyph updates.
    - A glyph without outline in the reference or the target is listed and
      skipped: it has no sidebearings.
    - Values round half up, not to the nearest even number: 52.5 becomes 53.

How to use:
    Space the reference master first. Select glyphs in the Font window. Run
    the script. Choose the reference and the rule. Check the table. Press
    Apply. The panel stays open; press "Use selection" for other glyphs.

Benefit:
    Consistent spacing across all masters in one step, as a start for
    fine-tuning the extremes.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (masters_sync_metrics.py, "Sync Sidebearings").
"""

from typing import Any

import fly.ap.metrics_panel as metrics_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap.scripting import connect_guarded, current_package, show_script_dialog

QtGui = qt.QtGui
MetricsPanel = metrics_panel.panel_type()

RULES = ("Proportional to ink width", "Same values")


# ---------------------------------------------------------------- core
def target_sidebearings(
    reference: tuple[float, float], width: float, own: tuple[float, float], proportional: bool
) -> tuple[int, int]:
    """Return the new (LSB, RSB) of a target layer in whole units.

    ``reference`` and ``own`` are the (left, right) ink edges of the
    reference and the target layer. ``width`` is the reference advance.
    """
    lsb, rsb = reference[0], width - reference[1]
    ink = reference[1] - reference[0]
    factor = (own[1] - own[0]) / ink if proportional and ink > 0 else 1.0
    return metrics_panel.unit(lsb * factor), metrics_panel.unit(rsb * factor)


def sync_planner(reference: Any, proportional: bool) -> metrics_panel.Planner:
    """Return the planner of one glyph, given its reference layer (or None)."""

    def plan(layer: Any, master: str) -> metrics_panel.LayerPlan | str:
        if reference is None:
            return "no layer in the reference master"
        ref = metrics_panel.ink_edges(reference)
        if ref is None:
            return "reference has no outline"
        own = metrics_panel.ink_edges(layer)
        if own is None:
            return "empty (no outline)"
        new_lsb, new_rsb = target_sidebearings(ref, reference.advanceWidth, own, proportional)
        left, right = metrics_panel.unit(own[0]), metrics_panel.unit(own[1])
        width = new_lsb + (right - left) + new_rsb
        if width < 0:
            return "negative width (skipped)"
        cells = (f"{left}", f"{metrics_panel.unit(layer.advanceWidth) - right}", f"{new_lsb}", f"{new_rsb}")
        return metrics_panel.make_plan(layer, new_lsb - left, width, cells)

    return plan


# ---------------------------------------------------------------- panel
class SyncSidebearings(MetricsPanel):
    """Reference master and rule over the shared Metrics panel."""

    TITLE = "Sync Sidebearings"
    KEY = "masters_sync_metrics"
    HEADERS = ("LSB", "RSB", "New LSB", "New RSB")
    ACCENT = (3, 4)

    def build(self) -> None:
        """Create the reference and rule controls. Start with all masters."""
        self.reference = QtGui.QComboBox()
        package = current_package()
        masters = [str(m) for m in package.masters] if package is not None else []
        for master in masters:
            self.reference.addItem(master)
        if package is not None and str(package.master) in masters:
            self.reference.setCurrentIndex(masters.index(str(package.master)))
        self.rule = QtGui.QComboBox()
        for label in RULES:
            self.rule.addItem(label)
        self.scope.setCurrentIndex(1)
        self.form.addWidget(QtGui.QLabel("Reference"), 1, 0)
        self.form.addWidget(self.reference, 1, 1, 1, 3)
        self.form.addWidget(QtGui.QLabel("Rule"), 2, 0)
        self.form.addWidget(self.rule, 2, 1, 1, 3)
        for combo in (self.reference, self.rule):
            connect_guarded(self, combo.currentIndexChanged, lambda *a: self.refresh())

    def subtitle_hint(self) -> str:
        """Describe the current settings."""
        return f"Sidebearings from {self.reference.currentText} ({RULES[self.rule.currentIndex].lower()})."

    def chosen_masters(self, package: Any) -> list[str]:
        """Return the target masters: the current or all masters, never the reference."""
        masters = [package.master] if self.scope.currentIndex == 0 else list(package.masters)
        return [m for m in masters if m != self.reference.currentText]

    def make_entries(self) -> list[metrics_panel.Entry]:
        """Plan each glyph with its own reference layer."""
        package = self.font_package()
        glyphs = self.target_glyphs(package)
        if not glyphs:
            raise ValueError(self.empty_message())
        targets = self.chosen_masters(package)
        if not targets:
            raise ValueError("The current master is the reference. Choose All masters or another reference.")
        proportional = self.rule.currentIndex == 0
        entries: list[metrics_panel.Entry] = []
        for glyph in glyphs:
            reference = glyph.findLayer(self.reference.currentText)
            reference = None if reference is None or reference.isNull else reference
            entries.extend(metrics_panel.survey([glyph], targets, sync_planner(reference, proportional)))
        return entries


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(SyncSidebearings, SyncSidebearings.KEY)


if __name__ == "__main__":
    main()
