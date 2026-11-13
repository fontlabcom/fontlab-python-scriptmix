# this_file: Scripts/Font UI Lab/Font Info and Vertical Metrics.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Font UI Lab · Font Info and Vertical Metrics
"""Stage font information beside the captured font's vertical metrics report.

Use: Open a font and run this tool. Edit information and explicitly Apply, or
Revert to reload it. Refresh metrics report preserves staged edits. Values are
for the captured font's current info source, not an all-master comparison.
The report lists OS/2 typo, hhea and Windows ascent/descent values, retaining
unset values separately from explicit zero. If a metric cannot be read or is
not finite, the report clears and shows the error; Refresh retries the read.
Switching the active font does not retarget this window. Open another instance
to edit another font. Closing the window disconnects its callbacks and releases
only its owned controls, leaving the borrowed document open.
The shared editor validates writes; the report never writes, saves or closes
fonts. Native history and saved/reopened behavior need separate qualification.
"""


def main():
    """Capture the current font once and retain its shared owned editor."""
    from fly.fp.world import FontWorld
    from fly.ap.fontui.font_info_metrics import show
    return show(FontWorld().CurrentFont())


if __name__ == '__main__':
    main()
