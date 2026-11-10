---
this_file: src_docs/md/scripts/components/dump-component-recipes.md
tags: ["Components"]
categories: ["Components"]
---

# Dump Component Recipes

Dump ordered recipes for selected component glyphs in Font/Glyph windows.

Select glyphs or editor layer occurrences, then run this command. The modeless
read-only report gives one `base+base=glyph` line per layer with components.
Selected-layer order, repeated occurrences/bases and mixed layers are retained.
The source format omits positions, transforms and own contours; the text is a
composition aid, not a complete geometry export or a guaranteed import recipe.

Use Refresh after changing the font, master or selection. Empty/missing/stale
sources and deadline overruns give a clear diagnosis; partial rows are cleared.
Close releases this owned panel. The report calls no font, selection, history,
preferences, clipboard or Output writers. Requires matching App and fontlab-fly
in FontLab9 Python3.11. Adapted from Simon Cozens' MIT Recipe Dumper; see NOTICE.
The shared reader retains each editor slot’s explicit layer choice. Font-window
selection uses the current master. Actual FontLab behavior and complete native
preservation remain pending acceptance.

Run **Components > Dump Component Recipes** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `8e46590e3f3d2400156c54be82f4ef9b5855c1d2a3c92c4fb832bf5ce69d6bc5`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Components/Dump%20Component%20Recipes.py)
