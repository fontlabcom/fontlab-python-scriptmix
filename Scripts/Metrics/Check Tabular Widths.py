# this_file: Scripts/Metrics/Check Tabular Widths.py
# SPDX-License-Identifier: Apache-2.0
"""Check exact selected-glyph advances against the first selected glyph.

Open a font and select glyphs in the Font window. Run this Metrics menu entry.
The first selected glyph in native font order supplies the reference; every
selected glyph is checked on the active master. Fractional values remain exact.
Metrics keys and Auto do not override the actual advances. The report shows
one result per glyph, same/different totals and the original time heading.

Use Refresh after changing selection, master or widths. Close removes the
owned modeless panel. No selection, font data, preferences or Output content is
changed. Empty selection and stale or missing sources produce a diagnosis.
Requires the matching fontlab-fontlabapp candidate and fontlab-fly in FontLab9
Python3.11. Adapted from Pedro Arilla's Apache-2.0 Tabular width checker; see
additional-tools.json and NOTICE. Native acceptance is pending.
"""


def main() -> None:
    """Load shared App support only when this menu command runs."""
    from fly.ap.scripting import show_script_dialog, tabular_width_dialog_type

    panel = tabular_width_dialog_type()
    show_script_dialog(panel, panel.KEY)


if __name__ == "__main__":
    main()
