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

SHA256: `7a7709373a95a0e54bac32d880aa62234ceade238e1062bb2961b0157d17d428`

[Python source at `ba6f2dfbe4d6`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/ba6f2dfbe4d6759bc53d77827e64a3d6ccee96e3/Scripts/Reports/Report%20Composite%20Differences.py)
