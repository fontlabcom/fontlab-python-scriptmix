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
    "@" (or "#") identifies master and alternate layers. Backups use
    <master> backup <suffix>; legacy @ and space-prefixed backups also take
    part, resolved by the longest master prefix. Masks and service layers stay out.
    The script reads the shown layer of each selected slot, lists the glyph layers
    of the same master in glyph order, and picks the previous one. A slot with an
    explicit layer name gets the new name. A slot that follows the active layer
    gets a new active layer for its glyph.

Why this design:
    - fly.ap.masters.inspect.model.associated_master resolves native layer names; the same
      backup resolver as Restore Backup Layer adds plain backup names.
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

## Source identity

SHA256: `3331bdaece5f15c49d130e0c4cb457cbc4e48f107846c704d37b7f69affdcb7b`

[Python source at `b52710a04ed5`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/b52710a04ed5e9e3759b7086daeb0b09ec65b6f3/Scripts/Masters/Display%20Previous%20Layer.py)
