---
this_file: src_docs/md/scripts/components/make-lower-unicase.md
tags: ["Components"]
categories: ["Components"]
---

# Make Lower Unicase

Make uppercase cells show lowercase components on every master.

What: Map encoded lowercase letters to their single-character uppercase cells.
Use existing uppercase glyphs only; list missing targets and later mappings as
kept. Existing uppercase contours, components and anchors are replaced; image
and sticker shapes stay. Target widths and kerning class memberships
follow the lowercase on each master. Multi-character uppercase mappings stay.
How: Use Unicode case data and current-font glyph names. Make plain components
from a plain component already in this font, with an explicit master layer.
Why: A plain component remains editable without automatic-layer rebuilds.
Use: Preview all uppercase/lowercase pairs, then Apply and confirm the font and
counts. Canonical round-trip lowercase comes first, then Unicode and glyph-name
order. Later sources for one target stay; their rows say kept. Existing Unicode
assignments stay. Replacing existing outlines is recorded as one Undo step.
Benefit: Build a lowercase unicase design consistently across every master.
Automatic targets and bases of automatic composites are refused. Circular
references are kept. Existing targets without a safe plain component to copy
are listed as kept; other eligible targets can still change. This tool creates
no capital glyph whose name is missing.

Independent behaviour rewrite after Pedro Arilla, based on Georg Seifert's
Make Unicase Font idea, glyphs-scripts/Components/Make lower-unicase font.py,
Apache-2.0. Repository: https://github.com/pedroarilla/glyphs-scripts .
No source code copied.

Run **Components > Make Lower Unicase** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/bd408850cfd13a467af71f1011ee0e94ace24b955898b47e49280ca33414dca2.py)
<!--/codeinclude-->
