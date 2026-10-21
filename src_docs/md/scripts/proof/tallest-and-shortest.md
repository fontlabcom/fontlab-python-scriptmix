---
this_file: src_docs/md/scripts/proof/tallest-and-shortest.md
tags: ["Proof"]
categories: ["Proof"]
---

# Tallest and Shortest

Open the exact highest and lowest current-master layers in a fresh FontLab tab.

Run this Proof command with a font open. Scan only the selected master.
Keep font glyph order and the first layer on equal coordinates. Empty bounds
participate, and the same winner appears twice when it is both extrema. Preserve
unencoded glyph names and exact layer names rather than substituting Unicode or
slash text. Missing/ambiguous layers and stale/slow reads fail before a proof.
Return both winning layers and coordinates for Python callers.

Fly loads shared App capture, extrema selection and native named-layer tabs.
No missing layer is created; no master/selection/font/history/Output writer or
application-wide event loop is used. A native tab failure can leave a new tab;
no atomic UI rollback is claimed. Native scope/order/role/bounds/tab and full
font/history/dirty/save/reopen preservation still require owned qualification.
Requires App>=0.2.49.dev0 and Fly in FontLab9/Python3.11.
Modified from simoncozens--GlyphsScripts/Tallest And Shortest.py; see NOTICE/additional-tools.json.
The port fixes the undefined font global and +/-9999 sentinels.

Run **Proof > Tallest and Shortest** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/f9bc30fa91bce7fc32c81e0d4bd54d3a36662755f58653f4ffdefe7773abe132.py)
<!--/codeinclude-->
