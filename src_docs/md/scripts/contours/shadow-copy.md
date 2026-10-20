---
this_file: src_docs/md/scripts/contours/shadow-copy.md
tags: ["Contours"]
categories: ["Contours"]
---

# Shadow Copy

Launch the preserved Shadow Copy sample.

Purpose: The preserved sample describes this task:
Add a shifted copy of the selected glyphs' outlines as a separate shadow
element.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Contours > Shadow Copy in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/generate_shadow.py

Run **Contours > Shadow Copy** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c109d95f79a126bd37eb608aa4fba18c5a10b323d40a80d2ab6f9e449e937f39.py)
<!--/codeinclude-->
