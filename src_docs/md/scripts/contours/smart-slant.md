---
this_file: src_docs/md/scripts/contours/smart-slant.md
tags: ["Contours"]
categories: ["Contours"]
---

# Smart Slant

Slant outlines and compensate the change in their horizontal bounds.

What: Apply a slant, then preserve sidebearings or the original ink centre.
How: Measure the actual cubic bounds before and after the shear. Keeping
sidebearings aligns the left ink edge and adjusts advance by the ink-width
change. Centre mode keeps advance and centres the new ink on the old ink.
Why: A plain shear can shift the drawing within its advance. Compensation
gives a controlled starting point for an italic, across selected masters.
Native Tools > Transform > Slant, Slant by Italic Angle and Actions > Oblique
do not provide this spacing compensation. Scripts/Contours/Slant.py keeps
the advance unchanged. This tool keeps both sidebearings by adjusting the
advance, or keeps the original ink centre at unchanged advance.
Use: Select glyphs, run this panel, choose angle and spacing mode, inspect
the preview, then Slant. Positive angles lean right. Reload new selections.
Benefit: Repeat the same optical placement over glyphs of different heights.

Anchors follow the same matrix when enabled. Guides and metric expressions
stay. Components, open contours and locked shapes are kept and listed;
other glyphs can still be edited. Automatic
glyphs and their bases follow the panel's geometry policy. Each Apply is
recorded as one Undo step. FontLab can round the baked coordinates.
Font italic-angle metadata is not changed by this drawing tool.

Independent behaviour-only rewrite after Fernando Díaz, Reset Type Studio,
https://github.com/Reset-Type-Studio/Glyphs-Scripts, Paths/Smart Slant.py.
Apache-2.0 declared in README.md; no separate LICENSE file. No code copied.

Run **Contours > Smart Slant** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c4456ee03f18fcf0a52bac718fda6b253e3668fa4c9a8799b02531bebfa4e2a0.py)
<!--/codeinclude-->
