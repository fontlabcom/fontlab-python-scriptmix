---
this_file: src_docs/md/scripts/reports/report-composite-differences.md
tags: ["Reports"]
categories: ["Reports"]
---

# Report Composite Differences

Report Composite Differences using the current font as the original reference.

Open two or more fonts. Only the first other open font is compared, using each font selected named master. Ordered component names and source-order missing glyphs are reported; only exact .sc/.pcap suffixes are excluded from missing rows.
Refresh repeats the complete original scan; select/copy report text normally.
Close releases only this owned nonmodal report. No font/master activation,
selection/history/preferences/Output/clipboard writer is called. Full native
getter preservation and PythonQt literal-text/lifetime qualification are pending.
Adapted from Jens Kutilek's MIT source; see NOTICE and additional-tools.json.
Requires App>=1.2.0 through Fly in FontLab Python3.11.

Run **Reports > Report Composite Differences** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `b0adc37383493640eeffa2a3efd0985dea1053bc1d86a48d50ca7b34d1ac1fce`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Reports/Report%20Composite%20Differences.py)
