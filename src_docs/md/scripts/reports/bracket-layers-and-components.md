---
this_file: src_docs/md/scripts/reports/bracket-layers-and-components.md
tags: ["Reports"]
categories: ["Reports"]
---

# Bracket Layers and Components

Find bracket-named glyphs and all transitive component dependants.

Scan every glyph and every foreground layer in the current font. A single layer
name must contain both [ and ]; this name pattern does not establish export rules.
Mask/service layers are background/cache records. Include direct and indirect
component users across all foreground layers, including cycles and group overlap.

Open or raise the complete read-only report with Refresh and Close.
Both groups retain overlapping names. The report counts their union and explains
overlap; the proof uses explicit named symbols, deterministic order and literal
headings, without empty-section orphan slashes or Unicode substitution.
An empty proof result diagnoses the source condition without opening a tab.

Complete source/context rechecks refuse unreadable, changing or expired scans.
No Output panel clearing or source font/master/selection/history/preference edit
is requested. Native read/cache, symbol/layer mapping, full font preservation and
UI acceptance remain pending. A failed tab creation/population may leave a new tab.

Requires App>=1.2.0 and FontLab9 Python3.11 with fontlab-fly.
Adapted from Reset Type Studio's Report Glyphs containing BL.py.
Copyright2025 Fernando Díaz & Reset Type Studio. See NOTICE and additional-tools.json.

Run **Reports > Bracket Layers and Components** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `9e1fd16e500ad842265491d162c751e258c4d66dd498adc8c54c42826b43e93f`

[Python source at `b52710a04ed5`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/b52710a04ed5e9e3759b7086daeb0b09ec65b6f3/Scripts/Reports/Bracket%20Layers%20and%20Components.py)
