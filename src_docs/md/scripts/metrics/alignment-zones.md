---
this_file: src_docs/md/scripts/metrics/alignment-zones.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Alignment Zones

Edit the alignment zones of every master in one table; Apply is one Undo step.

What it does:
    Opens a non-modal panel for the current font. Pick a master to list its top
    and bottom zones. Add a top or bottom zone, remove the selected rows, or edit
    the position, width and name. "Suggest from o / O" replaces the chosen
    master's zones with zones from the overshoots of o and O at the baseline,
    x-height and cap height. Edits stay staged for each master until Apply. Apply
    writes every changed master as one Undo step; the current master does not
    change. A top zone covers the area above its position, a bottom zone the
    area below.

How it works:
    The panel and its zone model are shared with the App. The native backend
    reads each master's zones and metrics, then puts the current master back.
    Apply checks that the font, its masters and its zones are still as read,
    then writes each changed master as FontLab's Font Info does and reads all
    masters back.

Why this design:
    One shared panel and one zone writer keep the staging rules, the refusals
    and the Undo step the same for every tool that edits zones.

How to use:
    Open a font, activate its Font window and run Metrics > Alignment Zones.
    Edit the zones of each master, then press Apply. Use Edit > Undo in the Font
    window to revert the whole Apply. Reopen the panel after you switch fonts.

Benefit:
    Stage the zones of a whole family together and apply them in one step.

Limitations:
    - Every zone needs a name, unique within its master's top or bottom list.
      Added rows get FontLab's names, such as "T: 500" or "B: 0". Apply refuses
      an empty or repeated name, and a zero-width row that FontLab would read
      as the other kind; the panel stays open so that you can fix the row.
    - A cell that is not a number rejects the whole table; no row is dropped.
    - Apply needs the Font window of this font as the active window. It refuses
      while a Glyph window is the active canvas.
    - Apply re-creates every zone guide of a changed master: the guides get new
      ids, x-centre 0 and the font guideline style. Only position, width,
      name, tags and lock stay. A failed Apply that restores the zones also
      re-creates the guides. Font Info does the same.
    - FontLab defect fl#8574: after Edit > Undo or Redo, the metric guides
      show 3 of 9 lines until you reopen the font. The saved file is correct.
    - The panel does not refresh FontLab's other windows with UpdateAll.

Credit:
    Adapted from metrics_zones_editor.py, the author's own FontLab sample,
    Apache-2.0. Its table and staging live in the shared App panel.

Run **Metrics > Alignment Zones** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0dbd56629eaddc7c640a66aeede1dd1d4888d4af6f37fb18bdedb5f175a9810d.py)
<!--/codeinclude-->
