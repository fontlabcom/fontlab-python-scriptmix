---
this_file: src_docs/md/scripts/masters/selection-layer-navigator.md
tags: ["Masters"]
categories: ["Masters"]
---

# Selection Layer Navigator

Compare selected glyph slots by layer name or by one design axis.

What: A non-modal navigator with Previous and Next. Layer order uses the first
usable selected slot to choose one name for all selected slots, across masters
and auxiliary layers. Skip locked layers in this mode. An unusable reference
gets a named kept row; the next usable slot supplies the reference instead.
Axis mode moves each slot to its next coordinate while keeping
all other axis coordinates fixed. Wrap at either end. Italic / Slant selects
the first axis tagged ital or slnt. All font axes are available.

How: Read the live selection on each click through App. Explicit text-block
layer names stay explicit, so repeated glyphs can show different layers. Slots
without an explicit layer name continue to follow the glyph's active layer.
Changing that active layer also affects other following slots of that glyph.
Read native master positions for intermediate layers; keep layers without
complete coordinates.
In a Font window, axis mode changes the current font master. Layer order needs
a Glyph window. Missing or ambiguous targets produce named kept rows. No
outlines, metrics, preferences or font history are written.

Why: Native Layer > Next (Alt+.) and Layer > Previous (Alt+,) navigate the
active glyph only and skip locked layers.
This panel adds selection-only synchronization, axis filtering, reverse travel
and per-slot results. Master Switcher chooses a named master; this tool finds
the next related coordinate instead. Display Next Layer and Display Previous
Layer cycle each glyph's backups separately within one master.

Usage: Open a font. Run the tool, select glyph slots in a Glyph window, choose
Layer order or an axis, then click Previous or Next. Each click reads the live
selection. After changing fonts, click Use Current Font. The result area lists
every changed or kept slot. Close releases the panel's signal connections.

Benefit: Compare matching drawings while keeping explicit unselected slots fixed.

Credit: Alex Slobzheninov, https://github.com/slobzheninov/Glyphs-Scripts,
Apache-2.0, copyright 2020 Alex Slobzheninov. Independent behaviour rewrite of
App/Next Layer in Selection.py, Previous Layer in Selection.py, Toggle Axis
1.py through Toggle Axis 4.py, Toggle Italic.py and ToggleAxis.py. No source
code, identifiers or comments were copied beyond public API names.

Run **Masters > Selection Layer Navigator** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7c8856746e61d3edfa35930f2d6a433bff35b068897d2b7e626067cfbb48ea20.py)
<!--/codeinclude-->
