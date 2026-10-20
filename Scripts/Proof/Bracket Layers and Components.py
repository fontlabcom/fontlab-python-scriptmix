# this_file: Scripts/Proof/Bracket Layers and Components.py
# SPDX-License-Identifier: Apache-2.0
"""Find bracket-named glyphs and all transitive component dependants.

Scan every glyph and every foreground layer in the current font. A single layer
name must contain both [ and ]; this name pattern does not establish export rules.
Mask/service layers are background/cache records. Include direct and indirect
component users across all foreground layers, including cycles and group overlap.

Open both sorted groups in a fresh Glyph tab in the captured font/master.
Both groups retain overlapping names. The report counts their union and explains
overlap; the proof uses explicit named symbols, deterministic order and literal
headings, without empty-section orphan slashes or Unicode substitution.
An empty proof result diagnoses the source condition without opening a tab.

Complete source/context rechecks refuse unreadable, changing or expired scans.
No Output panel clearing or source font/master/selection/history/preference edit
is requested. Native read/cache, symbol/layer mapping, full font preservation and
UI acceptance remain pending. A failed tab creation/population may leave a new tab.

Requires reviewed App>=0.2.53.dev0 and FontLab9 Python3.11 with fontlab-fly.
Adapted from Reset Type Studio's New Tab with Glyphs containing BL.py.
Copyright2025 Fernando Díaz & Reset Type Studio. See NOTICE and additional-tools.json.
"""


def main() -> None:
    """Run the complete shared workflow through the lazy Fly namespace."""
    from fly.ap.bracket_layers import open_tab

    open_tab()


if __name__ == "__main__":
    main()
