---
this_file: src_docs/md/scripts/kerning/pair-editor.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Pair Editor

Edit every kerning pair that involves one glyph, with one column per master.

What it does:
    Rows are the pairs where the glyph, or a kerning class it belongs to, is on the left or right.
    Type a new value in any master's cell; clear a cell to delete that pair on that master. Edited
    cells turn the accent colour until Apply, which writes all of them as one Undo step. Add a row
    for a new partner with the field under the table.

How it works:
    Collect pairs involving the glyph or its applicable classes and stage
    editable master cells. Treat an empty cell as deletion and validate new
    side-specific partners.

Why this design:
    Staged cells let the user review several master changes before the shared
    writer checks and commits the complete batch.

How to use:
    Run Kerning > Pair Editor. Choose a glyph, edit values or add a partner
    row, inspect highlighted changes and press Apply. Clear a cell only when
    that stored pair should be deleted.

Benefit:
    Edit related explicit pairs together; Apply is recorded as one Undo step.

Run **Kerning > Pair Editor** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `3ae4e4bdb1fdfd377ed521ee054fcd1eee843e024fbd0d994dc9755f3a0c13ab`

[Python source at `370bf9829bc1`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/370bf9829bc141c1c9f88be0018cbc285b502a5d/Scripts/Kerning/Pair%20Editor.py)
