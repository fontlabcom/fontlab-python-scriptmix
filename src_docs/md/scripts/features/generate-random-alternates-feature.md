---
this_file: src_docs/md/scripts/features/generate-random-alternates-feature.md
tags: ["Features"]
categories: ["Features"]
---

# Generate Random Alternates Feature

Generate seeded contextual alternate feature source for the current font.

What: Build random context classes and substitution lookups from user-supplied
base/alternate rows. Keep the seed to reproduce exactly the same source.
How: Read the current glyph catalogue. Assign category members to nonempty
classes, then choose a target and context for each rule using a local RNG.
Why: OpenType contextual substitutions are deterministic. Random generation
makes varied rules; it does not make the shaping engine choose randomly.
The native Features editor accepts source, but does not generate seeded contexts.
Use: Open a font, enter one base and its alternates per line, adjust counts,
categories and seed, then Preview. Copy feature sends the complete generated
source to the clipboard. Write feature replaces the code for the previewed
feature tag only after Replace existing feature is ticked for a differing
block. Preview shows existing and generated code side by side. Adding a tag
or writing identical code needs no confirmation. Changing input or refreshing
resets the tick. The shared source-bound writer preserves other
features and the prefix stay unchanged. Each changing write is recorded as one
Undo step. Compile and test in FontLab's Features panel after writing.
Benefit: Review and reproduce varied alternates without manual rule entry.
The non-modal panel shows the exact block that Write feature stores. The category filter
uses Unicode general categories, with base-name inheritance for suffix glyphs;
unencoded names without an encoded base match only All. Export flags are not
used. Classes stay inside the generated feature block.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Features/Generate Random Alternates Feature.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.

Run **Features > Generate Random Alternates Feature** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/8f30b07c8163c93e0c19227306f6f6a6a37604082469affd271276af79ca465b.py)
<!--/codeinclude-->
