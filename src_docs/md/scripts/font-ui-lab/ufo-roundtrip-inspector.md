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

SHA256: `7bb5fcaf1c7b499443c2b9ca610e3e32be4716a73f08990c53aeeed25e5472c6`

[Python source at `f4c16f20ef10`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/f4c16f20ef10163f48d550f3e8d74ab71620f1ec/Scripts/Font%20UI%20Lab/UFO%20Roundtrip%20Inspector.py)
