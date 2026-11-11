---
this_file: src_docs/md/scripts/font-ui-lab/ufo-roundtrip-inspector.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# UFO Roundtrip Inspector

Stage a borrowed font in a private temporary directory and inspect its roundtrip.

Use: Open a font and run this tool. Run the inspector to export and reopen an
owned staged UFO, then inspect the complete semantic comparison and diagnostics.
Safety: The source is never overwritten or closed. Temporary staging belongs
to the inspector. FontLab preservation, history and native UI lifetime still
require native qualification.

The inspection button runs an explicit snapshot/export/reopen/import comparison.
Read every difference and limitation in the report: a successful disk reopen
does not establish lossless native font conversion. The temporary result is
not an editable replacement for the source document. Run inspection again to
refresh the report after deliberate source changes. Closing the inspector
releases its callbacks and owned UI without closing the borrowed font.

Run **Font UI Lab > UFO Roundtrip Inspector** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `5e4e39d4eadb8fed8ba12308ced2525024a03fa1357bc864a04bc21fddd30beb`

Immutable source link pending a reviewed containing commit.
