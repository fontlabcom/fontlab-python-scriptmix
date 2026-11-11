---
this_file: src_docs/md/scripts/features/classes-browser.md
tags: ["Features"]
categories: ["Features"]
---

# Classes Browser

Browse feature classes and their members. Filter by class name or glyph; font-wide across masters.

What it does:
    Run with a font active. All original controls use the shared fly panel lifecycle.
    Feature data is font-wide; reopen after switching fonts or changing source.

How it works:
    Read feature-class records, exclude kerning-only classes and strip the
    native key-member marker. Filter the captured class names and member text.

Why this design:
    Feature classes and kerning classes serve different tasks; this view keeps
    the feature membership explicit.

How to use:
    Run Features > Classes Browser with a font open. Type a class or member
    filter, choose a row and copy the displayed class declaration when needed.

Benefit:
    Check which glyphs belong to a feature class without editing membership or
    feature source.

Run **Features > Classes Browser** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `a896a353e2d9ccc0ac4b6af74f4e6e6cfa47287aabd726188b78f55d16592ee9`

[Python source at `bf9287c6130a`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/bf9287c6130a3083b3c1047050305dfceecbee2b/Scripts/Features/Classes%20Browser.py)
