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
no original body is copied. Requires App>=0.2.26.dev159 and public Fly.

Run **Kerning > Symmetry** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/5f9f9537a58154100fc34cec5b7588522893ff897b33b4d984f5a958ae9579cd.py)
<!--/codeinclude-->
