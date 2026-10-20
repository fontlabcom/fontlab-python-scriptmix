# this_file: Scripts/Reports/Master Node Compatibility Report.py
# SPDX-License-Identifier: Apache-2.0
"""Selected unique glyphs, every master versus first, full path/oncurve/line/curve+qcurve/handle/point counters and first node mismatch. Fix equal-count type mismatches and trailing missing reference paths.

Open a font and select glyph layers before running. The owned modeless read-only
panel offers selectable text, Refresh and Close. Failures clear the entire old
report; no partial prefix is shown. No font, file, clipboard, Output, selection,
history or preference writers run. Actual native getter preservation and panel
lifetime acceptance remain pending. Requires FontLab9 Python3.11, matching Fly
and App0.2.77.dev0 or later. Adapted from Reset-Type-Studio--Glyphs-Scripts/Paths/Compatibility Check.py; see NOTICE.
"""


def main() -> None:
    """Open the complete original reporting workflow through shared Fly/App UI."""
    from fly.ap.master_node_report import show

    show()


if __name__ == "__main__":
    main()
