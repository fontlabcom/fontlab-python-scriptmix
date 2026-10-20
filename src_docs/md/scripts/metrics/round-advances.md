---
this_file: src_docs/md/scripts/metrics/round-advances.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Round Advances

Launch the preserved Round Advances sample.

Purpose: The preserved sample describes this task:
Round advance widths to a step (2, 5, 10 … units), keeping every outline
where it is.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Metrics > Round Advances in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/metrics_round_advances.py

Run **Metrics > Round Advances** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/97a54f04a680028ab64da50311c45921b703d92e00e86ec36097cc192fb09d76.py)
<!--/codeinclude-->
