---
this_file: src_docs/md/scripts/names/unicode-from-names.md
tags: ["Names"]
categories: ["Names"]
---

# Unicode From Names

Assign Unicode code points that the glyph names imply. Preview first.

WHAT: A non-modal panel reads glyph names and lists the code point each name
implies. It knows uniXXXX and uXXXX[XX] names, a built-in table of Adobe Glyph
List names, and accented Latin names (Wacute is LATIN CAPITAL LETTER W WITH
ACUTE, found with unicodedata). Names with a suffix (a.ss01), ligature names
(f_i) and surrogate code points (U+D800 to U+DFFF) are left alone. Assign writes all rows marked "assign".

HOW: The script scans the font and plans each row: "same" (already right),
"encoded differently" (the glyph has another code and Replace is off), "used by
X" (another glyph already owns the code, or an earlier row claims it), a
refusal reason, or "assign". The write rescans, then sets the code points on
the font-owned FontGate record as one Undo step. It reads each list back and
compares it with the plan. The scan, the refusal policy and the one-step write
come from the shared module fly.ap.names_edit. If a write fails part way, every
planned glyph is still notified and stamped, and the message asks you to use
Edit > Undo.

WHY: A code point must belong to one glyph only. The plan never steals a code
from another glyph and never lets two rows claim one code. FontLab rebuilds all
auto layers when an auto layer, or the base glyph of an auto composite (also
through other composites), is notified, and Undo does not restore them. So the
script REFUSES such glyphs. It never reads flGlyph.fgGlyph, never calls
UpdateAll (fl#8537), and refuses to write while native updates are pending.
Before it writes, the script applies the guards of the App Unicode writer: a
regular Font window must be active and no Glyph editor may be open.

USE: Select glyphs in the Font window, or choose "All glyphs in the font". Run
the script. Check the table. Press Assign.

BENEFIT: Fonts built from named outlines get a correct character map in one
previewed, undoable step.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. Native acceptance pending.

Run **Names > Unicode From Names** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0d2a2cc59388ec95df9f7bb850b7664bfc404cbd6d5f3ec7f11f25c402373819.py)
<!--/codeinclude-->
