---
this_file: src_docs/md/scripts/contours/angularizzle.md
tags: ["Contours"]
categories: ["Contours"]
---

# Angularizzle

Turn selected closed outlines into angular planes with a modeless preview.

Min plane defaults to 80; Keep detail preserves short segments. Single-layer
Process always samples the opening selected layer and writes its glyph's first
master. Process can repeat; Cancel restores that actual target's opening paths
while retaining the source tool's colour mark. Closing keeps processed paths.
Batch Process follows ordered selected occurrences, including repeats, then
closes. Open paths are omitted when a closed angular result replaces paths.

The bound session refuses stale sources, unsupported hints, automatic
dependants and ambiguous shape ownership before editing. A late native failure
disables further writes and retains recovery data; close the panel and inspect
the diagnosed result before continuing.
Requires matching App/Fly candidates. Adapted from NaN Angularizzle; see NOTICE.

Run **Contours > Angularizzle** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `a08ea56a473da5814a549a27e74f089e43e3d15450bf87bbc722e51631b8958b`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Contours/Angularizzle.py)
