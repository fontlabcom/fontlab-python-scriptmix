---
this_file: src_docs/md/scripts/masters/show-all-layers.md
tags: ["Masters"]
categories: ["Masters"]
---

# Show All Layers

Open every foreground layer of the selected glyph occurrences in a proof.

What: Show masters and auxiliary layers by their exact names in a new tab.
How: Capture the current selection, preserve occurrence order, and submit
explicit glyph/layer symbols through the shared exact-layer tab helper.
Why: Unicode and slash-text conversion can show the wrong glyph or layer.
The Masters panel shows one glyph’s masters. This proof also includes
auxiliary layers and several glyphs. Masks and service layers are omitted
because they are not foreground symbols.
Use: Select glyphs in a Font window or Glyph window, then run. Capture includes
selected or active slots. Each glyph has its own scan budget. No dialog.
Benefit: Compare all stored foreground variants without repeated layer switches.
The script writes no font data and makes no Undo step. The proof uses one row;
it preserves repeated selected glyph occurrences.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Glyphs/Show All Layers.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.

Run **Masters > Show All Layers** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7055021be7390ff7c868e5052730519be738672defbaa131fc1f71e7091f41ff.py)
<!--/codeinclude-->
