---
this_file: src_docs/md/scripts/kerning/scale-values.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Scale Values

Scale all kerning values by a percentage on one or all masters.

Loosen a Light master's kerning or tighten a display master's in one go: every pair (glyph and
class pairs alike) is multiplied and rounded to whole units, halves away from zero. Pairs that
become 0 can be deleted. The preview lists every change; one Apply is one Undo step.

Run **Kerning > Scale Values** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/6e0fd81379e5fe5a51da62cbb409dba08c7f8e0f7d972715b919e886d47ce7f6.py)
<!--/codeinclude-->
