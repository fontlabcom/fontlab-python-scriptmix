---
this_file: src_docs/md/scripts/components/set-component-locations.md
tags: ["Components"]
categories: ["Components"]
---

# Set Component Locations

Set or reset component source locations across selected glyphs and masters.

What: Give components a font-axis location, such as #wt=650,wd=100. Reset
sets Base layer name to the host master layer, as Reset to current layer does.
How: Preview each occurrence and its old and new source-layer choice. Set
one coordinate per declared axis and component/master occurrence. Each row
starts at the component's current location. Set writes only edited rows,
and keeps an existing @node suffix. Write componentLayer in
place through the shared geometry history writer, then read it back. Each
write is recorded as one Undo step. No source glyph or layer is renamed.
Why: Select component instance and Reset to current layer work on individual
components. This panel adds batch scope, per-master values and kept rows.
A multi-master base already answers font-axis locations; no conversion is
needed. Glyph-local axes use source-layer locations. Use Set Intermediate
Layer to create those layers; this panel uses the font's declared axes.
Use: Select glyphs. Run this tool. Choose Set or Reset, the component scope
and the host masters. Optionally enter an exact source-name filter. Review
the preview before Apply. Selected components are read from each glyph's
active layer and matched by shape position and base name in other masters.
All components in selected glyphs is the default. For Selected components,
select components in a Glyph window first. Reload selection reads current
coordinates and clears pending field edits. In Set mode, Apply without edits
writes nothing.
Benefit: Tune or reset many instances without repeating per-component edits.
Automatic layers, their owners and bases, locked layers, shared element data
and missing sources are listed as kept. Other eligible occurrences still
write. Set refuses unknown axes and non-finite or out-of-range coordinates.

Credit: Independent behaviour rewrite after Fernando Díaz, Reset Type Studio,
Glyphs-Scripts/Smart Components/Values for Smart Components.py and Selected
to Normal Components.py. Apache-2.0, declared in README.md; no LICENSE file.
Copyright 2025 Fernando Díaz & Reset Type Studio.
Repository: https://github.com/Reset-Type-Studio/Glyphs-Scripts .
No source code was copied. Reset sets each base layer to its host master
layer without deleting the source glyph's variation layers.

Run **Components > Set Component Locations** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/87df5fb922a121df3d5ca11507dbbfd26cb2cf344ebc9b19392566093ddb45bc.py)
<!--/codeinclude-->
