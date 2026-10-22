# this_file: Scripts/Contours/Select Contours.py
# SPDX-License-Identifier: Apache-2.0
"""Select each own contour with any selected node in the first selected layer.

What it does:
    Select a node or control handle, then run this command. All nodes in its contour
    become selected. Existing components and other non-node selections stay intact.
    Other selected layers stay unchanged. No geometry or Undo step is created.

    Adapted independently from Pedro Arilla's Paths/Select paths.py (2018–2022).
    See NOTICE and additional-tools.json for exact source hashes and Apache terms.
    Requires fontlab-fly and App 0.2.71.dev0.

How it works:
    Delegate contour expansion to App. Capture original node selection on the
    first selected layer and select all nodes of each touched own contour.

Why this design:
    A handle is a node too, so touching a control can identify the same whole
    contour without requiring an on-curve selection.

How to use:
    Open a glyph, select a node or control and run Contours > Select Contours.
    Inspect the expanded selection before a separate contour operation.

Benefit:
    Expand node selection to complete contours while keeping geometry,
    components and other layers unchanged.
"""


def main() -> int:
    """Run the shared native action through Fly and report selected contour count."""
    from fly.ap.contour_selection import select_contours

    count = select_contours()
    print(f"{count} contours selected.")
    return count


if __name__ == "__main__":
    main()
