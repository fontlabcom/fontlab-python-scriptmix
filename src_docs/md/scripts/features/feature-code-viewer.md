---
this_file: src_docs/md/scripts/features/feature-code-viewer.md
tags: ["Features"]
categories: ["Features"]
---

# Feature Code Viewer

Read-only feature source for the whole font. Choose a feature and search its code.

What it does:
    Run with a font active. All original controls use the shared fly panel lifecycle.
    Feature data is font-wide; reopen after switching fonts or changing source.

How it works:
    Read ordered prefix and feature blocks through Fontport. Keep empty blocks
    and exact source; highlight literal search matches without compiling the
    font.

Why this design:
    Direct source inspection avoids confusing generated classes with the code
    that is actually stored.

How to use:
    Run Features > Feature Code Viewer with a font open. Choose the prefix or
    a feature, enter search text and use the search action to move through its
    matches.

Benefit:
    Locate a rule or language declaration while leaving feature source and
    glyph data unchanged.

Run **Features > Feature Code Viewer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `78bcce4cb4f7fc5090c30709fb1e5ebd77452e42fdced4931ea482232fb124c9`

[Python source at `4bab81718f97`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/4bab81718f976cbdb0cf33c249fc85b5df530a9a/Scripts/Features/Feature%20Code%20Viewer.py)
