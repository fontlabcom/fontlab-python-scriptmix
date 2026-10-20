---
this_file: src_docs/md/scripts/font-info/calculate-vertical-metrics.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Calculate Vertical Metrics

Set hhea, Win (and optionally OS/2 typo) vertical metrics to enclose every glyph, per master.

Bounds are rounded outward and can be padded. FontLab's master ascender, descender and
line gap ARE the OS/2 typo values (measured), so Typo is off by default: turning it on
moves the font's ascender/descender lines to the glyph bounds. Preview before Apply.

Open with a font active. Choose current or all masters, padding, line gap and the
metric groups to update. Review the table, then choose Apply. Bounds are captured
when the panel opens; reopen after outline edits. Large scans stop before edits.
Empty masters are skipped. The undoable edit preserves outlines and unselected
metric groups. Reopen after switching the font or active master.

Run **Font Info > Calculate Vertical Metrics** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/496f21b000f65b652e6547cb00a74db9d24d0a23f924e14f2e967612240f4126.py)
<!--/codeinclude-->
