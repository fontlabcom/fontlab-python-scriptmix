---
this_file: src_docs/md/scripts/masters/copy-outline-to-mask.md
tags: ["Masters"]
categories: ["Masters"]
---

# Copy Outline To Mask

Copy the outline of each selected glyph into the mask of its master layer.

What it does:
    For each selected glyph and chosen master, put a copy of the contours of
    the master layer into its mask (background) layer. The mask is created
    when it is missing. "Replace mask" removes what the mask holds first;
    "Add to mask" keeps it. The master layer does not change.

How it works:
    A non-modal panel lists every glyph and master with three numbers:
    contours in the outline, contours in the mask now (plus its components,
    which "Replace mask" also removes), contours in the mask after the copy.
    Apply reads the font again, then writes all masks in one Undo step
    through the shared module fly.ap.history. Existing masks join the
    history list before the edit; new masks join the notification as
    created objects. "Replace mask" removes the old mask shapes one by one.
    The shape, shape data and builder of each removed component are read
    before the edit and retained in the notification. The removal is
    recorded as one Undo step. After the write the script counts
    the mask contours again, checks that no old component is left, and
    reports any difference.

Why this design:
    - Only contours are copied. Components stay in the body: a mask is a
      drawing reference, and a component in a mask would follow later edits
      of its base glyph.
    - Each outline shape is cloned whole, so its own transform stays. FontLab
      clone() drops shape notes and names and the raw state and name of
      nodes (fl#8516, fl#8538). The script copies them back, and clears
      selection bits: a mask must not look selected. A clone with another
      contour count stops the run.
    - Edit > Undo of removed components depends on FontLab (fl#7641).
    - Automatic layers, glyphs with automatic layers, bases of automatic
      composites (also through manual composites) and locked layers are
      listed and skipped. A notification there makes FontLab rebuild the
      automatic glyphs, and Undo does not restore them.
    - Apply discloses queued ids and their possible date changes. The panel
      binds to the font that was current when it opened.

How to use:
    Select glyphs in the Font window. Run the script. Choose the current
    master or all masters, and the mode. Check the table. Press Copy. The
    panel stays open; press "Use selection" after you select other glyphs.

Benefit:
    A reference copy of the current drawing behind every glyph, before a
    redesign, in one step and one Undo.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (masters_copy_to_mask.py, "Copy Outline to Mask").
    Known limit: node.clone loses explicit corner smoothness and other
    scalar node properties (fl#8569); a shape clone may lose them too.

Run **Masters > Copy Outline To Mask** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0c326bc183ced9d824248080338aec041a858ec00e4a9f380683b9391383341e.py)
<!--/codeinclude-->
