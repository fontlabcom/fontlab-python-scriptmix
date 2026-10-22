---
this_file: src_docs/md/scripts/masters/set-intermediate-layer.md
tags: ["Masters"]
categories: ["Masters"]
---

# Set Intermediate Layer

Add interpolated intermediate layers to selected glyphs at explicit coordinates.

What: Preview one new intermediate layer per selected glyph. Set each axis
coordinate in design units, then press Add Layers. Existing layers stay.
How: FontLab interpolates each glyph with interpolateInstance. The result gets
a location name such as :wt=512.5 and is added through shared history.commit.
The change is recorded as one Undo step. No glyph or font master is created.
Why: FontLab's Layers and Masters panel can add a layer and Glyph > Reinterpolate
can fill it. This panel combines the two over a selection, with a refusal report.
Use: Open a font with at least two masters and declared axes. Select glyphs,
run the tool, set coordinates and inspect the preview before adding layers.
Benefit: Build matching intermediate locations without repeating layer setup.

Automatic glyphs and their bases, locked sources, incompatible masters,
existing locations and fonts without declared axes are kept. Editor tabs and
their order stay in place; this tool does not replace displayed glyph slots.
Fractional coordinates are preserved. Invalid values are refused.

Independent behaviour rewrite after Reza Bohloul, RezaBohloul,
Glyph/Set Intermediate Layer.py; no licence declared.
Repository: https://github.com/RezaBohloul/RezaBohloul . No source code copied.

Run **Masters > Set Intermediate Layer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/564aacbfcf678dff586d105e3953a23911aed5eb0baefeb6332876fbfddda770.py)
<!--/codeinclude-->
