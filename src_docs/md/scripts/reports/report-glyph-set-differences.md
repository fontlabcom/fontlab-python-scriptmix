---
this_file: src_docs/md/scripts/reports/report-glyph-set-differences.md
tags: ["Reports"]
categories: ["Reports"]
---

# Report Glyph Set Differences

Report Glyph Set Differences using the current font as the original reference.

Open a current reference font; with no other open font the report is empty. Every other open font is compared. Raw filepath headings, target-order extra glyphs and reference-order missing glyphs are preserved.
Refresh repeats the complete original scan; select/copy report text normally.
Close releases only this owned nonmodal report. No font/master activation,
selection/history/preferences/Output/clipboard writer is called. Full native
getter preservation and PythonQt literal-text/lifetime qualification are pending.
Adapted from Jens Kutilek's MIT source; see NOTICE and additional-tools.json.
Requires App>=0.2.26.dev325 through Fly in FontLab Python3.11.

Run **Reports > Report Glyph Set Differences** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9fc47b0a582b7a65c47c4c4eb79634b0478e9f2def17d463c92acdf78d64a1ec.py)
<!--/codeinclude-->
