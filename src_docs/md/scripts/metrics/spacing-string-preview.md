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

## Source identity

SHA256: `48c3240f5aa1c920679ca3722171da565a3be2c282b14a5f301736d7808ef3c5`

[Python source at `168b57cbfbaf`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/168b57cbfbaf1b00b43f4aa06ba26d2e01ba12e1/Scripts/Metrics/Spacing%20String%20Preview.py)
