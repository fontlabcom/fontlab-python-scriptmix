# this_file: Scripts/Font UI Lab/Anchor and Component Inspector.py
# SPDX-License-Identifier: Apache-2.0
"""Browse anchors and component references with a linked glyph preview.

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
preview clear. Close the inspection window when finished."""


def main():
    """Open the inspection window for the current borrowed font."""
    from fly.ap.fontui.anchor_components import show
    from fly.fp.world import FontWorld

    world = FontWorld()
    return show(world.CurrentFont())


if __name__ == "__main__":
    main()
