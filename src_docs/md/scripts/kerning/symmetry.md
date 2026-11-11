---
this_file: src_docs/md/scripts/kerning/symmetry.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Symmetry

Make the complete Science Gothic target set bidirectionally symmetric.

Apply every configured pair and its inverse across all masters except names
containing # or case-sensitive Ctr. Seven named smallcaps and 21 Unicode targets retain original
order, class-side priority, sequential alias effects and ties-even five-unit
rounding. Missing directions use the present value; a requested zero deletes
both explicit keys. Equal existing zeros remain. An owned result lists every
mismatch, warning, chosen class and per-master count without clearing Output.

The complete batch uses shared history and preflight: stale targets/classes,
missing required targets/class categories, fractional history and unsupported
save/reopen ranges refuse before writes. A native write failure can be partial;
use Undo as its diagnostic directs.

Independent implementation of Vassil Kateliev / Karandash Type Foundry's
SG-Font-Kerning-Symmetry.py (2025), Science Gothic. Original licence undeclared;
no original body is copied. Requires App>=1.2.0 and public Fly.

Run **Kerning > Symmetry** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `8b8001c1d327737a265ddfd5aee98e0cd149e8b13097c0f1d8d6dbb41e5001ce`

[Python source at `370bf9829bc1`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/370bf9829bc141c1c9f88be0018cbc285b502a5d/Scripts/Kerning/Symmetry.py)
