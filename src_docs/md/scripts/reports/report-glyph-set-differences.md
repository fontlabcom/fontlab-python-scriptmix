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
Requires App>=0.2.161.dev0 through Fly in FontLab Python3.11.

Run **Reports > Report Glyph Set Differences** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/8f0cee856f041cea1350786d2a473a7eda70b921cab179ff0d20d7fb3acc5094.py)
<!--/codeinclude-->
