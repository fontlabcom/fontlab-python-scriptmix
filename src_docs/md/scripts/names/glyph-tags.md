---
this_file: src_docs/md/scripts/names/glyph-tags.md
tags: ["Names"]
categories: ["Names"]
---

# Glyph Tags

Add tags to, or remove tags from, the selected glyphs in one step.

WHAT: A non-modal panel lists each tag used by the selected glyphs and how
many glyphs carry it. Type a tag and press Add, or tick tags and press Remove.
The tag field completes from all tags in the font.

HOW: The script reads the selection through the shared App selection reader. It
then scans the whole font once. For each edit it rescans, builds a plan, and
writes the plan as one Undo step. After the write it reads each tag list back
and compares it with the plan. The scan, the refusal policy and the one-step
write come from the shared module fly.ap.names_edit. If a write fails part way,
every planned glyph is still notified and stamped, and the message asks you to
use Edit > Undo.

WHY: FontLab rebuilds all auto layers when an auto layer is notified. Undo
does not restore the rebuilt layers. So the script REFUSES glyphs that own an
auto layer and never puts an auto layer in the notify list. A base glyph of
an auto composite may be tagged: its tags do not reach the composites (native
check pending). The script never reads flGlyph.fgGlyph (that getter can clear
a fresh glyph note on build 9784). It never calls UpdateAll (that feeds the
fl#8537 pending-update queue). It discloses queued ids and their possible date
changes.

USE: Select glyphs in the Font window. Run the script. Press Reload selection
after you change the selection. A tag has 1 to 64 characters, no spaces and
no commas.

BENEFIT: Review states, spacing status and similar marks stay on the glyphs
and travel with the font. One Edit > Undo reverts one Add or Remove.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. The edit is recorded as one Undo step.

Run **Names > Glyph Tags** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9e56cdc339d9dc152b0bb7e456d3633379104d6bade7edf3247093912746cdf2.py)
<!--/codeinclude-->
