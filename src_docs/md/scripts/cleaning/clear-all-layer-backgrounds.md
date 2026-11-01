---
this_file: src_docs/md/scripts/cleaning/clear-all-layer-backgrounds.md
tags: ["Cleaning"]
categories: ["Cleaning"]
---

# Clear All Layer Backgrounds

Inspect every current-font glyph, then clear entire mapped backgrounds.

All physical foreground layers are included. Refresh rereads the original
font; Clear removes complete background objects in one history batch. Shared
master/auxiliary masks and automatic-layer dependencies refuse before writing.
See the background-cleaning guide for scope and native qualification limits.

Run **Cleaning > Clear All Layer Backgrounds** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/3671e9371e32ec5414ff0b529ec8f5d902229b938a32a2291631f991676d6c8c.py)
<!--/codeinclude-->
