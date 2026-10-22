---
this_file: src_docs/md/scripts/masters/master-text-comparison.md
tags: ["Masters"]
categories: ["Masters"]
---

# Master Text Comparison

Compare comma-separated text across all masters of the opening font.

Start with blank custom text or select one of four original fallback lists.
A local UTF-8 MasterBlaster-presets.txt in the opening working directory loads
on opening; an absolute path also supports manual loading. Each physical line
is an editable comma-separated list; BOM and platform newlines are normalized.
Selecting a preset preserves custom input. Double-click runs that preset
immediately; List as Masters prefers nonempty custom text, then the selection.
Stacked (0) ends every copy with newline and each group with another newline.
Side-by-side (1, default) ends every copy with literal space, each group with
newline, including the final group. Available characters, whitespace and
repetitions retain their order; complete sanitation and alias diagnostics are
shown before proofing. Explicit Names mode adds /glyphname for unencoded names.
Tool-owned custom/layout settings save after successful proof; Close saves
window geometry. No selection and blank custom disables List as Masters.
Exact native binding, special text/IME fidelity and rendering remain pending.

Credit: Luke Prowse (LukeProwse), NaN-xyz/GlyphsApp-Scripts,
MasterBlaster/MasterBlaster.py, MIT (root LICENSE), copyright 2019 LukeProwse.
The upstream README also declares Apache-2.0.
https://github.com/NaN-xyz/GlyphsApp-Scripts
Independent rewrite of behaviour. Only attributed fallback list VALUES are
retained as behavioral data; no original executable or preset file is shipped.

Run **Masters > Master Text Comparison** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a90920a023fcbc419da46bee88ca61f5cbc910fc561f2e9aa5e3238a4c467bdc.py)
<!--/codeinclude-->
