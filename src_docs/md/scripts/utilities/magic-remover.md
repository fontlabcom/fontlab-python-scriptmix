---
this_file: src_docs/md/scripts/utilities/magic-remover.md
tags: ["Utilities"]
categories: ["Utilities"]
---

# Magic Remover

Remove corresponding selected items from compatible glyph layers.

What: Preview selected polygon nodes, whole contours and components on every
compatible foreground master or intermediate layer of one glyph. If any
compatible master must keep an item, every master keeps that item.
How: Match stored shape, contour and node indices and component bases.
Use the shared outline writer. Components retain their
original history objects. The change is recorded as one Undo step.
Why: FontLab Delete with Preferences > Variations > Synchronize "Remove node"
and matching edits removes corresponding nodes, including curve nodes, on the
other masters. This panel adds a per-layer preview and explicit kept reasons.
Use: Select items in one Glyph window slot. Run the tool, inspect the rows,
then press Remove. Use selection refreshes the current editor selection.
Benefit: Remove the same detail over compatible masters without repeated edits.

Partial curve-node selections are kept: use FontLab's Delete as described above.
The public contour API does not expose curve-preserving node deletion.
Whole curved contours can be removed, along with any outline shape left empty.
Anchors are not part of selection removal: the public pin binding exposes no
selection member. Existing anchors stay unchanged.
Polygon endpoints and the minimum of three closed or two open nodes are kept.
Masks, service, locked, shared and transformed outlines are kept. Automatic
glyphs and their bases are kept. Glyphs corner-component hints have no FontLab
counterpart. For a separate outline backup, use Masters > Copy Outline To Mask
before removal; this tool never overwrites a mask on a modifier-key press.

Independent behaviour rewrite after Reza Bohloul, RezaBohloul,
Edit/Magic Remover.py; no licence declared.
Repository: https://github.com/RezaBohloul/RezaBohloul . No source code copied.

Run **Utilities > Magic Remover** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/51ef715b8e2ca2aa5252741e4855fd707177ed00ba0aa0a7cef37e14c4b5fc13.py)
<!--/codeinclude-->
