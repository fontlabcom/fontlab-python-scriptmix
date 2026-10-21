---
this_file: src_docs/md/scripts/masters/duplicate-current-layer.md
tags: ["Masters"]
categories: ["Masters"]
---

# Duplicate Current Layer

Copy the selected glyph layer into a new time-stamped layer.

What it does:
    Make an exact copy of the shown layer of each selected glyph. The copy is a
    normal body layer named "<Master>@ HH:MM:SS, DD/MM/YY". It stays attached to
    the same master, so "Display Next Layer" finds it.

How it works:
    FontLab binds a layer to a master by the name text before the first "@".
    The script keeps that prefix, adds the time stamp, and adds " (2)", " (3)"
    when the name is taken. It clones the layer, renames the clone, and adds it
    to the glyph. One notification covers all new layers: one Undo step.

Why this design:
    - A plain backup layer never joins interpolation: FontLab does not treat the
      "@" name as a second master location.
    - The time stamp has seconds. Two quick copies do not collide.
    - Mask (background), service and automatic layers are refused. Their copies
      would break background naming or re-run automatic recipes. A glyph that
      is a base of an automatic layer is refused too: FontLab cannot undo it.
    - FontLab clone() drops shape notes and names, active and selected flags,
      and the raw state and name of nodes. The script copies them back and
      checks the shape count before it adds the layer.
    - Every layer is checked before the first change.

How to use:
    Select glyphs (Font window) or open a Glyph window. Run the script. Use it
    before a risky edit, then use "Use Layer As Master" to swap back if needed.

Benefit:
    A safe copy in one key press, without the Layers panel dialog.

Credit:
    Behaviour after Pedro Arilla's Glyphs script "Duplicate current layer"
    (Apache-2.0). Independent rewrite. No source code was copied.
    Known limit: clone() recalculates smooth flags (fl#8516); the script
    restores node states.

Run **Masters > Duplicate Current Layer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/b1a7f1ef25312b4ee64916b9fa776890091739d5af1cd66f4501b644d252e909.py)
<!--/codeinclude-->
