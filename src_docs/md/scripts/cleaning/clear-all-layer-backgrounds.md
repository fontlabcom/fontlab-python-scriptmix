---
this_file: src_docs/md/scripts/cleaning/clear-all-layer-backgrounds.md
tags: ["Cleaning"]
categories: ["Cleaning"]
---

# Clear All Layer Backgrounds

Inspect every current-font glyph, then clear entire mapped backgrounds.

What it does:
    All physical foreground layers are included. Refresh rereads the original
    font; Clear removes complete background objects in one history batch. Shared
    master/auxiliary masks and automatic-layer dependencies refuse before writing.
    See the background-cleaning guide for scope and supported background types.

How it works:
    Delegate background inspection and removal to the shared App workflow. Map
    every physical foreground layer and refuse unsafe shared masks or
    automatic dependencies.

Why this design:
    Removing a complete background object differs from deleting only its
    outlines, so the preview shows the actual mapped scope.

How to use:
    Run Cleaning > Clear All Layer Backgrounds. Inspect the preview for the
    current font, use Refresh after changes and press Clear only for the shown
    proposal. Read the background-cleaning guide for supported domains.

Benefit:
    Clear mapped backgrounds across foreground layers in one recorded history
    batch.

Run **Cleaning > Clear All Layer Backgrounds** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/2faa23957e134bde1e6e28847aeaca355feb95e0611d66f382c14ff82a7fc36d.py)
<!--/codeinclude-->
