---
this_file: src_docs/md/scripts/contours/node-coordinates-panel.md
tags: ["Contours"]
categories: ["Contours"]
---

# Node Coordinates Panel

Follow selected nodes as you edit; inspect coordinates, offsets and distances.

Open a glyph, run this script and select nodes. Both tables update every 400 ms.
Copy exports the displayed node coordinates as tab-separated lines. Contour
numbers start at one; node indices start at zero. Component contours are excluded.
The modeless panel reads the bound font only. Switching or closing that font
stops polling; reopen the tool to bind another font. No font data is written.

Run **Contours > Node Coordinates Panel** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4dc0d75c5aa4c73dce01988302edd14bb91b148b6bd84a7ec629701a0f262b63.py)
<!--/codeinclude-->
