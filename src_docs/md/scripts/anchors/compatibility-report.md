---
this_file: src_docs/md/scripts/anchors/compatibility-report.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Compatibility Report

Compare anchor names across masters: a glyph whose masters carry different anchors cannot interpolate them.

The tree lists each glyph with its anchor count per master; expand a glyph to see
which master lacks which anchor. Mismatches are flagged and listed first.
Auto layers show "auto" and are not compared: FontLab rebuilds their anchors.
Double-click a glyph to select it in the Font window. Nothing is changed.

Run **Anchors > Compatibility Report** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/35038e202e171e0301a981249d9846f1327e9fad8aa80c727f4254baa3a8edc8.py)
<!--/codeinclude-->
