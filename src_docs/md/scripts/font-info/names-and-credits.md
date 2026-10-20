---
this_file: src_docs/md/scripts/font-info/names-and-credits.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Names and Credits

Edit family, style, credits and version naming for the current font.

Family, designer, copyright and version name are font-wide; the style name belongs
to the current master (FontLab stores it per master). A table previews the changed
fields before Apply.

Open with a font active. Edit the fields, review the table, then choose Apply.
Blank family or style names and invalid version text disable Apply. The undoable
edit leaves outlines and other masters' style names intact. Reopen after changing
the active master or font so the displayed style scope stays explicit.

Run **Font Info > Names and Credits** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/22770ea8c13c0e5680a12f718a2d3d774139011938e33bd48a46808d3f3f2557.py)
<!--/codeinclude-->
