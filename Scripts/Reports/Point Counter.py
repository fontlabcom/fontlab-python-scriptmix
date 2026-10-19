# this_file: Scripts/Reports/Point Counter.py
# SPDX-License-Identifier: Apache-2.0
"""Count own contour nodes in all foreground layers of selected glyphs.

Select glyphs in a Font window or occurrences in a Glyph window, then run this
Reports command. Each selected occurrence emits its glyph's complete foreground
layer list in stored order, including auxiliary and empty layers. Repeated
selections remain repeated. Components are not decomposed. Masks and service
layers are background/cache records and are excluded explicitly.

Each row shows points, lines, curves, offcurves and paths. The original '?'
marker compares a row's total with the previous two rows. Quadratic on-curves
now count as curves, correcting the source's omission from point totals.
Refresh replaces the complete snapshot. Select and copy report text normally.
Close removes the owned modeless panel. This adaptation uses an owned report
instead of clearing/writing the user's Output panel; no font, selection,
history or preference writers are called. Native getter preservation, layer
mapping, selection order/focus and lifecycle acceptance are pending.

Requires reviewed App>=0.2.35.dev1 and fontlab-fly in FontLab9 Python3.11.
Adapted from Alex Slobzheninov's Apache-2.0 Point Counter. See NOTICE and
additional-tools.json for source identity and full license provenance.
"""


def main() -> None:
    """Load the shared report panel through Fly only when this menu runs."""
    from fly.ap.scripting import point_counts_dialog_type, show_script_dialog

    panel = point_counts_dialog_type()
    show_script_dialog(panel, panel.KEY)


if __name__ == "__main__":
    main()
