---
this_file: src_docs/md/scripts/font-ui-lab/detached-transform-preview.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Detached Transform Preview

Preview one explicitly chosen layer/glyph without writing the captured font.

What: Compare a detached affine result with its immutable before snapshot.
Use: Choose a layer and glyph, Capture, then edit the existing transform fields.
Refresh reads the same captured font. Save settings creates a chosen new JSON;
Show script displays text without execution. Closing never closes the source.
Snapshot: Capture reads backend-stored outlines, not unfinished changes held in
borrowed scripting wrappers. Only the selected glyph, its reachable component
bases and required image bytes enter the private models. Missing bases, cycles
or unavailable resources refuse the snapshot. Changing the layer or glyph clears
the prior proof; choose the new target explicitly before Capture. Switching the
host's current font never retargets an already opened window. After closing the
source, the detached copy can still be inspected, but Refresh cannot read it.
Safety: Use an owned test font. No font Apply/save/export is provided. Native
metadata/resource completeness and FontLab lifetime/rendering remain unqualified.

Run **Font UI Lab > Detached Transform Preview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `8c8b631a35fab00f4af7403e7df3b44b1e276b3c39b494d9480554a131f28e83`

[Python source at `168b57cbfbaf`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/168b57cbfbaf1b00b43f4aa06ba26d2e01ba12e1/Scripts/Font%20UI%20Lab/Detached%20Transform%20Preview.py)
