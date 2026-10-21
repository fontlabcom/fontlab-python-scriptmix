---
this_file: src_docs/md/scripts/masters/layer-cleanup.md
tags: ["Masters"]
categories: ["Masters"]
---

# Layer Cleanup

List the extra layers of the selected glyphs and delete the ticked ones.

What it does:
    Fonts collect masks, backups, alternates and experiment layers. The
    panel lists every non-master layer of the selected glyphs with its kind
    and contour count. Tick rows one by one, or tick a whole kind with one
    button. "Delete Ticked" removes the ticked layers.

How it works:
    The kind comes from the layer role and the FontLab name rule
    (fly.ap.masters.associated_master): "mask" for a mask (background)
    layer; "backup" for "<master>@ ..." layers, as "Duplicate Current Layer"
    makes them; "alternate" for "<master>#..." layers, such as bracket
    layers; "other" for every other layer. Master layers, service layers,
    image layers and temporary "|temp|" layers are never listed. The delete
    runs in one Undo step through the shared module fly.ap.history. FontLab
    records the step only for layers plus their glyph, so the notification
    holds a layer that stays: the body layer of a deleted mask, else the
    first master layer. The script then checks by layer id that every
    ticked layer is gone.

Why this design:
    - Nothing is ticked at the start. A delete is explicit.
    - The shown (active) layer of a glyph and locked layers are listed but
      cannot be ticked: FontLab would have to pick another shown layer, and
      a lock is a deliberate "keep".
    - Glyphs with automatic layers and bases of automatic composites (also
      through manual composites) are listed but cannot be ticked. A
      notification there makes FontLab rebuild the automatic glyphs, and
      Undo does not restore them.
    - A deleted body layer leaves its mask. The mask has its own row: tick
      both to remove both.
    - The components of the deleted layers (shape, shape data, builder) are
      read before the edit and retained in the notification. The deletion
      is recorded as one Undo step. Edit > Undo of removed components depends on FontLab (fl#7641).
    - To clear the backgrounds of the whole font, use Cleaning > Clear All
      Layer Backgrounds or Clear Master Backgrounds: they check the whole
      font mapping first. This panel is for mixed cleanup of a selection.
    - Delete is refused while FontLab has pending glyph updates. The panel
      binds to the font that was current when it opened.

How to use:
    Select glyphs in the Font window (Select All for the whole font). Run
    the script. Tick rows or press a kind button. Press Delete Ticked. The
    deletion is recorded as one Undo step.

Benefit:
    A clean Layers panel and a smaller file, without clicking through every
    glyph.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (masters_layer_cleanup.py, "Layer Cleanup").

Run **Masters > Layer Cleanup** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/99af551cc8e6fecf08f8d7a0d7bca02d43eafd333954717409af26e466b1886d.py)
<!--/codeinclude-->
