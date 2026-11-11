---
this_file: src_docs/md/scripts/features/alternate-preview.md
tags: ["Features"]
categories: ["Features"]
---

# Alternate Preview

Compare a base glyph and its suffixed alternates in each master. Read-only; outlines share one scale per row.

What it does:
    Run with a font active. All original controls use the shared fly panel lifecycle.
    Feature data is font-wide; reopen after switching fonts or changing source.

How it works:
    Match the complete base-plus-dot prefix, then draw existing alternates
    with their transformed outlines. Each master row uses a common scale for
    comparison.

Why this design:
    Naming identifies candidate alternates without claiming that a feature
    rule selects them during shaping.

How to use:
    Run Features > Alternate Preview. Enter an existing base name, choose the
    master scope and scroll through all displayed rows. Reopen after changing
    the bound font.

Benefit:
    Compare alternate proportions and master differences without generating a
    font or changing glyphs.

Run **Features > Alternate Preview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `ee331b1a0e0d9f3529ac41275b5c18ff8366afd114eba2398d396e69b3280f35`

[Python source at `6b1048c4f1db`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6b1048c4f1dbc64ebe49d419db9193ccb3d9a9f0/Scripts/Features/Alternate%20Preview.py)
