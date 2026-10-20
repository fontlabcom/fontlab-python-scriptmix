---
this_file: src_docs/md/scripts/guides/copy-guides-between-masters.md
tags: ["Guides"]
categories: ["Guides"]
---

# Copy Guides Between Masters

Merge or replace glyph guides on explicitly selected target masters.

Select glyphs and choose From, To, merge/replace and optional width scaling.
Inspect every add/remove row, then use Copy. Nonpositive widths cannot be scaled.
Matching target guides retain native colour, tags and geometry; hints are kept.
Unsafe automatic dependants are refused before history. Close releases signals.

Run **Guides > Copy Guides Between Masters** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/218123089612d8496dddef4da8c7f2bfb31858d3ebe1793b3b17409135810f26.py)
<!--/codeinclude-->
