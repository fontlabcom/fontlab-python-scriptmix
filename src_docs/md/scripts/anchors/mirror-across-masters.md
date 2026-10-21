---
this_file: src_docs/md/scripts/anchors/mirror-across-masters.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Mirror Across Masters

Copy the anchors of one master into the other masters of the same glyphs.

What: Takes the anchors of a source master. Moves the same-named anchors in the
ticked target masters, and adds the missing ones. Optional: add only the
missing anchors.

How: The x value can scale with the advance-width ratio, target over source.
An anchor in the middle of a narrow Light glyph then lands in the middle
of the wide Bold glyph. Positions round half up to whole units. A new
anchor gets its name-derived appearance.

Why: One master carries the reference design. The others follow in one step.
This is a start: interpolation or hand work refines the result.

Use: Select glyphs. Run the script. Choose the source master. Tick the target
masters. Check the table. Press Mirror.

Benefit: Fast, consistent anchor sets in all masters of many glyphs.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- an existing anchor would move to 0, 0 (FontLab cannot Redo that);
- a glyph is the base of an automatic composite (FontLab rebuilds the
  composite and Undo does not restore it);
- several anchors on a layer share a name (the edit is ambiguous);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads every value back. It reports any value
that FontLab did not keep, for example under a strong rounding preference.
If FontLab fails part-way, the error says that native changes may remain.
Edit > Undo restores the font.

Source: the author's own FontLab sample
anchors_mirror_across_masters.py, Apache-2.0.
Independent rewrite for the current FontLab 9 API.

Run **Anchors > Mirror Across Masters** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c0ca3fec771f78a0f01de54ed2f1aa37325b6664f092471dba6b4c5506650878.py)
<!--/codeinclude-->
