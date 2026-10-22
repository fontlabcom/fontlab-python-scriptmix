---
this_file: src_docs/md/scripts/proof/highest-lowest-glyphs.md
tags: ["Proof"]
categories: ["Proof"]
---

# Highest & Lowest Glyphs

Open the exact highest and lowest foreground layers in a fresh FontLab tab.

Run this Proof command with a font open. Scan all foreground masters and ordinary auxiliary layers; omit masks/service caches.
Keep font glyph order and the first layer on equal coordinates. Empty bounds
participate, and the same winner appears twice when it is both extrema. Preserve
unencoded glyph names and exact layer names rather than substituting Unicode or
slash text. Missing/ambiguous layers and stale/slow reads fail before a proof.
A modeless coordinate panel preserves the source messages without changing Output. Run Again repeats the complete scan and new-tab action.

Fly loads shared App capture, extrema selection and native named-layer tabs.
No missing layer is created; no master/selection/font/history/Output writer or
application-wide event loop is used. A native tab failure can leave a new tab;
no atomic UI rollback is claimed.
Requires App>=0.2.49.dev0 and Fly in FontLab9/Python3.11.
Modified from slobzheninov--Glyphs-Scripts/Testing/Highest & Lowest Glyphs.py; see NOTICE/additional-tools.json.
The port fixes zero being mistaken for an unset extrema value.

Run **Proof > Highest & Lowest Glyphs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/b1a8215b52fe0991d9fcf5307ea749bb2c242dd1f63220a32204a925864b9033.py)
<!--/codeinclude-->
