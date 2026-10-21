# this_file: Scripts/Reports/Vertical Metrics Reporter.py
# SPDX-License-Identifier: Apache-2.0
"""Compare eight stored vertical metrics across every open font and master.

Open the fonts to compare, then run this Reports command. The complete report
compares typoAscender, typoDescender, typoLineGap, hheaAscender, hheaDescender,
hheaLineGap, winDescent and winAscent in source order. Equal values receive a
check mark; differences list every document/master and its value, in stored
order. An unset hhea override is None, distinct from an explicit zero.

FontLab mapping uses master ascender/descender/lineGap, otherData hhea fields,
safeBottom and safeTop. This compares stored native settings; exported or
automatically derived metrics are outside its claim. No active-master switch
is used. No open fonts, unreadable data, deadline or changing source produces
a partial report. Native serialization/schema/order and complete preservation
qualification remain pending.

Refresh replaces the entire snapshot. Select and copy text normally. Close
removes this owned modeless panel. This presentation replaces the source's
Output clearing; no font, history, selection, preference or Output writer is
called. Requires App>=0.2.37.dev0 and Fly in FontLab9 Python3.11.
Adapted from Pedro Arilla's Apache-2.0 Vertical metrics reporter.py; provenance
and license are retained in NOTICE and additional-tools.json.
"""


def main() -> None:
    """Load the shared App report through Fly only when this menu is invoked."""
    from fly.ap.scripting import show_script_dialog, vertical_metrics_dialog_type

    panel = vertical_metrics_dialog_type()
    show_script_dialog(panel, panel.KEY)


if __name__ == "__main__":
    main()
