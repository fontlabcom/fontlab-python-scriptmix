---
this_file: src_docs/md/scripts/font-info/bump-font-version.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Bump Font Version

Bump the numeric version and version name; optionally append a dated font note.

What it does:
    Open with a font active. Choose a major or minor bump and optional dated notes,
    review the field changes, then choose Apply. Minor 999 carries into the major.
    Version fields are global; notes are appended to each master's existing note.
    The edit is undoable. Reopen the panel after switching fonts.

How it works:
    Plan a bounded numeric version and matching version name. Optionally
    append a dated note to every master's existing note; keep the fields
    staged until Apply.

Why this design:
    Version naming and numeric metadata must agree, while an optional history
    note must not replace existing master notes.

How to use:
    Run Font Info > Bump Font Version. Choose major or minor and the dated-
    note option, inspect all proposed changes and press Apply once for the
    intended increment.

Benefit:
    Update related version metadata together and retain the previous note
    content.

Run **Font Info > Bump Font Version** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `98b2a1a721c4ad5b4b6a6851cf10a9f3aa20f31774fa4bf66244cd628aa48e53`

[Python source at `bf9287c6130a`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/bf9287c6130a3083b3c1047050305dfceecbee2b/Scripts/Font%20Info/Bump%20Font%20Version.py)
