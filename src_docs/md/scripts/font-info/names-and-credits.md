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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/6f53bcec74d4f657b3cf7a5595c9e567ab03e5c3009fe0dc19070d40498d46e5.py)
<!--/codeinclude-->
