---
this_file: src_docs/md/scripts/reports/case-coverage.md
tags: ["Reports"]
categories: ["Reports"]
---

# Case Coverage

Find missing uppercase and lowercase counterparts and export-policy conflicts.

What it does:
    Check the current font or every open font. Report missing uppercase and
    lowercase counterparts, alternate encoded names and export-policy conflicts.
    Open an ordered proof of each problem, reusing the current proof when asked.

How it works:
    Read detached FontGate names and alternative encodings. Glyport supplies
    maintained GlyphData categories. The caller supplies canonical GlyphData
    names to App's host-free engine. Canonical names win; the first encoded
    alias in font order follows, and all ambiguous aliases remain in the report.
    Multi-character case mappings stay complete; i_dotaccentcomb maps to i and
    SS maps to Germandbls. Other expansions use complete GlyphData component
    names joined by underscores; unknown component mappings stay unknown.
    Math exclusions and ligatures remain visible in detailed diagnostics.
    The public.skipExportGlyphs compatibility policy defines export status;
    this is not a guarantee about FontLab's binary exporter.

Why this design:
    Preserve mekkablue's Casefolding Report controls and source-order proofs
    while correcting its ord() failure on multi-character case mappings.
    Shared App mechanics own capture, proofs, settings and window lifetime.

How to use:
    Open a font and run Reports > Case Coverage. Choose the four controls and
    click Report. Use Show detailed report to read the complete per-font rows.
    Exclude math symbols suppresses missing counterparts only. Reuse current
    tab controls proof placement. When inactive views are ambiguous, choose the
    exact existing view and click Report again. FontLab does not expose Glyphs'
    remembered-tab order. The exact text-block binding is checked at runtime;
    unsupported bindings refuse proof creation/replacement with guidance.
    Installed native proof usability remains unqualified.
    Open detailed report window shows diagnostics
    automatically; it never clears or writes FontLab's Output panel.
    Refresh font availability after opening a font. Close the panel when done.

Benefit:
    Find incomplete case pairs and compatibility export mismatches before proofing.

Credits:
    Workflow: mekkablue/Glyphs-Scripts/Glyph Names, Notes and Unicode/
    Casefolding Report.py, Apache-2.0. Reimplementation; no source body copied.

Run **Reports > Case Coverage** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/fdab954a270ea6f738085dd8ba826168cc58f6d39a8ade49215ffe365ac6278f.py)
<!--/codeinclude-->
