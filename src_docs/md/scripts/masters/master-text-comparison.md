---
this_file: src_docs/md/scripts/masters/master-text-comparison.md
tags: ["Masters"]
categories: ["Masters"]
---

# Master Text Comparison

Open comparison tabs whose glyph slots name exact master layers.

What: Resolve comma-separated words and repeat each word on every master.
How: Use proof.font_maps for first-encoded-name-wins Unicode lookup, check all
requested layers, then call public named_tab.open_layer_rows once.
The shared tab helper saves and restores shape activation flags.
Use: Enter words or /glyphname tokens and press Open comparison. Side by side
puts each word group on one row, with a space between master copies.
Stacked puts each word/master on one row, with blank group separators.
Keep the non-modal panel open for repeated proofs. Enter an absolute UTF-8
preset-file path and press Load presets; each nonempty line is one preset.
The path stays in the panel until it closes. BOM and line endings are normalized;
NUL, NBSP and Unicode line/paragraph separators are refused.
Why: Over FontLab's Glyph-window multi-master text views and Text By Master,
this adds comma-separated word groups and file presets with exact per-slot layers.
Benefit: Prepare repeatable master comparisons from one short word list.

Credit: Luke Prowse (LukeProwse), NaN-xyz/GlyphsApp-Scripts,
MasterBlaster/MasterBlaster.py, MIT (root LICENSE), copyright 2019 LukeProwse.
The repository README also declares Apache-2.0.
https://github.com/NaN-xyz/GlyphsApp-Scripts
Independent rewrite of behaviour. No source code or preset text was copied.

Run **Masters > Master Text Comparison** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/71df63167f60cefd2de6c6b3e363f2175b63ba1dceffb6945cb9ff2a52e3c260.py)
<!--/codeinclude-->
