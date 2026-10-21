---
this_file: src_docs/md/scripts/proof/bracket-layers-and-components.md
tags: ["Proof"]
categories: ["Proof"]
---

# Bracket Layers and Components

Find bracket-named glyphs and all transitive component dependants.

Scan every glyph and every foreground layer in the current font. A single layer
name must contain both [ and ]; this name pattern does not establish export rules.
Mask/service layers are background/cache records. Include direct and indirect
component users across all foreground layers, including cycles and group overlap.

Open both sorted groups in a fresh Glyph tab in the captured font/master.
Both groups retain overlapping names. The report counts their union and explains
overlap; the proof uses explicit named symbols, deterministic order and literal
headings, without empty-section orphan slashes or Unicode substitution.
An empty proof result diagnoses the source condition without opening a tab.

Complete source/context rechecks refuse unreadable, changing or expired scans.
No Output panel clearing or source font/master/selection/history/preference edit
is requested. Native read/cache, symbol/layer mapping, full font preservation and
UI acceptance remain pending. A failed tab creation/population may leave a new tab.

Requires App>=0.2.53.dev0 and FontLab9 Python3.11 with fontlab-fly.
Adapted from Reset Type Studio's New Tab with Glyphs containing BL.py.
Copyright2025 Fernando Díaz & Reset Type Studio. See NOTICE and additional-tools.json.

Run **Proof > Bracket Layers and Components** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/131a8885c55527a6a64dd62c04cf54f0ce9fcf6df3ec8327b2c13931f404e4a1.py)
<!--/codeinclude-->
