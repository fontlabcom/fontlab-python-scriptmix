---
this_file: src_docs/md/scripts/cleaning/clear-master-backgrounds.md
tags: ["Cleaning"]
categories: ["Cleaning"]
---

# Clear Master Backgrounds

Inspect every current-font glyph, then clear entire mapped backgrounds.

Only declared master foreground layers are included. Refresh rereads the original
font; Clear removes complete background objects in one history batch. Shared
master/auxiliary masks and automatic-layer dependencies refuse before writing.
See the background-cleaning guide for scope and native qualification limits.

Run **Cleaning > Clear Master Backgrounds** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a2e99aba286bbc5f8ea0008a1e7210756f8b494b892fa911351483affae77fa4.py)
<!--/codeinclude-->
