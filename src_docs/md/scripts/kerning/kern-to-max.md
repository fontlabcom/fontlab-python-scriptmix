---
this_file: src_docs/md/scripts/kerning/kern-to-max.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Kern To Max

Set a selected pair to minus half the narrower advance width.

What: Set class kerning, or glyph kerning without a class, on the shown master.
How: Read two adjacent selected master layers. Truncate half the smaller
advance toward zero, negate it, and pass a typed pair to the shared kerning writer.
Why: Unlike entering a value in the Metrics bar, this derives the limit from
the narrower advance in one action, independent of outline bounds. It
does not measure collisions. Ambiguous side-group membership is refused.
Use: Select exactly two adjacent glyph slots in a Glyph window and run.
Capture includes selected OR active slots. An active slot outside the pair
makes the count larger and is refused; a lone active slot is also refused.
Explicit selection replaces the Glyphs insertion-cursor fallback.
Benefit: One shortcut gives a consistent tight starting value. Each changing
action is recorded as one Undo step. No panel or font-wide redraw is needed.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Kerning/Kern to max.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.

Run **Kerning > Kern To Max** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7645322da9c75fbdd20a18ce7d68437513b7b4eb69434f203cde853779ec956a.py)
<!--/codeinclude-->
