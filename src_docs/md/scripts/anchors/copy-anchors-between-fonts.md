---
this_file: src_docs/md/scripts/anchors/copy-anchors-between-fonts.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Copy Anchors Between Fonts

Copy anchor metadata between two chosen fonts with complete collision options.

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

Run **Anchors > Copy Anchors Between Fonts** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a8ffa04402e1bf42b4c6bd2fedc23b589cfe7ec3464eb04f6e3ccee9139da5be.py)
<!--/codeinclude-->
