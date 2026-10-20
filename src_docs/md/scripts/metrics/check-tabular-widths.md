---
this_file: src_docs/md/scripts/metrics/check-tabular-widths.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Check Tabular Widths

Check exact selected-layer advances against the first selected occurrence.

Select glyphs in a Font window or layer occurrences in a Glyph window. Run
this Metrics command. The first occurrence supplies the reference. Editor
repeats retain their own layer choices; Font-window rows use the current master.
Fractional values remain exact.
Metrics keys and Auto do not override the actual advances. The report shows
one result per selected-layer occurrence, same/different totals and time heading.

Use Refresh after changing selection, master or widths. Close removes the
owned modeless panel. The report calls no font, selection, history, preferences
or Output writers. Empty/stale/missing sources produce a complete diagnosis.
Requires the reviewed App>=0.2.33.dev0 candidate and fontlab-fly in FontLab9
Python3.11. Adapted from Pedro Arilla's Apache-2.0 Tabular width checker; see
additional-tools.json and NOTICE. Native acceptance is pending.

Run **Metrics > Check Tabular Widths** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/699d492d34d2b039342ac28bf9c25c19bc120096c885eed2a6b53a025684f619.py)
<!--/codeinclude-->
