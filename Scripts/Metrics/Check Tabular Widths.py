# this_file: Scripts/Metrics/Check Tabular Widths.py
# SPDX-License-Identifier: Apache-2.0
"""Check exact selected-layer advances against the first selected occurrence.

Select glyphs in a Font window or layer occurrences in a Glyph window. Run
this Metrics command. The first occurrence supplies the reference. Editor
repeats retain their own layer choices; Font-window rows use the current master.
Fractional values remain exact.
Metrics keys and Auto do not override the actual advances. The report shows
one result per selected-layer occurrence, same/different totals and time heading.

Use Refresh after changing selection, master or widths. Close removes the
owned modeless panel. The report calls no font, selection, history, preferences
or Output writers. Empty/stale/missing sources produce a complete diagnosis.
Requires App>=0.2.33.dev0 and fontlab-fly in FontLab9
Python3.11. Adapted from Pedro Arilla's Apache-2.0 Tabular width checker; see
additional-tools.json and NOTICE.
"""


def main() -> None:
    """Load shared App support only when this menu command runs."""
    from fly.ap.scripting import show_script_dialog, tabular_width_dialog_type

    panel = tabular_width_dialog_type()
    show_script_dialog(panel, panel.KEY)


if __name__ == "__main__":
    main()
