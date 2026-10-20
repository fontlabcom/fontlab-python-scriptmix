---
this_file: src_docs/md/scripts/cleanup/select-unreferenced-glyphs.md
tags: ["Cleanup"]
categories: ["Cleanup"]
---

# Select Unreferenced Glyphs

List unencoded glyphs that nothing references, and select them in the Font window for review.

A glyph counts as referenced when it has a code point, is used as a component or in an
auto recipe on any layer, is named in the OpenType feature source, or belongs to a feature
class that the source uses. Candidates are often alternates waiting for a feature, so the
script only selects them; it never deletes. Feature files pulled in with include() cannot
be read and stop the scan.

Run **Cleanup > Select Unreferenced Glyphs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a5e8d7e44df8719de8e0ac3d10f0b28d04b277e141a9594339c5abf1d921cdbb.py)
<!--/codeinclude-->
