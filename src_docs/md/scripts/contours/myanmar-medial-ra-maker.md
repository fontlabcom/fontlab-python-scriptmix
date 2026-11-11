---
this_file: src_docs/md/scripts/contours/myanmar-medial-ra-maker.md
tags: ["Contours"]
categories: ["Contours"]
---

# Myanmar Medial Ra Maker

Generate width-fitted Myanmar medial-ra variants on every FontLab master.

What: Group consonants on the current master. Fit the same group members on
all masters, using each master's mean advance minus its own template enclosure.
Names use the current master's group means floored to tens. Also create eight
unstretched omission variants. Existing names and targets with a bad master
are kept, with the master and reason listed.
How: Read U+1000–U+1020 by Unicode or hexadecimal name. Verify the five pieces:
stem, top rail, top hook, bottom rail, bottom hook. The stem must be tallest;
top pieces above bottom pieces; hooks right of rails. The rails' closing edges
must be on their right, the hooks' on their left. Copy through the shared App
contour copier. Show every target's extension and node/handle bounds on every
master in the Preview table. Apply refuses source data changed since Preview.
Why: Fit this five-part Myanmar outline to consonant width groups.
All-master output keeps the generated glyph structure
consistent across masters; a failed template keeps the entire target.
Use: Select one template, or leave the selection empty to use U+103C. Inspect
Preview and consent to any listed automatic-glyph rebuilds, then Apply.
Each new glyph is recorded as its own Undo step, and the outlines as one more Undo step.
Benefit: Produce a compatible set of fitted medial-ra variants for refinement.

Credit: Independent behaviour-only rewrite of Simon Cozens,
GlyphsScripts/Myanmar Medial Ra Maker.py, MIT, copyright 2017.
Repository: https://github.com/simoncozens/GlyphsScripts . No source code copied.

Run **Contours > Myanmar Medial Ra Maker** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `61690c07f8852a18c2fbeba9b4d242e4e834cfc86fed9a1501c35642abc7db35`

[Python source at `6b1048c4f1db`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6b1048c4f1dbc64ebe49d419db9193ccb3d9a9f0/Scripts/Contours/Myanmar%20Medial%20Ra%20Maker.py)
