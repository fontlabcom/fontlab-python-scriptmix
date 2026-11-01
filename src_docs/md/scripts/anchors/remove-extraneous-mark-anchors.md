---
this_file: src_docs/md/scripts/anchors/remove-extraneous-mark-anchors.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Remove Extraneous Mark Anchors

Remove opposite-side anchors from selected marks on all masters.

What: Remove bottom where _top exists, and top where _bottom exists.
How: Preview conditional removals across named masters. Keep all other pins
and automatic layers; refuse unsafe dependencies before writing.
Why: A conditional rule preserves useful stacking anchors that an
unconditional name-based removal would also delete.
Use: Select glyphs, inspect the non-modal preview, then click Remove.
Benefit: Clean mark attachments consistently across masters. Each
application is recorded as one Undo step.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.

Run **Anchors > Remove Extraneous Mark Anchors** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/bad3945f9902b485ed90a39fdf9ec10e290196cc2102d167e2649084c23b9042.py)
<!--/codeinclude-->
