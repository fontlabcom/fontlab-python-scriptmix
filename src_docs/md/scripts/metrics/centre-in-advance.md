---
this_file: src_docs/md/scripts/metrics/centre-in-advance.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Centre In Advance

Launch the preserved Centre In Advance sample.

Purpose: The preserved sample describes this task:
Centre the outlines of the selected glyphs in their advance width,
optionally with a new width.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Metrics > Centre In Advance in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/metrics_center_in_advance.py

Run **Metrics > Centre In Advance** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1a8e6715eca8df821a3d11b66fc3c85e917b80d3cb749319788451622b290eef.py)
<!--/codeinclude-->
