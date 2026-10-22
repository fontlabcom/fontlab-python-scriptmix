# this_file: Scripts/Contours/Angularizzle.py
# SPDX-License-Identifier: Apache-2.0 AND MIT
"""Turn selected closed outlines into angular planes with a modeless preview.

Min plane defaults to 80; Keep detail preserves short segments. Single-layer
Process always samples the opening selected layer and writes its glyph's first
master. Process can repeat; Cancel restores that actual target's opening paths
while retaining the source tool's colour mark. Closing keeps processed paths.
Batch Process follows ordered selected occurrences, including repeats, then
closes. Open paths are omitted when a closed angular result replaces paths.

The bound session refuses stale sources, unsupported hints, automatic
dependants and ambiguous shape ownership before editing. A late native failure
disables further writes and retains recovery data; close the panel and inspect
the diagnosed result before continuing.
Requires matching App/Fly candidates. Adapted from NaN Angularizzle; see NOTICE.
"""


def main() -> None:
    """Load shared App controls through Fly when the menu is invoked."""
    from fly.ap.scripting import angularizzle_dialog_type, show_script_dialog

    panel = angularizzle_dialog_type()
    show_script_dialog(panel, panel.KEY)


if __name__ == "__main__":
    main()
