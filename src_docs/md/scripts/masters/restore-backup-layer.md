---
this_file: src_docs/md/scripts/masters/restore-backup-layer.md
tags: ["Masters"]
categories: ["Masters"]
---

# Restore Backup Layer

Restore a backup layer into the master layer it belongs to.

What it does:
    Choose a backup layer name, such as "Regular@ 14:05:09, 21/10/26". For
    every selected glyph that has a layer with this name, replace the
    contours of the master layer with copies of the backup contours, move
    same-named anchors to the backup positions and set the backup advance
    width. Optionally delete the backup layer and its mask afterwards.

How it works:
    The script discovers plain "Regular backup" layers and old "Regular@ backup"
    layers. The longest matching master name chooses the restore target;
    no new @ layer is created. Bracket layers ("#") and
    temporary layers are never offered. A non-modal panel shows, per glyph,
    the master, contours and width (master now → after). Restore reads the
    font again and writes all master layers in one Undo step through the
    shared module fly.ap.history, then reads contours, widths, anchors and
    deleted layers back.

Why this design:
    - The master layer object stays. Its components, guides, hints and
      other properties are kept; only outline, anchors and width come back.
      "Use Layer As Master" instead swaps two whole layers in one glyph.
    - The old outline shapes of the master are removed, never edited, so a
      shape that other glyphs share stays intact for them. FontLab clone()
      drops shape notes and names and the raw state and name of nodes
      (fl#8516, fl#8538): the script copies them back and stops when a clone
      has another contour count.
    - Missing anchors are listed, never added. Two anchors with one name, or
      an existing anchor that would move to 0, 0 (FontLab cannot Redo it,
      fl#8527), skip the glyph.
    - Skipped and listed: automatic master layers, glyphs with automatic
      layers, bases of automatic composites (also through manual
      composites), locked master layers, master layers with a metrics link
      or expression, and an empty backup. A backup that is the shown layer
      of its glyph, or that is locked or has a locked mask, is not deleted.
      Apply is refused while FontLab has pending glyph updates.
    - A deleted backup usually holds components. Their shape, shape data
      and builder are read before the edit and retained in the notification.
      The restore is recorded as one Undo step. Edit > Undo of removed components depends on FontLab (fl#7641).

How to use:
    Make backups with "Duplicate Current Layer". Later select the glyphs in
    the Font window. Run the script, choose the backup, tick "Delete the
    backup" if you want, check the table and press Restore.

Benefit:
    Undo a failed redesign of many glyphs at once, long after Edit > Undo
    has lost the steps.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (masters_restore_backup.py, "Restore Backup Layer").
    Known limit: node.clone loses explicit corner smoothness and other
    scalar node properties (fl#8569); a shape clone may lose them too.

Run **Masters > Restore Backup Layer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7a77823479b71e07ce84eecb2f724d62d85be4d84f89fac090006e25774e0772.py)
<!--/codeinclude-->
