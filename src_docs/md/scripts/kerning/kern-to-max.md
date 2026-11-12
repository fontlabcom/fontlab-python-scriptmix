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

## Source identity

SHA256: `b29b820eafbdfd05a2760d8dd1dc6b4b8774e278fd0e913874b3f6170a5ae3cd`

[Python source at `b52710a04ed5`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/b52710a04ed5e9e3759b7086daeb0b09ec65b6f3/Scripts/Kerning/Kern%20To%20Max.py)
