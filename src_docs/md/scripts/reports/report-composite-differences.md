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
Requires App>=0.2.26.dev325 through Fly in FontLab Python3.11.

Run **Reports > Report Composite Differences** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1e1e37861770b55681b3eaadaa37d3cf3316450c7cf0c16f3c105e52847ddeba.py)
<!--/codeinclude-->
