---
this_file: src_docs/md/scripts/masters/common-glyphs.md
tags: ["Masters"]
categories: ["Masters"]
---

# Common Glyphs

Report exact glyph names common to every open font, including unencoded glyphs.

What:
    Show analysed family names, count, first-open-font character strings, exact
    stored nice names and verified GlyphData production names. Unknown production
    mappings remain explicit. Alternative encodings are listed separately.

How:
    Shared App double-reads registered font-owned records within a deadline;
    this caller supplies real glyphsLib production metadata. One font retains
    its glyph order. Multiple fonts use sorted names because the original set
    intersection order was unspecified. Character strings use the first assigned
    scalar, never the current font, alternate concatenation or inferred ligatures.
    Each nonempty string and each name retains its final source space.

Use:
    Run Masters > Common Glyphs with one or more open fonts; none need be current.
    Use Copy Characters or Copy Original Report for exact detached source MIME
    payloads, or inspect the encoding/metadata details. Refresh after changing
    fonts, and Close when done. Opening/Refresh changes no clipboard, Output or
    font data. Ordinary selection copying can normalize Unicode spaces/separators;
    escaped JSON retains exact strings. The literal MIME callbacks/OS clipboard
    handoff and native rendering still need qualification.
    The optional charcoal control is visible, unchecked and unavailable: FontLab
    lacks a supported glyph-only mark/history path (FontLab issue 8564).

Status:
    Partial source improvement. The original optional all-open-font charcoal
    action remains required and unimplemented; native report acceptance remains
    pending. This is not a complete equivalent of the original workflow.

Credits:
    Independent rewrite of behaviour, not copied source code. Luke Prowse
    (LukeProwse), NaN-xyz/GlyphsApp-Scripts/CommonGlyphs.py. MIT root LICENSE,
    Copyright (c) 2019 LukeProwse; upstream README also declares Apache-2.0.
    Exact MIT notice is retained in NOTICE.
    https://github.com/NaN-xyz/GlyphsApp-Scripts

Run **Masters > Common Glyphs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `e33465af702a32d55c3f0ea20a550ab7912c61ec37603befe7a441d703d0f1e6`

[Python source at `c2b34988556c`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/c2b34988556c9214a67f800f68565b7a32df832a/Scripts/Masters/Common%20Glyphs.py)
