---
this_file: src_docs/md/scripts/masters/display-next-layer.md
tags: ["Masters"]
categories: ["Masters"]
---

# Display Next Layer

Show the next layer of each selected glyph in the Glyph window.

What it does:
    Cycle the displayed layer of the selected glyph slot(s) to the next layer
    of the same master. After the last layer, wrap to the first one.

How it works:
    FontLab binds a layer to a master by its name. The text before the first
    "@" (or "#") must equal a master name. So "Bold" and "Bold@ 10:41, 02/03/26"
    belong to master "Bold". Mask (background) and service layers never take part.
    The script reads the shown layer of each selected slot, lists the glyph layers
    of the same master in glyph order, and picks the next one. A slot with an
    explicit layer name gets the new name. A slot that follows the active layer
    gets a new active layer for its glyph.

Why this design:
    - The name rule is the rule of the FontLab source, so the cycle matches the
      Layers panel. The shared module fly.ap.masters.associated_master
      holds it.
    - All slots are planned first. One bad slot stops the run before any change.
    - The script writes no font data. No Undo step is needed.

How to use:
    Open a Glyph window. Select a glyph. Run the script. Assign a shortcut to
    this script and to "Display Previous Layer" to walk through backups fast.

Benefit:
    One key press compares master, backup and alternate layers in place.

Credit:
    Behaviour after Pedro Arilla's Glyphs script "Display next layer"
    (Apache-2.0). Independent rewrite. No source code was copied.

Run **Masters > Display Next Layer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e7808302ee1c19bbb59cf9032bdab8672d31826bd927bde290b7764f99c26376.py)
<!--/codeinclude-->
