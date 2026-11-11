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
    The kind comes from the layer role, fly.ap.masters.inspect.model.associated_master,
    and the same backup resolver as Restore Backup Layer: "mask" for a
    background; "backup" for <master> backup <suffix> and legacy @ or
    space-prefixed backups; "alternate" for <master>#... layers, such as
    bracket
    layers; "other" for every other layer. Master layers, service layers,
    image layers and temporary "|temp|" layers are never listed. The delete
    runs in one Undo step through the shared module fly.ap.core.history.glyphs. FontLab
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
      is recorded as one Undo step. Edit > Undo of removed components depends
      on FontLab (fl#7641).
    - To clear the backgrounds of the whole font, use Cleanup > Clear All
      Layer Backgrounds or Clear Master Backgrounds: they check the whole
      font mapping first. This panel is for mixed cleanup of a selection.
    - Delete discloses queued ids and their possible date changes. The panel
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

## Source identity

SHA256: `5a240c54715580d83d5d65687b7aabbb3502e58878dbd70ab91680049601f013`

[Python source at `3dc87d8a0e3d`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3dc87d8a0e3dec803dc9255436da39eb19abefb2/Scripts/Masters/Layer%20Cleanup.py)
