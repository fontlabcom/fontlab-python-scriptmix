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
Requires App>=1.2.0 through Fly in FontLab Python3.11.

Run **Reports > Report Glyph Set Differences** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `6e3ca96f20b12320ec9e5ae720ad51260edbd20a324523125f2e253d9a1232cd`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Reports/Report%20Glyph%20Set%20Differences.py)
