---
this_file: src_docs/md/scripts/font-info/glyph-order-preview-and-export.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Glyph Order Preview and Export

Sort by Unicode, name or Unicode script; export one glyph name per line for the whole font.

What it does:
    Open this script with a font active. Choose Unicode, Name or Script, then select
    Export order. The modeless chooser saves UTF-8 text for use in another workflow.
    The font's glyph order and outlines stay unchanged. Reopen after switching fonts.

How it works:
    Sort captured glyph records by the selected Unicode, name or script key,
    always keeping .notdef first. Export the resulting names as UTF-8 lines.

Why this design:
    An exported proposal can feed another workflow without relying on an
    unverified native glyph-order writer.

How to use:
    Run Font Info > Glyph Order Preview and Export. Choose the sort mode,
    inspect old and new indices and select Export order to choose a
    destination file.

Benefit:
    Prepare a reproducible glyph-order list while preserving the font's stored
    glyph order.

Run **Font Info > Glyph Order Preview and Export** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `da3d34aaa6f1665591530edda75507155fde3f55c986b10035ee33d2e1cad30c`

[Python source at `1e4c2b2dd9bc`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1e4c2b2dd9bccfd04b38e70ed3dcaaa52242835d/Scripts/Font%20Info/Glyph%20Order%20Preview%20and%20Export.py)
