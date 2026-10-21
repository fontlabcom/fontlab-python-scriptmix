---
this_file: src_docs/md/scripts/components/build-from-recipes.md
tags: ["Components"]
categories: ["Components"]
---

# Build From Recipes

Build composite glyphs from one-line recipes with FontLab's own builder.

What: One recipe per line, for example "Aacute.alt = A + acute@acute". It
attaches the "_acute" anchor of acute to the "acute" anchor of A.
"a & b" places glyphs side by side; "mark@top[_top]" names both anchors.
Check runs every line on every chosen master as a dry run: no outline,
component, anchor or width changes (FontLab may refresh its internal glyph
data), so it runs only when you press it. Build creates the glyphs, or
rebuilds their layers when "Replace existing layers" is on.

How: The script hands each line to FontLab's construction engine, which
validates the recipe, places the components by their anchors and sets the
width. It does not compute positions itself. The result is a plain layer,
never an auto layer: FontLab would notify an auto layer, and that rebuilds
other auto layers in the font. An existing glyph without a layer for a
chosen master gets an empty layer first (one Undo step for all such
layers). A new glyph is built on the first chosen master; press Build again
to build its other masters (the status line says how many are left).

Why: A recipe list is exact, repeatable and easy to review. The builder is
FontLab's own, so the script does no anchor arithmetic that could disagree
with FontLab.

Use: Type or paste the recipes. Choose the masters and whether to replace
existing layers. Press Check, read the table, then press Build.

Benefit: Builds many composites over many masters from one reviewed list.

Undo: FontLab's builder writes each layer itself, so Edit > Undo of a rebuilt
existing layer depends on FontLab; Undo of a new glyph is FontLab's Add Glyph
step. Keep a saved copy of the font. The status line says how many layers
were built.

Safety: Check before Build: Build stays off until every line passes. The
script refuses, before any change, when:

- an existing target glyph has an automatic layer, or is the base of an
  automatic composite (FontLab rebuilds the composite and Undo does not
  restore it);
- FontLab holds queued glyph updates (they would alter other glyph dates);
- a line contains a character that FontLab's text conversion can change
  (NUL, no-break space, line or paragraph separator).

If a build fails part-way, the error names it; the layers built before it
stay. The refusal rules and the panel are shared with other scripts
(fly.ap.component_writer, fly.ap.component_panel, fly.ap.history,
fly.ap.edit_guards); the recipe parser and the panel controls belong to
this script.

Source: the author's own FontLab sample
components_build_from_recipes.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Components > Build From Recipes** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7550b49a4b16961169be06b8341f3fc0aada9684edc7bc52c12acedb3ccf702b.py)
<!--/codeinclude-->
