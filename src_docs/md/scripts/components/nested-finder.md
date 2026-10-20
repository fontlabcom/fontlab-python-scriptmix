---
this_file: src_docs/md/scripts/components/nested-finder.md
tags: ["Components"]
categories: ["Components"]
---

# Nested Finder

Launch the preserved Nested Finder sample.

Purpose: The preserved sample describes this task:
Find components whose base glyph is itself a composite (nested components),
and unnest them.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Components > Nested Finder in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/components_nested_finder.py

Run **Components > Nested Finder** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/66fea89671e3cf8c53f66db71d0cdc3fae69e0501b78ba81d68b82c91f82d4a5.py)
<!--/codeinclude-->
