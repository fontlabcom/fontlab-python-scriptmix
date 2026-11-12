---
this_file: src_docs/md/scripts/font-ui-lab/feature-source-and-proof.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Feature Source and Proof

Edit stored feature source and refresh an independent glyph proof.

What: Link feature source and the existing glyph sequence for one captured font.
Use: Edit a block, choose explicit proof text or /glyph names, then Apply source.
Accepted Apply refreshes the proof once. Refresh proof retries only the view.
Feature source is stored, not compiled. Unicode and kerning placement does not
apply OpenType substitutions or positioning; unchanged positions are expected.

Safety: Use an owned test font. Active-font changes do not retarget this window.
External changes retain dirty drafts with a warning; explicit Apply can overwrite
newer source. Revert reloads stored source. Original paragraph separators remain
inspect-only; unsupported input is refused. Closing never saves or closes the
borrowed font. Native history, painting and saved-font acceptance remain separate.

Run **Font UI Lab > Feature Source and Proof** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `7dabf6b6e6ccd024a7011442f7456597f7eaed31038fadb02fc1b0aeff144a7d`

[Python source at `b52710a04ed5`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/b52710a04ed5e9e3759b7086daeb0b09ec65b6f3/Scripts/Font%20UI%20Lab/Feature%20Source%20and%20Proof.py)
