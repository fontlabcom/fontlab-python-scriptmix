# this_file: Scripts/Contours/Select Partial Contours.py
# SPDX-License-Identifier: Apache-2.0
"""Fill stored-order spans between originally selected nodes in the first layer.

What it does:
    Each selected node toggles the fill state. State carries across contour bounds;
    the command never wraps around to the first node or chooses a shortest arc.
    Controls count as nodes. Components, other non-node selections and other layers
    stay unchanged. No geometry or Undo step is created.

    Adapted independently from Pedro Arilla's Paths/Select partial path.py
    (2018–2022). See NOTICE and additional-tools.json for exact hashes and Apache
    terms. Requires fontlab-fly and App 0.2.71.dev0.

How it works:
    Delegate the stored-order toggle-fill algorithm to App. Capture original
    node selection, carry fill state across contours and leave component
    selections outside the pass.

Why this design:
    A deterministic stored-order span differs from shortest-arc selection;
    keeping that rule explicit prevents a surprising wraparound choice.

How to use:
    Open a glyph, select the boundary nodes and run Contours > Select Partial
    Contours. Inspect the resulting spans before applying a separate edit to
    that selection.

Benefit:
    Select repeatable node spans across contours while leaving geometry and
    all other layers unchanged.
"""


def main() -> int:
    """Apply the original cross-contour toggle algorithm through Fly."""
    from fly.ap.contour_selection import select_partial_contours

    count = select_partial_contours()
    print(f"{count} contours selected.")
    return count


if __name__ == "__main__":
    main()
