# this_file: Scripts/Anchors/Copy Anchors Between Fonts.py
# SPDX-License-Identifier: Apache-2.0
"""Copy anchor metadata between two chosen fonts with complete collision options.

What it does:
    Choose each font and layer (or All masters), all/selected source glyphs and
    all/specific anchors. Keep absolute or width-proportional x and optional italic
    shift, overwrite or rename incoming/destination, and the editable suffix.
    Selected mode requires the chosen source Font window to be active.
    Independent implementation of TypeRig TR-CopyAnchors2.3; no original body copy.
    See NOTICE/additional-tools.json for MPL2 upstream provenance and App.134.

How it works:
    Delegate the two-font anchor dialog to App. Plan source selection, layer
    mapping, coordinate scaling and collision handling before writing target
    anchor metadata.

Why this design:
    Explicit source and destination choices avoid assuming that the currently
    visible font is the intended donor or recipient.

How to use:
    Open the fonts and run Anchors > Copy Anchors Between Fonts. Choose fonts,
    layers, source scope and anchor options, inspect the proposal and run the
    copy action.

Benefit:
    Reuse anchor metadata across fonts with the chosen collision policy and a
    visible target scope.
"""


def main() -> object:
    """Open the complete owned copy dialog through Fly's application facade."""
    from fly.ap.crossfont_anchors import show

    return show()


if __name__ == "__main__":
    main()
