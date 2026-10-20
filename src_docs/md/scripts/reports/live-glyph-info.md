---
this_file: src_docs/md/scripts/reports/live-glyph-info.md
tags: ["Reports"]
categories: ["Reports"]
---

# Live Glyph Info

A live panel for the glyph you are working on: widths, side-bearings, bounds and counts per master.

It follows the first glyph selected in the Font window (or the glyph being
edited) and re-reads it twice a second, so edits show up as you make them.
Values that differ between masters stand out. Nothing in the font changes.

Run **Reports > Live Glyph Info** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d950a1a7e3f38b38405c51fadc968acc0dcf571fd8eba5db9adb3cce354f3b10.py)
<!--/codeinclude-->
