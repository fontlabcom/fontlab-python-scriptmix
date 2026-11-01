---
this_file: src_docs/md/scripts/metrics/spacing-string-preview.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Spacing String Preview

Render a spacing control string such as HOHnono from the font's own outlines and advances.

What it does:
    Type characters or /glyphname tokens, pick a master, and judge the rhythm of straight and round
    sidebearings without generating a font. Advance boxes and LSB/RSB numbers can be shown under
    each glyph. Nothing is edited; the preview follows the outlines as they are now.

How it works:
    Resolve text tokens to current outline paths and advances on the chosen
    master. Draw optional advance boxes and sidebearing values below each
    glyph.

Why this design:
    Control strings isolate spacing rhythm; the preview uses the font drawings
    directly and does not add kerning to hide raw spacing.

How to use:
    Run Metrics > Spacing String Preview. Enter a control string, choose a
    master and enable boxes or numbers as needed. Compare straight and round
    glyphs at the chosen size.

Benefit:
    Judge current spacing without generating a font or changing advance
    widths.

Run **Metrics > Spacing String Preview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0c1c9d2968b2e270bbac73f22cddc18cc40f950e27815117b0ee676aa1aef104.py)
<!--/codeinclude-->
