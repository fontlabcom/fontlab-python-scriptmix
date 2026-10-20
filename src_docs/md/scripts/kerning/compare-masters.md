---
this_file: src_docs/md/scripts/kerning/compare-masters.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Compare Masters

Line up every kerning pair across all masters and flag the ones that look inconsistent.

Each row is one pair (glyph or @class sides) with its value on every master; a pair missing
on a master shows a dash. Rows are flagged when the sign flips between masters, when a pair
exists on some masters only, or when neighbouring masters differ by more than the jump
threshold. Tick "Only flagged" to proof just those. Nothing is edited.

Run **Kerning > Compare Masters** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/f0051ebeee2e17c7cdb3c1e794334fbcc3bae733c7169eb906d3667207dfb872.py)
<!--/codeinclude-->
