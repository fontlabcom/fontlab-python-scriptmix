# this_file: Scripts/Contours/Small Caps From Capitals.py
# SPDX-License-Identifier: Apache-2.0
"""Create small-cap glyphs (h.sc, a.sc, ...) from the selected capitals.

What it does:
    For each selected capital the script creates a small-cap glyph on every
    master: H becomes h.sc, H.ss01 becomes h.sc.ss01. The outline is scaled
    by separate horizontal and vertical factors; the advance width is scaled
    horizontally. The capitals do not change.

How it works:
    A non-modal panel lists every selected glyph with its new name, or the
    reason why it is skipped. Create checks the font again. FontLab's own
    Add Glyph command makes each new glyph with its master layers and widths
    (rounded half up). Then one step through the shared module
    fly.ap.history adds the scaled copies to all new layers. The copy keeps
    node names and raw node flags, which a FontLab contour copy can drop
    (fl#8569). After the write the script reads every new layer back, and
    checks that no automatic glyph of the font changed. The creation, the
    contour copy and the panel are shared (fly.ap.glyph_copies,
    fly.ap.contour_copy).

Copy limits:
    Anchors are not copied. Add the required anchors to the new glyphs before
    building accented composites.
    Only node names and raw node flags are repaired (fl#8569); selection is
    cleared. Other node properties and contour names are not repaired.
    Copied contours are merged into one element; source element names and
    notes are not copied.

Why this design:
    - The name is the lowercase base plus ".sc", the usual naming for the
      smcp and c2sc features.
    - A larger horizontal than vertical factor keeps vertical stems
      relatively heavier, so the small caps do not look too light at once.
      The result is a starting point for drawing, not finished small caps.
    - A capital needs a layer with contours on every master, with no
      components and no automatic layer. Otherwise it is listed and skipped,
      so the new glyphs stay compatible across masters. Accented capitals
      are usually components: build their small caps from the new bases.
    - A target name that exists is never overwritten. Create is refused
      while FontLab has pending glyph updates. The script does not call
      UpdateAll (fl#8537).
    - FontLab can rebuild an automatic glyph when a new name appears. When
      the font has automatic glyphs without a recipe whose names carry the
      new suffix (such as eacute.sc), the row shows "may rebuild auto ..."
      and is skipped unless you tick "Create even if FontLab may rebuild
      these auto glyphs". Use selection clears the tick.
    - Each new glyph is recorded as its own Undo step, and the outlines as
      one more Undo step.

How to use:
    Select capitals in the Font window. Run the script. Set the horizontal
    and vertical scale, check the table and press Create.

Benefit:
    A compatible set of small caps to refine, in every master, in one step.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_small_caps.py, "Small Caps from Capitals").
"""

from collections.abc import Sequence
from typing import Any

TITLE = "Small Caps From Capitals"
KEY = "generate_small_caps"
SUFFIX = ".sc"


def is_capital(name: str) -> bool:
    """True when the base name (before the first dot) starts with a capital letter."""
    base = name.partition(".")[0]
    return base[:1].isupper() and base.lower() != base


def target_name(name: str) -> str:
    """Return the small-cap name: H -> h.sc, H.ss01 -> h.sc.ss01."""
    base, dot, rest = name.partition(".")
    return base.lower() + SUFFIX + (dot + rest if dot else "")


def naming(name: str) -> tuple[str, str]:
    """Return (new name, problem) for a selected glyph name."""
    if not is_capital(name):
        return "", "not a capital"
    return target_name(name), ""


def survey(
    package: Any, names: Sequence[str], facts: Any, allow_rebuild: bool = False
) -> list[Any]:
    """Plan one small cap per selected capital. Change nothing."""
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return glyph_copies.survey_with(package, names, naming, facts, allow_rebuild)


def prepare(rows: Sequence[Any], x_scale: int, y_scale: int) -> list[Any]:
    """Return the jobs: copies scaled by the percentages about the origin."""
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402
    from fly import qt

    sx, sy = x_scale / 100, y_scale / 100
    transform = qt.QtGui.QTransform(sx, 0, 0, sy, 0, 0)
    return [
        (
            row.target,
            [
                (
                    m,
                    contour_copy.copy_contours(x, transform),
                    glyph_copies.half_up(x.advanceWidth * sx),
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

    class SmallCapsPanel(glyph_copies.panel_type()):
        """Horizontal and vertical scale, preview table, status and buttons."""

        TITLE, KEY, NOUN = TITLE, KEY, "capitals"

        def build_controls(self) -> None:
            """Horizontal and vertical scale in percent."""
            self.x_scale, self.y_scale = QtGui.QSpinBox(), QtGui.QSpinBox()
            for spin, value in ((self.x_scale, 75), (self.y_scale, 70)):
                spin.setRange(10, 200)
                spin.setSuffix(" %")
                spin.setValue(value)
            self.add_row("Horizontal scale", self.x_scale)
            self.add_row("Vertical scale", self.y_scale)

        def survey(self, package: Any, facts: Any, allow_rebuild: bool) -> list[Any]:
            """Plan one small cap per selected capital."""
            return survey(package, self.names, facts, allow_rebuild)

        def jobs(self, rows: list[Any]) -> list[Any]:
            """Scaled copies of the ready rows."""
            return prepare(rows, int(self.x_scale.value), int(self.y_scale.value))

    return SmallCapsPanel


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
