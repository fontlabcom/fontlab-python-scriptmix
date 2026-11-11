---
this_file: src_docs/md/scripts/contours/outline-doctor.md
tags: ["Contours"]
categories: ["Contours"]
---

# Outline Doctor

Inspect and apply outline changes through named task tabs and a live glyph view.

Add extremes, correct contour direction, delete close points or duplicate and
small contours, repair zero handles, optimise starts, remove overlaps and round
coordinates.
Choose glyphs and master scope in the task tab. Preview Changes lists the exact
planned edits without writing. Inspect the sortable, filterable result table
and the captured glyph and layer in the read-only canvas. Apply Changes rechecks
the accepted input and source state before the original guarded native writer.

Staged previews stay in their tabs. Use Discard Preview before Refresh. Locked,
shared and automatic targets retain their operation-specific refusals; changes
to bases of automatic composites need explicit consent. Structural operations
retain the original compatibility rules. Partial native failures remain visible
and require checking the font and Undo. Save/reopen caveats for raw Smooth flags
remain in the relevant operation's status advice.

Requires FontLab App with the Outline Doctor composition and fontlab-fly.
Sources: FontLab App contributors, Apache-2.0; independent adaptations after
Simon Cozens (MIT) and Pedro Arilla (Apache-2.0). See Scriptmix NOTICE and the
preserved provenance manifests for the complete original source identities.

Run **Contours > Outline Doctor** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `aa245a80c122a259203c257192df856b8e8dd18e3e78614837a53cbfcd58a043`

[Python source at `3dc87d8a0e3d`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3dc87d8a0e3dec803dc9255436da39eb19abefb2/Scripts/Contours/Outline%20Doctor.py)
