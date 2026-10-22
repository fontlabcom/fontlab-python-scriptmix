---
this_file: src_docs/md/scripts/kerning/text-preview.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Text Preview

Set text from the font's outlines with its kerning applied, per master, at any size.

What it does:
    Type text or /glyphname tokens, pick a master and drag the size slider; lines wrap to the
    window. Kerned gaps can be labelled with their values, and kerning can be switched off to see
    the raw spacing. FontLab resolves each pair, including class kerning. Nothing is edited.

How it works:
    Resolve text tokens to glyphs, cache transformed paths and ask FontLab for
    effective pair kerning on the chosen master. Wrap lines inside the proof
    window.

Why this design:
    Effective pair lookup includes class kerning, so the proof can compare
    resolved spacing with raw advances.

How to use:
    Run Kerning > Text Preview. Enter characters or slash-name tokens, choose
    a master and size, then toggle kerning and value labels to compare the
    spacing.

Benefit:
    Inspect the current outlines with effective kerning without exporting or
    editing the font.

Run **Kerning > Text Preview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/20440aea9ec454e262b6436010f97d16edbf92c492fae6d6edd635c8ebd5da31.py)
<!--/codeinclude-->
