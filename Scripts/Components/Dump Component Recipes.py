# this_file: Scripts/Components/Dump Component Recipes.py
# SPDX-License-Identifier: Apache-2.0 AND MIT
"""Dump ordered recipes for selected component glyphs in Font/Glyph windows.

Select glyphs or editor layer occurrences, then run this command. The modeless
read-only report gives one `base+base=glyph` line per layer with components.
Selected-layer order, repeated occurrences/bases and mixed layers are retained.
The source format omits positions, transforms and own contours; the text is a
composition aid, not a complete geometry export or a guaranteed import recipe.

Use Refresh after changing the font, master or selection. Empty/missing/stale
sources and deadline overruns give a clear diagnosis; partial rows are cleared.
Close releases this owned panel. The report calls no font, selection, history,
preferences, clipboard or Output writers. Requires matching App and fontlab-fly
in FontLab9 Python3.11. Adapted from Simon Cozens' MIT Recipe Dumper; see NOTICE.
The shared reader retains each editor slot’s explicit layer choice. Font-window
selection uses the current master. Actual FontLab behavior and complete native
preservation remain pending acceptance.
"""


def main() -> None:
    """Load shared App support only when this menu runs."""
    from fly.ap.scripting import component_recipes_dialog_type, show_script_dialog

    panel = component_recipes_dialog_type()
    show_script_dialog(panel, panel.KEY)


if __name__ == "__main__":
    main()
