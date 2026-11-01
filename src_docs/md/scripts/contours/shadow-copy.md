---
this_file: src_docs/md/scripts/contours/shadow-copy.md
tags: ["Contours"]
categories: ["Contours"]
---

# Shadow Copy

Add a shifted copy of the outline behind each selected glyph, as its own
element.

What it does:
    For each selected glyph and chosen master, the script copies the contours
    of the layer, moves the copy by a horizontal and a vertical offset, and
    puts it behind the outline as a new element named "shadow". The original
    outline and the advance width do not change.

How it works:
    A non-modal panel lists every glyph and master with its contour count, or
    the reason why the layer is skipped. Apply reads the font again and
    writes all layers in one Undo step through the shared module
    fly.ap.history. The copy is made from each contour with its element
    transform applied; FontLab can drop node names and raw node flags in a
    contour copy (fl#8569), so the script copies them back and clears the
    selection bit. After the write it checks that every layer starts with the
    shadow element and reports any difference. The contour copy and the panel
    are shared (fly.ap.contour_copy, fly.ap.selection_panel).

Copy limits:
    Only node names and raw node flags are repaired (fl#8569); selection is
    cleared. Other node properties and contour names are not repaired.
    Copied contours are merged into one element; source element names and
    notes are not copied.

Why this design:
    - A separate element is easy to recolour, move or delete as one unit, and
      a layer font workflow can split it into shadow glyphs. Filled together
      with the outline it gives an extruded silhouette.
    - Layers with components are skipped: a copy of the contours alone would
      not be the full glyph. Locked layers and layers that already hold a
      shadow element are skipped too.
    - Automatic layers and glyphs with automatic layers are never edited. A
      base of automatic composites is skipped unless you tick "Edit bases of
      auto glyphs anyway": FontLab then rebuilds those composites, can drop
      their anchors and locks, and Undo does not restore them.
    - Apply discloses queued ids and their possible date changes. The script
      does not call UpdateAll (fl#8537). The panel binds to the font that was
      current when it opened.

How to use:
    Select glyphs in the Font window. Run the script. Set the offsets, choose
    the current master or all masters, check the table and press Add Shadow.
    The panel stays open; press "Use selection" after you select other
    glyphs. Each Apply is recorded as one Undo step.

Benefit:
    Shadowed or extruded display styles start from the real outline in one
    step, and the shadow stays a separate element.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_shadow.py, "Shadow Copy").

Run **Contours > Shadow Copy** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1883fe5a05be4c6f3dbeec219721657bc6a48489d308098568ba0dce936c8547.py)
<!--/codeinclude-->
