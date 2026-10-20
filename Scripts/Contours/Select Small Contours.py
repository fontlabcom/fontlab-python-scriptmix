# this_file: Scripts/Contours/Select Small Contours.py
# SPDX-License-Identifier: Apache-2.0
"""Ask for an unsigned area threshold and select smaller first-layer contours.

Enter square font units. Select clears that layer's node and non-node selection,
then selects every node of each own contour strictly below the threshold. Open
contours are closed for measurement only. Negative and zero finite values are
valid; invalid text, nonfinite values and Close leave selection unchanged.

Curves use analytic FontTools area, which can differ from Glyphs' flattening.
Mixed non-node selection currently requires one displayed glyph; unsupported
native selection kinds refuse before writes. Native acceptance is pending.
Adapted independently from Pedro Arilla's Paths/Select small paths.py
(2018–2022), Apache-2.0; exact hashes are in NOTICE/additional-tools.json.
Requires fontlab-fly and fontlab-fontlabapp[fontui] 0.2.71.dev0.
"""

from typing import Any


def main() -> Any:
    """Open the owned source-bound numeric prompt through Fly."""
    from fly.ap.contour_selection import show_small_contours

    return show_small_contours()


if __name__ == "__main__":
    main()
