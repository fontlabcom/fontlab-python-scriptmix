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

Requires App>=1.2.0 and FontLab9 Python3.11 with fontlab-fly.
Adapted from Reset Type Studio's New Tab with Glyphs containing BL.py.
Copyright2025 Fernando Díaz & Reset Type Studio. See NOTICE and additional-tools.json.

Run **Proof > Bracket Layers and Components** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `cea59f6bba23b2bce78e7e2dee8ee026a03137f6d24599ba73781d32395e740f`

[Python source at `cca80db1b47f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/cca80db1b47f998bbbf4a26427a1e5949ccf7230/Scripts/Proof/Bracket%20Layers%20and%20Components.py)
