# this_file: Scripts/Reports/Dump to Svg Path Commands.py
# SPDX-License-Identifier: Apache-2.0 AND MIT
"""First selected layer own paths only; ordered M/L/C operands, unconditional Z and blank line after every open/closed/empty contour. Unsupported/quadratic segments refuse the whole report; not a complete SVG/component export. Own affine shape transforms are applied; projective transforms refuse the whole report.

Open a font and select glyph layers before running. The owned modeless read-only
panel offers selectable text, Refresh and Close. Failures clear the entire old
report; no partial prefix is shown. No font, file, clipboard, Output, selection,
history or preference writers run. Actual native getter preservation and panel
lifetime acceptance remain pending. Requires FontLab9 Python3.11, matching Fly
and App0.2.77.dev0 or later. Adapted from simoncozens--GlyphsScripts/Dump to SVG.py; see NOTICE.
"""


def main() -> None:
    """Open the complete original reporting workflow through shared Fly/App UI."""
    from fly.ap.svg_path_commands import show

    show()


if __name__ == "__main__":
    main()
