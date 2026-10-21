---
this_file: src_docs/md/scripts/components/set-default-figures.md
tags: ["Components"]
categories: ["Components"]
---

# Set Default Figures

Set one figure family as components in the default digit cells.

What: Choose lining (.lf), oldstyle (.osf), tabular lining (.tf), or tabular
oldstyle (.tosf) figures. Missing default digit cells are created. With Replace
own contours on, their old contours are removed; turn it off to
keep them. Their components, widths and kerning class memberships follow
the chosen figures on every master. Unicode assignments stay.
How: Preview exact base names and set explicit base and master-layer names. No automatic layer is made.
Why: One complete set avoids mixing figure styles between glyphs or masters.
Use: Choose the set and the contour option, inspect the table, then Apply.
Benefit: Ten digits across every master. Each new glyph is recorded as its own Undo step.
Changed kerning memberships are recorded in the same Undo step, or as one more
Undo step when no outlines are filled. Circular references, automatic targets and targets without
a safe plain component to copy are listed as kept; other targets can change. Components are placed at the origin with the source advance; Glyphs'
automatic component alignment has no identical FontLab control here.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Components/Set default figures.py, Apache-2.0.
Repository: https://github.com/pedroarilla/glyphs-scripts . No source code copied.

Run **Components > Set Default Figures** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/2504925d059cb56480971e8de5ec560ef9fc53e6d6ae791ece533c65f2415648.py)
<!--/codeinclude-->
