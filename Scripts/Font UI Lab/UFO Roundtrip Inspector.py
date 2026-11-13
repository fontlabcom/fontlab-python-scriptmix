# this_file: Scripts/Font UI Lab/UFO Roundtrip Inspector.py
# SPDX-License-Identifier: Apache-2.0
"""Stage a borrowed font in a private temporary directory and inspect its roundtrip.

Use: Open a font and run this tool. Run the inspector to export and reopen an
owned staged UFO, then inspect the complete semantic comparison and diagnostics.
Safety: The source is never overwritten or closed. Temporary staging belongs
to the inspector. FontLab preservation, history and native UI lifetime still
require native qualification.

The inspection button runs an explicit snapshot/export/reopen/import comparison.
Read every difference and limitation in the report: a successful disk reopen
does not establish lossless native font conversion. The temporary result is
not an editable replacement for the source document. Run inspection again to
refresh the report after deliberate source changes. Closing the inspector
releases its callbacks and owned UI without closing the borrowed font."""


def main():
    """Capture the current borrowed font once and return its owned inspector."""
    from fly.ap.fontui.ufo_roundtrip import show
    from fly.fp.world import FontWorld

    return show(FontWorld().CurrentFont())


if __name__ == "__main__":
    main()
