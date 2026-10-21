# this_file: Scripts/Contours/Tabular Figure Copies.py
# SPDX-License-Identifier: Apache-2.0
"""Create tabular (.tf) copies of the selected figures, with one shared width per master.

What it does:
    For each selected figure (zero to nine, also with a suffix such as
    one.osf) the script creates a new glyph with ".tf" added to the name, on
    every master. In each master all new glyphs get one advance width: the
    widest selected figure of that master plus an extra amount. The figure
    outline is copied and centred in that width. The source figures do not
    change.

How it works:
    A non-modal panel lists every selected glyph with its new name, or the
    reason why it is skipped. Create checks the font again. FontLab's own
    Add Glyph command makes each new glyph with its master layers and the
    shared widths. Then one step through the shared module fly.ap.history
    adds the centred copies to all new layers. The centring keeps the
    outline on whole units; an odd unit of white space goes to the right
    side. The copy keeps node names and raw node flags, which a FontLab
    contour copy can drop (fl#8569). After the write the script reads every
    new layer back, and checks that no automatic glyph of the font changed.
    The creation, the contour copy and the panel are shared
    (fly.ap.glyph_copies, fly.ap.contour_copy).

Copy limits:
    Anchors are not copied. Add the required anchors to the new glyphs before
    building accented composites.
    Only node names and raw node flags are repaired (fl#8569); selection is
    cleared. Other node properties and contour names are not repaired.
    Copied contours are merged into one element; source element names and
    notes are not copied.

Why this design:
    - New glyphs, not changed figures: proportional and tabular figures can
      then live side by side, as the OpenType tnum feature expects. To make
      the existing figures tabular in place, use Metrics > Tabular Width.
    - A figure needs a layer with contours on every master, with no
      components and no automatic layer. Otherwise the figure is listed and
      skipped, so the new glyphs stay compatible across masters.
    - A target name that exists is never overwritten.
    - Create is refused while FontLab has pending glyph updates. The script
      does not call UpdateAll (fl#8537).
    - FontLab can rebuild an automatic glyph when a new name appears. When
      the font has automatic glyphs without a recipe whose names carry the
      new suffix, the row shows "may rebuild auto ..." and is skipped unless
      you tick "Create even if FontLab may rebuild these auto glyphs". Use
      selection clears the tick.
    - Each new glyph is recorded as its own Undo step, and the outlines as
      one more Undo step.

How to use:
    Select the figures in the Font window. Run the script. Set the extra
    width, check the table and press Create. Narrow figures such as one can
    then need redrawing in their wider space.

Benefit:
    A complete, compatible set of tabular figures to refine, in one step.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_tabular_copies.py, "Tabular Figure Copies").
"""

from collections.abc import Sequence
from typing import Any

TITLE = "Tabular Figure Copies"
KEY = "generate_tabular_copies"
SUFFIX = ".tf"
FIGURES = frozenset(
    {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"}
)


def naming(name: str) -> tuple[str, str]:
    """Return (new name, problem) for a selected glyph name."""
    parts = name.split(".")
    if parts[0] not in FIGURES:
        return "", "not a figure"
    if "tf" in parts[1:]:
        return "", "already tabular"
    return name + SUFFIX, ""


def survey(
    package: Any, names: Sequence[str], facts: Any, allow_rebuild: bool = False
) -> list[Any]:
    """Plan one tabular copy per selected figure. Change nothing."""
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return glyph_copies.survey_with(package, names, naming, facts, allow_rebuild)


def tabular_widths(rows: Sequence[Any], extra: int) -> dict[str, int]:
    """Map each master to the widest source advance (rounded half up) plus ``extra``."""
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    widths: dict[str, int] = {}
    for row in rows:
        if row.note:
            continue
        for master, layer in row.layers:
            widths[master] = max(
                widths.get(master, 0), glyph_copies.half_up(layer.advanceWidth)
            )
    return {master: width + extra for master, width in widths.items()}


def centring_shift(layer: Any, width: int) -> int:
    """Return the whole-unit x shift that centres the outline in ``width``.

    The left side becomes (width - ink width) // 2; an odd unit goes right.
    """
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    box = layer.boundingBox
    left = glyph_copies.half_up(box.x())
    ink = glyph_copies.half_up(box.x() + box.width()) - left
    return (width - ink) // 2 - left


def prepare(rows: Sequence[Any], widths: dict[str, int]) -> list[Any]:
    """Return the jobs: centred contour copies and the shared width per master."""
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    from fly import qt

    jobs: list[Any] = []
    for row in rows:
        if row.note:
            continue
        layers = []
        for master, layer in row.layers:
            move = qt.QtGui.QTransform(
                1, 0, 0, 1, centring_shift(layer, widths[master]), 0
            )
            layers.append(
                (master, contour_copy.copy_contours(layer, move), widths[master])
            )
        jobs.append((row.target, layers))
    return jobs


def panel_type() -> type:
    """Build the panel class once Qt is available (inside FontLab)."""
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    from fly import qt

    QtGui = qt.QtGui

    class TabularCopiesPanel(glyph_copies.panel_type()):
        """Extra width, preview table, status and buttons."""

        TITLE, KEY, NOUN = TITLE, KEY, "figures"

        def build_controls(self) -> None:
            """Extra width; a change plans again."""
            self.extra = QtGui.QSpinBox()
            self.extra.setRange(-200, 400)
            self.extra.setSuffix(" units")
            self.extra.setValue(0)
            self.add_row("Extra width", self.extra)
            self.watch(self.extra.valueChanged)

        def survey(self, package: Any, facts: Any, allow_rebuild: bool) -> list[Any]:
            """Plan one tabular copy per selected figure."""
            return survey(package, self.names, facts, allow_rebuild)

        def jobs(self, rows: list[Any]) -> list[Any]:
            """Centred copies of the ready rows in the shared widths."""
            return prepare(rows, tabular_widths(rows, int(self.extra.value)))

        def intro(self) -> str:
            """Subtitle: the shared width per master."""
            widths = tabular_widths(self.rows, int(self.extra.value))
            shown = ", ".join(f"{m} {w}" for m, w in widths.items())
            return (
                f"Shared width per master: {shown}"
                if widths
                else "No figure qualifies."
            )

    return TabularCopiesPanel


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
