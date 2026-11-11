---
this_file: src_docs/md/scripts/components/set-default-figures.md
tags: ["Components"]
categories: ["Components"]
---

# Set Default Figures

Set one figure family as components in the default digit cells.

What: Choose lining (.lf), oldstyle (.osf), tabular lining (.tf), or tabular
oldstyle (.tosf) figures. Missing default digit cells are created. Existing own
contours stay by default, so the new components can overlap the old drawing.
Enable Replace own contours to remove those contours. Components, widths and
kerning class memberships follow the chosen figures on every master. Existing
anchors and Unicode assignments stay. The chosen family is remembered; Replace
own contours starts unchecked each time. Window position and size are restored
when reopened; closing saves them even without Apply.
How: Preview exact base names and set explicit base and master-layer names. No
automatic layer is made.
Why: One complete set avoids mixing figure styles between glyphs or masters.
Use: Choose the set and the contour option, inspect the table, then Apply.
Benefit: Ten digits across every master. Each new glyph is recorded as its own
Undo step.
Changed kerning memberships are recorded in the same Undo step, or as one more
Undo step when no outlines are filled. Circular references, automatic targets
and targets without
a safe plain component to copy are listed as kept; other targets can change.
Components are placed at the origin with the source advance; Glyphs'
automatic component alignment has no identical FontLab control here.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Components/Set default figures.py, Apache-2.0.
Repository: https://github.com/pedroarilla/glyphs-scripts . No source code
copied.

Run **Components > Set Default Figures** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `5c85f757a55663252e39bb53006b7b6db95f612374efca5f91bf32169ab26a78`

[Python source at `6064e3e08a50`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6064e3e08a50137c10a3e1789855917be9874916/Scripts/Components/Set%20Default%20Figures.py)
