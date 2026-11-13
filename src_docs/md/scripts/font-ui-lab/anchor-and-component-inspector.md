---
this_file: src_docs/md/scripts/font-ui-lab/anchor-and-component-inspector.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Anchor and Component Inspector

Browse anchors and component references with a linked glyph preview.

Use: Open this window with a font available, filter the glyph names and select a
glyph. The anchor table lists each anchor's name and coordinates in the order
provided by that glyph. Repeated names and unnamed anchors remain separate rows;
the inspection does not merge them or decide which should be kept. The preview
displays anchors and outline points alongside the selected glyph.

The component table lists direct component references and their complete six-value
affine transformations. It shows the source records, so nested components are not
flattened into extra table rows. The linked outline can resolve component geometry
for display. A missing component, cyclic reference or invalid transformation can
produce a diagnostic while useful direct anchor and component records remain
visible. This helps distinguish the stored references from their drawable result.

Safety: This is a read-only inspection of the current borrowed font. It does not
rename anchors, replace components, transform outlines, save a file, or close the
font. With no font, no selection or unreadable glyph data, the relevant tables and
preview clear. Close the inspection window when finished.

Run **Font UI Lab > Anchor and Component Inspector** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `bcad7f3760c86d6678cf77c9c0b1237306843cd74495f45c2dca7f316cad397e`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Font%20UI%20Lab/Anchor%20and%20Component%20Inspector.py)
