---
this_file: src_docs/md/scripts/features/nastaliq-connection-editor.md
tags: ["Features"]
categories: ["Features"]
---

# Nastaliq Connection Editor

Edit Qalmi Nastaliq connections and save reverse substitutions in the font.

What: Choose a left medial/final glyph, a right medial/initial family and its
numbered alternate. Preview entry/exit alignment on any master. Previous and
Next step through actual alternates, including s/sd forms.
How: Save connection writes a named lookup inside rlig through Fontport's
exact-source writer. A JSON comment in that lookup stores the choices, so
reopening the tool restores them. Each save is recorded as one Undo step.
Existing rlig statements and all other feature blocks stay in place. Earlier
unmanaged reverse rules are listed as a warning because they can run first.
Saved pairs with missing glyphs appear as named kept rows and produce no rules;
their records stay in the font until Drop stale pairs on Save is ticked.
Why: FontLab's Features panel edits source text. This panel adds Qalmi pair
selection, aligned outlines and grouped reverse contextual substitutions.
Use: Open a Qalmi-named font. Choose a pair and alternate, inspect the preview,
then Save connection. Compile and test the feature in FontLab's Features panel.
Reload reads saved choices. Closing without Save does not change that pair.
Benefit: Review and persist connections without editing feature syntax.

Credit: Independent behaviour-only rewrite of Simon Cozens,
GlyphsScripts/Nastaliq Connection Editor.py, MIT, copyright 2017.
Repository: https://github.com/simoncozens/GlyphsScripts . No source code copied.

Run **Features > Nastaliq Connection Editor** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/bbe018282d33c7c05f843898d5fcfffe8db47a34779b03f6647da60b0f5cf7d7.py)
<!--/codeinclude-->
