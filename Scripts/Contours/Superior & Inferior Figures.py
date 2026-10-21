# this_file: Scripts/Contours/Superior & Inferior Figures.py
# SPDX-License-Identifier: Apache-2.0
"""Create superior (.sups) or inferior (.subs) copies of the selected figures.

What it does:
    For each selected figure (zero to nine, also with a suffix) the script
    creates a new glyph with ".sups" or ".subs" added to the name, on every
    master. The outline is scaled by one factor and moved up or down; the
    advance width is scaled by the same factor. The source figures do not
    change.

How it works:
    A non-modal panel lists every selected glyph with its new name, or the
    reason why it is skipped. Choose Superior or Inferior: the vertical shift
    takes the usual preset (350 or -150 units), which you can change. Create
    checks the font again. FontLab's own Add Glyph command makes each new
    glyph with its master layers and widths (rounded half up). Then one step
    through the shared module fly.ap.history adds the scaled copies to all
    new layers. The copy keeps node names and raw node flags, which a
    FontLab contour copy can drop (fl#8569). After the write the script
    reads every new layer back, and checks that no automatic glyph of the
    font changed. The creation, the contour copy and the panel are shared
    (fly.ap.glyph_copies, fly.ap.contour_copy).

Copy limits:
    Anchors are not copied. Add the required anchors to the new glyphs before
    building accented composites.
    Only node names and raw node flags are repaired (fl#8569); selection is
    cleared. Other node properties and contour names are not repaired.
    Copied contours are merged into one element; source element names and
    notes are not copied.

Why this design:
    - Scaling about the baseline origin, then one vertical shift, keeps all
      new figures on one common baseline, as the sups and subs features
      expect.
    - Scaled figures come out lighter than the originals. The result is a
      starting point for drawing, not finished superiors.
    - A figure needs a layer with contours on every master, with no
      components and no automatic layer. Otherwise the figure is listed and
      skipped, so the new glyphs stay compatible across masters.
    - A target name that exists is never overwritten. Create is refused
      while FontLab has pending glyph updates. The script does not call
      UpdateAll (fl#8537).
    - FontLab can rebuild an automatic glyph when a new name appears. When
      the font has automatic glyphs without a recipe whose names carry the
      new suffix, the row shows "may rebuild auto ..." and is skipped unless
      you tick "Create even if FontLab may rebuild these auto glyphs". Use
      selection clears the tick.
    - Each new glyph is recorded as its own Undo step, and the outlines as
      one more Undo step.

How to use:
    Select the figures in the Font window. Run the script. Choose Superior or
    Inferior, set the scale and the shift, check the table and press Create.

Benefit:
    A compatible set of superior or inferior figures to refine, in every
    master, in one step.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_superiors.py, "Superior & Inferior Figures").
"""

from collections.abc import Sequence
from typing import Any

TITLE = "Superior & Inferior Figures"
KEY = "generate_superiors"
FIGURES = frozenset(
    {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"}
)
KINDS = (
    (".sups", "Superior", 350),
    (".subs", "Inferior", -150),
)  # suffix, label, preset shift
SIZED = frozenset(
    {"sups", "subs", "sinf", "numr", "dnom"}
)  # suffixes of figures that are sized already


def naming_for(suffix: str) -> Any:
    """Return the naming function for ``suffix`` (".sups" or ".subs")."""

    def naming(name: str) -> tuple[str, str]:
        parts = name.split(".")
        if parts[0] not in FIGURES:
            return "", "not a figure"
        if SIZED.intersection(parts[1:]):
            return "", "already superior or inferior"
        return name + suffix, ""

    return naming


def survey(
    package: Any,
    names: Sequence[str],
    facts: Any,
    suffix: str = ".sups",
    allow_rebuild: bool = False,
) -> list[Any]:
    """Plan one sized copy per selected figure. Change nothing."""
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return glyph_copies.survey_with(
        package, names, naming_for(suffix), facts, allow_rebuild
    )


def prepare(rows: Sequence[Any], scale: int, shift: int) -> list[Any]:
    """Return the jobs: copies scaled by ``scale`` percent about the origin, then shifted up."""
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402
    from fly import qt

    factor = scale / 100
    transform = qt.QtGui.QTransform(factor, 0, 0, factor, 0, shift)
    return [
        (
            row.target,
            [
                (
                    m,
                    contour_copy.copy_contours(x, transform),
                    glyph_copies.half_up(x.advanceWidth * factor),
                )
                for m, x in row.layers
            ],
        )
        for row in rows
        if not row.note
    ]


def panel_type() -> type:
    """Build the panel class once Qt is available (inside FontLab)."""
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    from fly import qt

    QtGui = qt.QtGui

    class SuperiorsPanel(glyph_copies.panel_type()):
        """Kind, scale, shift, preview table, status and buttons."""

        TITLE, KEY, NOUN = TITLE, KEY, "figures"

        def build_controls(self) -> None:
            """Kind, scale and vertical shift; a new kind takes its preset shift."""
            self.kind = QtGui.QComboBox()
            for suffix, label, _ in KINDS:
                self.kind.addItem(f"{label} ({suffix})")
            self.factor = QtGui.QSpinBox()
            self.factor.setRange(10, 100)
            self.factor.setSuffix(" %")
            self.factor.setValue(60)
            self.shift = QtGui.QSpinBox()
            self.shift.setRange(-1000, 1000)
            self.shift.setSuffix(" units")
            self.shift.setValue(KINDS[0][2])
            self.add_row("Kind", self.kind)
            self.add_row("Scale", self.factor)
            self.add_row("Vertical shift", self.shift)
            self.watch(self.kind.currentIndexChanged, self.switch_kind)

        def suffix(self) -> str:
            """Return the chosen suffix."""
            return KINDS[self.kind.currentIndex][0]

        def switch_kind(self) -> None:
            """Take the preset shift of the chosen kind, then plan again."""
            self.shift.setValue(KINDS[self.kind.currentIndex][2])
            self.refresh()

        def survey(self, package: Any, facts: Any, allow_rebuild: bool) -> list[Any]:
            """Plan one sized copy per selected figure with the chosen suffix."""
            return survey(package, self.names, facts, self.suffix(), allow_rebuild)

        def jobs(self, rows: list[Any]) -> list[Any]:
            """Scaled and shifted copies of the ready rows."""
            return prepare(rows, int(self.factor.value), int(self.shift.value))

    return SuperiorsPanel


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
