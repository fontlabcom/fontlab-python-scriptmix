---
this_file: src_docs/md/scripts/metrics/scale-advances.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Scale Advances

Launch the preserved Scale Advances sample.

Purpose: The preserved sample describes this task:
Scale the advance widths of the selected glyphs by a percentage, each
outline staying centred.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Metrics > Scale Advances in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/metrics_scale_advances.py

Run **Metrics > Scale Advances** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/afe9403bffa87d29a820b95708dafb141206e80d29f214ec120d45dc6b599e7c.py)
<!--/codeinclude-->
