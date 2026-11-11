---
this_file: src_docs/md/scripts/font-info/names-and-credits.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Names and Credits

Edit family, style, credits and version naming for the current font.

What it does:
    Family, designer, copyright and version name are font-wide; the style name belongs
    to the current master (FontLab stores it per master). A table previews the changed
    fields before Apply.

    Open with a font active. Edit the fields, review the table, then choose Apply.
    Blank family or style names and invalid version text disable Apply. The undoable
    edit leaves outlines and other masters' style names intact. Reopen after changing
    the active master or font so the displayed style scope stays explicit.

How it works:
    Validate all single-line naming fields and stage explicit font-wide or
    current-master metadata changes. Apply through the shared Font Info
    history writer.

Why this design:
    Style is master-specific while family and credit fields are global, so the
    preview must keep their scopes distinct.

How to use:
    Run Font Info > Names and Credits. Edit the fields, review the changed-
    field table and press Apply. Reopen after changing font or master before
    editing that master's style.

Benefit:
    Update related naming and credit metadata together while retaining
    outlines and other masters' style names.

Run **Font Info > Names and Credits** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `504f56070a5741e45718fd78bf97b2e1b239bec27d6c558171d8a2a2bc5cd9d0`

[Python source at `370bf9829bc1`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/370bf9829bc141c1c9f88be0018cbc285b502a5d/Scripts/Font%20Info/Names%20and%20Credits.py)
