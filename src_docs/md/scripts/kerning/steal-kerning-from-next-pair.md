---
this_file: src_docs/md/scripts/kerning/steal-kerning-from-next-pair.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Steal Kerning From Next Pair

Match one selected pair's outline gap to the following pair at a set height.

What: Measure four consecutive same-master glyph slots as two pairs. Set the
first pair's kerning so its gap matches the second pair at the chosen height.
How: Read own and transformed component contours. Elevate quadratic spans to
cubics, flatten with the shared twelve-step curve helper, then find horizontal
ray crossings. Write the integer gap difference plus the second pair's effective
kerning through the shared checked kerning writer. Preserve target exceptions.
Why: The Metrics bar accepts a kerning value, but does not derive it from two
outline gaps at a specified height. Curve flattening is an approximation.
Use: Select four adjacent glyphs in one Glyph-window text block. The capture
includes selected OR active slots; an extra active slot or a lone active slot
is refused. Set Height (default: half the shown master's x-height), then Preview
and Apply. Use a height that crosses all four outlines. No cursor API is needed.
Benefit: Compare pairs such as AV and VA at a repeatable measurement height.
The non-modal panel keeps the height. Each changing action is recorded as one
Undo step. Zero gaps are valid; a computed zero removes the target pair record.
Open contours are skipped and reported by glyph name. A missing closed-outline
crossing refuses the complete action. Flat edges at the measuring height count.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Kerning/Steal Kerning From Next Pair at Cursor's Y.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.

Run **Kerning > Steal Kerning From Next Pair** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `1f39494601cac658e2ba8900484749639b825b0ac065beb9779f24ae1c5bb18c`

[Python source at `1e4c2b2dd9bc`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1e4c2b2dd9bccfd04b38e70ed3dcaaa52242835d/Scripts/Kerning/Steal%20Kerning%20From%20Next%20Pair.py)
