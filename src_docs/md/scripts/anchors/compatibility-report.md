---
this_file: src_docs/md/scripts/anchors/compatibility-report.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Compatibility Report

Compare anchor names across masters: a glyph whose masters carry different anchors cannot interpolate them.

What it does:
    The tree lists each glyph with its anchor count per master; expand a glyph to see
    which master lacks which anchor. Mismatches are flagged and listed first.
    Auto layers show "auto" and are not compared: FontLab rebuilds their anchors.
    Double-click a glyph to select it in the Font window. Nothing is changed.

How it works:
    Read anchor-name sets for selected glyphs on each master. Compare only
    non-automatic layers and expand mismatches to show missing names per
    master.

Why this design:
    Automatic layers rebuild anchors, so including them as manually comparable
    source sets would give a misleading compatibility diagnosis.

How to use:
    Select glyphs and run Anchors > Compatibility Report. Expand flagged
    glyphs to inspect their anchor names and double-click a glyph to select it
    in the Font window.

Benefit:
    Find anchor-name differences without adding, deleting or moving anchors.

Run **Anchors > Compatibility Report** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `f82b3024ab2402469bb11df09ee38567a22c3928441d67736a930ae080377afd`

[Python source at `bf9287c6130a`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/bf9287c6130a3083b3c1047050305dfceecbee2b/Scripts/Anchors/Compatibility%20Report.py)
