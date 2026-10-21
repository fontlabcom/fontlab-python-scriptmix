---
this_file: src_docs/md/scripts/contours/simplify-selected-nodes.md
tags: ["Contours"]
categories: ["Contours"]
---

# Simplify Selected Nodes

Remove alternate selected nodes from straight contours.

What: Keep the first selected node, remove the second, and repeat in contour
order. Open endpoints stay. Closed polygons keep at least three nodes.
How: Preview the removals on each master. Delete by descending stored index.
Curves are kept; use FontLab Contour > Simplify for curve reduction. Shared or transformed outlines are also kept.
Why: Restrict this operation to polygons so deletion cannot break cubic topology.
Use: Select polygon nodes, run the tool, choose masters and press Simplify.
Benefit: A repeatable reduction with matching selected indices applied across compatible masters.
The change is recorded as one Undo step. Automatic layers are kept; leave the
automatic-base consent off to keep their bases too.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Paths/Simplify selection.py, Apache-2.0.
Repository: https://github.com/pedroarilla/glyphs-scripts . No source code copied.

Run **Contours > Simplify Selected Nodes** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/3d3cdebe8d72a1143a918dfab35b4da28f328d1ed81c7ba6d6be3c025441abf9.py)
<!--/codeinclude-->
