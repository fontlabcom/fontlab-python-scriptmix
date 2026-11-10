---
this_file: src_docs/md/scripts/components/nested-finder.md
tags: ["Components"]
categories: ["Components"]
---

# Nested Finder

Find nested components and unnest them by one level.

What: Lists every component whose base glyph is itself a composite, on the
chosen masters of the selected glyphs or of the whole font. Unnest replaces
each such component with the parts of its base glyph: the inner components
and the base's own contours, placed where they appear now.

How: The base's parts are copied with the outer component transform applied,
so the glyph looks the same. Inner components stay components and keep
following their own base glyphs. Raw node flags, element names and element
notes that a native copy drops are copied back; some per-node and
per-contour properties, such as corner smoothing and contour names, are not
yet copied back. Auto layers are listed and kept.

Why: Nested components are legal, but some build tools and formats flatten
them badly or not at all. One level keeps the shared parts shared; only the
middle step goes.

Use: Select glyphs and run the script. It looks at every master; choose
Whole font to search all glyphs, or the current master to narrow it. A
whole-font run is refused while any glyph in it has an automatic layer or is
the base of one. Press Unnest. Press Reload selection after you change the
font or the selection.

Benefit: Finds every nesting in the selection or the font and fixes it as
one Undo step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- a base glyph has no plain layer for the master, holds a perspective
  transform or a composite shape that is not a component, or the components
  loop or nest more than 64 levels (the row says which).

After the write, the script reads the layers back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
The write is recorded as one Undo step: it hands FontLab each removed
component, with its data and builder. Edit > Undo of removed components
depends on FontLab (fl#7641). The copy, the base checks, the history write, the
panel, the
automatic-layer rule and the pending-update check are shared with other
scripts (fly.ap.components.writer, fly.ap.components.panel.model, fly.ap.core.history.glyphs,
fly.ap.core.edit_guards); the planner and the panel controls belong to this
script.

Source: the author's own FontLab sample
components_nested_finder.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Components > Nested Finder** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `0ae15ec6b25aefba241459e79226cc7ecce0a890a60f63a626215741a36365d9`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Components/Nested%20Finder.py)
