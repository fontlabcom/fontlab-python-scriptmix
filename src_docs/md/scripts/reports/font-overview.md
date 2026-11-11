---
this_file: src_docs/md/scripts/reports/font-overview.md
tags: ["Reports"]
categories: ["Reports"]
---

# Font Overview

A one-screen dashboard of the current font: glyphs, encoding, masters, kerning, composites.

What it does:
    Cards show glyph and code point counts, composites, glyphs without
    outlines on the current master, marks and notes; the table lists each
    master's vertical metrics and kerning pair count. Click Refresh after
    editing. Nothing in the font changes.

How it works:
    Count glyph encodings, composites, empty current-master drawings, marks
    and notes. Read each master's vertical metrics and explicit kerning-pair
    count for the table.

Why this design:
    Cards give a compact census, while the master rows keep family-specific
    metrics visible beside it.

How to use:
    Run Reports > Font Overview with a font open. Inspect the cards and master
    rows; press Refresh after edits or a font change to obtain a new report.

Benefit:
    Review the reported font inventory without modifying outlines, labels,
    metrics or kerning.

Run **Reports > Font Overview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `7801721daf5b5866fbcc4cbc9f768855ee9b9a1d0d10e97046dd44d2d63b2976`

[Python source at `3dc87d8a0e3d`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3dc87d8a0e3dec803dc9255436da39eb19abefb2/Scripts/Reports/Font%20Overview.py)
