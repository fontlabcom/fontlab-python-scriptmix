---
this_file: src_docs/md/scripts/reports/why-you-not-compatible.md
tags: ["Reports"]
categories: ["Reports"]
---

# Why You Not Compatible

Report original structural differences across selected glyph layers.

Select glyphs in a Font window or occurrences in a Glyph window. Run this
Reports command. Every selected occurrence retains its own complete foreground
layer list: masters first, then auxiliary layers. Repeated glyph groups remain
repeated; mask/service layers are background/cache records.

Compare adjacent layers for path counts, ordered node counts/types, anchor-name
sets and component-name sets. Coordinates, transforms, component multiplicity,
path closure, hints and styles are outside these original checks. A compatible
message therefore is not a variable-font/export certificate. Native cubic and
quadratic endpoint types and closed-path node indexes follow the bridge mapping.

Refresh replaces the complete report or diagnoses failure without a valid prefix.
Close releases the owned modeless panel. Source label/global-short-circuit bugs
are repaired; name sets print deterministically. No Output panel is cleared,
and no font/selection/master/history/preference writer is called. Actual native
mapping, read/cache/font/history/persistence and UI acceptance remain pending.

Requires reviewed App>=0.2.51.dev0 and FontLab9 Python3.11 with fontlab-fly.
Adapted from Simon Cozens' MIT Why You Not Compatible? See NOTICE and
additional-tools.json for exact source and license provenance.

Run **Reports > Why You Not Compatible** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/8f2222b91f234a9c093b6b14949a91b19356128ff663fae93797427854add950.py)
<!--/codeinclude-->
