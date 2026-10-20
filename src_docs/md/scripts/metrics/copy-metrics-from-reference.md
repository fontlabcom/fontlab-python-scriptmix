---
this_file: src_docs/md/scripts/metrics/copy-metrics-from-reference.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Copy Metrics From Reference

Launch the preserved Copy Metrics From Reference sample.

Purpose: The preserved sample describes this task:
Give the selected glyphs the sidebearings or the advance width of a
reference glyph.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Metrics > Copy Metrics From Reference in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/metrics_copy_from_reference.py

Run **Metrics > Copy Metrics From Reference** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/824c0f81cf049c0193d1618201b1dd5d25a67d965691660136d032e11cb2cdcf.py)
<!--/codeinclude-->
