---
this_file: src_docs/md/scripts/proof/text-by-master.md
tags: ["Proof"]
categories: ["Proof"]
---

# Text By Master

Render the same text once per master, stacked, to compare weight and width at a glance.

What it does:
    Each row is drawn from that master's outlines with its line width in units.
    Type text (use /glyphname for unencoded glyphs), adjust the size and scroll
    through the masters. Advance widths only: kerning is not applied. Nothing in
    the font changes.

How it works:
    Parse characters and slash-name tokens, read each master's glyph run and
    draw stacked rows with their total advances. Use the same requested proof
    size.

Why this design:
    A repeated text line makes width and weight changes easier to compare
    across the complete master set.

How to use:
    Run Proof > Text By Master. Enter proof text, adjust the size and scroll
    through the master rows. Inspect missing-character counts as well as the
    drawings.

Benefit:
    Compare master text with advance spacing while keeping kerning and font
    data unchanged.

Run **Proof > Text By Master** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/22a100a01bf9af350a0cec5981c67e0f2c5dde77648b8e47dda92c2bfc424907.py)
<!--/codeinclude-->
