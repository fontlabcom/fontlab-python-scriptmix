---
this_file: src_docs/md/scripts/cleanup/empty-layers.md
tags: ["Cleanup"]
categories: ["Cleanup"]
---

# Empty Layers

Delete the empty extra layers of the selected glyphs.

What it does:
    Remove every extra layer that holds nothing: no shapes, anchors, guides,
    note, recipe, library data, TrueType hints or data, metrics links, and no
    mask that holds any of these. An empty mask of such a layer goes with it. Print the
    deleted layers (the first ten by name) and what was skipped.

How it works:
    The script checks each layer of the selected glyphs against the list of
    data fields above. Master layers, automatic, mask, service, image and
    temporary "|temp|" layers are never deleted on their own. The empty
    mask of a deleted layer is removed first, so no orphan mask stays. All
    deletions run in one Undo step through the shared module fly.ap.history.
    FontLab records the step only for layers plus their glyph, so the
    notification holds the first master layer of each glyph, which stays.
    Then the script checks by layer id that each deleted layer and mask is
    gone.

Why this design:
    - No dialog: the script deletes only layers that carry no data, and
      the deletion is recorded as one Undo step. A preview would show only
      names.
    - The shown (active) layer of a glyph is kept, so FontLab never has to
      pick another shown layer. A locked layer, or one with a locked mask,
      is kept: a lock is a deliberate "keep".
    - The deleted layers and masks hold no shapes, so no component has to
      be retained for Undo (fl#7641).
    - Glyphs with automatic layers and bases of automatic composites (also
      through manual composites) are skipped and named in the result. A
      notification there makes FontLab rebuild the automatic glyphs, and
      Undo does not restore them.
    - The run is refused while FontLab has pending glyph updates.

How to use:
    Select glyphs in the Font window (Select All for the whole font), or
    open one glyph. Run the script. Read the result in the Output panel.
    Use "Layer Cleanup" to delete layers that hold data.

Benefit:
    Leftover empty layers from imports and experiments go in one key press.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (cleanup_empty_layers.py, "Remove Empty Auxiliary Layers").

Run **Cleanup > Empty Layers** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/08d8d53a4aaeb47450dd265d6c5109e7aa5d7117042eb6e42583cd7cd8b90781.py)
<!--/codeinclude-->
