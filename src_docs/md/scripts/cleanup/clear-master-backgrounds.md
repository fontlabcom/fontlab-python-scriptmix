---
this_file: src_docs/md/scripts/cleanup/clear-master-backgrounds.md
tags: ["Cleanup"]
categories: ["Cleanup"]
---

# Clear Master Backgrounds

Inspect every current-font glyph, then clear entire mapped backgrounds.

What it does:
    Only declared master foreground layers are included. Refresh rereads the original
    font; Clear removes complete background objects in one history batch. Shared
    master/auxiliary masks and automatic-layer dependencies refuse before writing.
    See the background-cleaning guide for scope and supported background types.

How it works:
    Delegate background inspection and removal to the shared App workflow. Map
    declared master foreground layers and refuse shared masks or unsafe
    automatic dependencies.

Why this design:
    Restricting scope to declared masters keeps auxiliary foreground
    backgrounds outside this cleaning operation.

How to use:
    Run Cleanup > Clear Master Backgrounds. Inspect the current-font preview,
    use Refresh after edits and press Clear for the shown master-layer
    proposal. Read the background-cleaning guide before use.

Benefit:
    Remove mapped master backgrounds in one recorded history batch while
    retaining auxiliary scope boundaries.

Run **Cleanup > Clear Master Backgrounds** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `10e44ef3e8e121b2000dee22ec143d86d18edc10bb7f054622eb98cb77e56169`

[Python source at `75235791e388`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/75235791e3880a7bc761f4bbc9c5dccc08813705/Scripts/Cleanup/Clear%20Master%20Backgrounds.py)
