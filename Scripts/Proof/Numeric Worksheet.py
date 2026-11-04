# this_file: Scripts/Proof/Numeric Worksheet.py
# SPDX-License-Identifier: Apache-2.0
"""Estimate proof widths and quotes from the selected glyphs, and count revisions.

What: Opens a modeless worksheet with three groups of inputs. The integer and
decimal recipes each adjust the advance widths of the selected glyph layers
(an offset in font units, and for the decimal recipe a percent scale). The
report lists, for every selected layer, both candidate advances and an
advance-only proof width in points at 12 pt, which is an estimate without
kerning or shaping. It also quotes a price per distinct selected glyph for
each recipe. The revision group takes a date, a time and an instant and counts
the glyphs of the whole font whose modification date is on or before each
cutoff; glyphs without a recorded date are counted as unknown.

Use: Open a font and select glyphs in a Font window or glyph layers in a Glyph
window. Run Proof > Numeric Worksheet. Edit the inputs and read the report.
Press Refresh Font and Selection after you change the font, the master or the
selection; your inputs stay. Close the panel when you are done. Without a
font the inputs still work and the report says that no facts are captured.

Safety: Read-only. The tool reads units per em, the advance widths of the
selected layers and the glyph modification dates. All inputs and results stay
in the panel and nothing is applied to the font. It writes no font data,
metrics, selection, history, preference, file, clipboard or Output text. If
the facts change while the tool reads them, it refuses to publish a partial
result and asks you to refresh.

Source: Original workflow built on the shared App numeric worksheet
(fly.ap.proof.numeric.launcher), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.
"""

from typing import Any


def main() -> Any:
    """Open the shared numeric worksheet, or replace the one already open."""
    from fly.ap.proof.numeric.launcher import show

    return show()


if __name__ == "__main__":
    main()
