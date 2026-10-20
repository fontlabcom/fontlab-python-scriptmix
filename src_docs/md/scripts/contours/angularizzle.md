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
the diagnosed result before continuing. Native FontLab acceptance is pending.
Requires matching App/Fly candidates. Adapted from NaN Angularizzle; see NOTICE.

Run **Contours > Angularizzle** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/207a1e6279026b105f5f767be9772dabada23e2bec4d3f52eea03b03b4f1c9ae.py)
<!--/codeinclude-->
