---
this_file: src_docs/md/scripts/reports/report-glyph-set-differences.md
tags: ["Reports"]
categories: ["Reports"]
---

# Report Glyph Set Differences

Report Glyph Set Differences using the current font as the original reference.

Open two or more fonts. Every other open font is compared. Raw filepath headings, target-order extra glyphs and reference-order missing glyphs are preserved.
Refresh repeats the complete original scan; select/copy report text normally.
Close releases only this owned nonmodal report. No font/master activation,
selection/history/preferences/Output/clipboard writer is called. Full native
getter preservation and PythonQt literal-text/lifetime qualification are pending.
Adapted from Jens Kutilek's MIT source; see NOTICE and additional-tools.json.
Requires App>=0.2.161.dev0 through Fly in FontLab Python3.11.

Run **Reports > Report Glyph Set Differences** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/404a9732d0a4385c1183a64bdbe3ae3040e7c7f2e99531c70f962755e5165f39.py)
<!--/codeinclude-->
