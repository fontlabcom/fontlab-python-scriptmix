---
this_file: src_docs/md/scripts/reports/smallcap-consistency.md
tags: ["Reports"]
categories: ["Reports"]
---

# Smallcap Consistency

Report missing smallcaps, orphan smallcaps and capital kerning-group differences.

What it does:
    Count exporting upper, lower and smallcap glyphs. List missing .sc/.smcp
    and .sc/.c2sc counterparts, orphan smallcaps, missing capitals/lowercase
    and left/right smallcap-to-capital kerning-group differences.

How it works:
    Capture detached metadata from the current font and master. Use Unicode
    case mappings with alternate suffixes intact, including ligatures and
    multi-character mappings. Exact SC suffix particles identify smallcaps.
    The public.skipExportGlyphs compatibility list defines export scope;
    this is not a guarantee about FontLab's binary exporter. Unknown name
    mappings and ambiguous groups appear separately. A three-second budget
    refuses partial reports; synchronous getters are checked on return.

Why this design:
    Keep both modern and legacy checks from mekkablue's Check Smallcap
    Consistency while correcting its Boolean counterpart test. A report
    exposes incomplete sets without changing glyphs, selection or history.

How to use:
    Open a font and run Reports > Smallcap Consistency. Read the named
    sections in the non-modal report. Run again after changes to refresh the
    same owned report window. Close the report when finished.

Benefit:
    Find gaps in a smallcap set and its kerning groups before proofing.

Credits:
    Workflow: mekkablue, Glyphs-Scripts/Smallcaps/Check Smallcap Consistency.py,
    Apache-2.0. This FontLab implementation does not copy the original body.

Run **Reports > Smallcap Consistency** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `9bc4fe033f5cf0d2643a0f5026ac6d9a7bf0bb01066a2a2622e9ea8fd26b9736`

[Python source at `3dc87d8a0e3d`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3dc87d8a0e3dec803dc9255436da39eb19abefb2/Scripts/Reports/Smallcap%20Consistency.py)
