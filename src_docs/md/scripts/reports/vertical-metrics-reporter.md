---
this_file: src_docs/md/scripts/reports/vertical-metrics-reporter.md
tags: ["Reports"]
categories: ["Reports"]
---

# Vertical Metrics Reporter

Compare eight stored vertical metrics across every open font and master.

Open the fonts to compare, then run this Reports command. The complete report
compares typoAscender, typoDescender, typoLineGap, hheaAscender, hheaDescender,
hheaLineGap, winDescent and winAscent in source order. Equal values receive a
check mark; differences list every document/master and its value, in stored
order. An unset hhea override is None, distinct from an explicit zero.

FontLab mapping uses master ascender/descender/lineGap, otherData hhea fields,
safeBottom and safeTop. This compares stored native settings; exported or
automatically derived metrics are outside its claim. No active-master switch
is used. No open fonts, unreadable data, deadline or changing source produces
a partial report.

Refresh replaces the entire snapshot. Select and copy text normally. Close
removes this owned modeless panel. This presentation replaces the source's
Output clearing; no font, history, selection, preference or Output writer is
called. Requires App>=0.2.37.dev0 and Fly in FontLab9 Python3.11.
Adapted from Pedro Arilla's Apache-2.0 Vertical metrics reporter.py; provenance
and license are retained in NOTICE and additional-tools.json.

Run **Reports > Vertical Metrics Reporter** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4c51bd52195903544a1913513989c5992256f349ea64fab1042a13ac180cb867.py)
<!--/codeinclude-->
