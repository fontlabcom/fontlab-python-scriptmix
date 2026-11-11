---
this_file: src_docs/md/scripts/components/component-graph.md
tags: ["Components"]
categories: ["Components"]
---

# Component Graph

Draw which glyphs use which other glyphs as components, as a movable graph.

What: Opens a modeless panel with a node graph of the current font. Each node
is a glyph; an arrow joins a composite glyph to each glyph it uses as a
component. A force layout spreads the nodes; drag a node to move it and the
neighbours follow. Use it to see at a glance which base glyphs carry many
composites, which glyphs sit in long dependency chains and which glyphs stand
alone.

Use: Open a font. Run Components > Component Graph. Watch the layout settle,
then drag nodes to explore; hover a node to see its exact glyph name. Press
Refresh after you change components in the font; the graph does not follow
edits by itself. The report area lists every "glyph → base" link and marks
the isolated glyphs; the status line gives the reason when no graph could be
built. The graph shows the components of the current master. Close the panel
when you are done.

Safety: Read-only. The tool reads the component structure of the current
master once per refresh. Moving a node moves only a picture in the panel. It
writes no font data, selection, history, preference, file, clipboard or Output
text. Closing the panel releases its scene and timers.

Source: Original workflow built on the shared App component graph
(fly.ap.components.graph.model), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.

Run **Components > Component Graph** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `890762f22f39f64455ec29dcd0fe3a3bd919266d6b62de3026e9daab525d4725`

[Python source at `75235791e388`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/75235791e3880a7bc761f4bbc9c5dccc08813705/Scripts/Components/Component%20Graph.py)
