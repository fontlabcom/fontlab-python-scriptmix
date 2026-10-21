---
this_file: src_docs/md/scripts/masters/display-previous-layer.md
tags: ["Masters"]
categories: ["Masters"]
---

# Display Previous Layer

Show the previous layer of each selected glyph in the Glyph window.

What it does:
    Cycle the displayed layer of the selected glyph slot(s) to the previous
    layer of the same master. Before the first layer, wrap to the last one.

How it works:
    FontLab binds a layer to a master by its name. The text before the first
    "@" (or "#") must equal a master name. So "Bold" and "Bold@ 10:41, 02/03/26"
    belong to master "Bold". Mask (background) and service layers never take part.
    The script reads the shown layer of each selected slot, lists the glyph layers
    of the same master in glyph order, and picks the previous one. A slot with an
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
    this script and to "Display Next Layer" to walk through backups fast.

Benefit:
    One key press compares master, backup and alternate layers in place.

Credit:
    Behaviour after Pedro Arilla's Glyphs script "Display previous layer"
    (Apache-2.0). Independent rewrite. No source code was copied.

Run **Masters > Display Previous Layer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4d90e069d299929200afc2715968dee33631a1823a1a3f76f45a42b5f485c050.py)
<!--/codeinclude-->
