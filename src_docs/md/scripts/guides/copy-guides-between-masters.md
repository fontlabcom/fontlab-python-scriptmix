---
this_file: src_docs/md/scripts/guides/copy-guides-between-masters.md
tags: ["Guides"]
categories: ["Guides"]
---

# Copy Guides Between Masters

Merge or replace glyph guides on explicitly selected target masters.

What it does:
    Select glyphs and choose From, To, merge/replace and optional width scaling.
    Inspect every add/remove row, then use Copy. Nonpositive widths cannot be scaled.
    Matching target guides retain native colour, tags and geometry; hints are kept.
    Unsafe automatic dependants are refused before history. Close releases signals.

How it works:
    Read source guide records and plan merge or replacement for each checked
    target master. Preserve matching native guide properties and reject
    impossible width scaling.

Why this design:
    Explicit target checks prevent a master choice from silently applying to
    the whole family; matching guides need not be rebuilt.

How to use:
    Select glyphs and run Guides > Copy Guides Between Masters. Choose source,
    targets, mode and scaling, inspect add/remove rows and press Copy.

Benefit:
    Reuse construction guides between masters; Copy is recorded as one Undo
    step.

Run **Guides > Copy Guides Between Masters** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `221f489ff22572c7c0ac867f086db03d259219991d7c36d0af4730859e86ce15`

[Python source at `c2b34988556c`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/c2b34988556c9214a67f800f68565b7a32df832a/Scripts/Guides/Copy%20Guides%20Between%20Masters.py)
