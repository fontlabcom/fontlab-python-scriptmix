---
this_file: src_docs/md/scripts/components/replace-reference.md
tags: ["Components"]
categories: ["Components"]
---

# Replace Reference

Launch the preserved Replace Reference sample.

Purpose: The preserved sample describes this task:
Replace every component that references glyph X with a component of glyph Y,
keeping its position.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Components > Replace Reference in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/components_replace_reference.py

Run **Components > Replace Reference** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/92644df91aecd16f85a391279a5248740931df10010deee3dace82974d5fb448.py)
<!--/codeinclude-->
