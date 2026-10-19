# this_file: Scripts/Components/Dump Component Recipes.py
# SPDX-License-Identifier: Apache-2.0 AND MIT
"""Dump ordered recipes for selected component glyphs on the active master.

Select glyphs in the Font window, then run this Components command. The modeless
read-only report gives one `base+base=glyph` line per layer with components.
Component order, repeated bases and mixed contour/component layers are retained.
The source format omits positions, transforms and own contours; the text is a
composition aid, not a complete geometry export or a guaranteed import recipe.

Use Refresh after changing the font, master or selection. Empty/missing/stale
sources and deadline overruns give a clear diagnosis; partial rows are cleared.
Close releases this owned panel. No font, selection, preferences, clipboard or
Output content is changed. Requires the matching App candidate and fontlab-fly
in FontLab9 Python3.11. Adapted from Simon Cozens' MIT Recipe Dumper; see NOTICE.
Native acceptance and original editor-tab/repeated/multi-master selected-layer
semantics remain pending. This candidate uses Font-window active-master input.
"""


def main() -> None:
    """Load shared App support only when this menu runs."""
    from fly.ap.scripting import component_recipes_dialog_type, show_script_dialog

    panel = component_recipes_dialog_type()
    show_script_dialog(panel, panel.KEY)


if __name__ == "__main__":
    main()
