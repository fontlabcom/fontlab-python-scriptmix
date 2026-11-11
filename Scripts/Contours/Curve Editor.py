# this_file: Scripts/Contours/Curve Editor.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Curve Editor
"""Inspect and apply outline changes through named task tabs and a live glyph view.

Convert straights to cubics, straighten all or only short curves, retract
handles, or simplify selected polygon nodes.
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

Requires FontLab App with the Curve Editor composition and fontlab-fly.
Sources: FontLab App contributors, Apache-2.0; independent adaptations after
Simon Cozens (MIT) and Pedro Arilla (Apache-2.0). See Scriptmix NOTICE and the
preserved provenance manifests for the complete original source identities.
"""


def main():
    """Open the owned studio through Fly."""
    from fly.ap.fontui.outline_editing import show

    return show('Curve Editor')


if __name__ == "__main__":
    main()
