# this_file: Scripts/Reports/Report Glyph Set Differences.py
# SPDX-License-Identifier: MIT AND Apache-2.0
"""Report Glyph Set Differences using the current font as the original reference.

Open a current reference font; with no other open font the report is empty. Every other open font is compared. Raw filepath headings, target-order extra glyphs and reference-order missing glyphs are preserved.
Refresh repeats the complete original scan; select/copy report text normally.
Close releases only this owned nonmodal report. No font/master activation,
selection/history/preferences/Output/clipboard writer is called. Full native
getter preservation and PythonQt literal-text/lifetime qualification are pending.
Adapted from Jens Kutilek's MIT source; see NOTICE and additional-tools.json.
Requires App>=0.2.26.dev325 through Fly in FontLab Python3.11.
"""

def main() -> None:
    """Load the package-owned complete comparison lazily through Fly."""
    from fly.ap.crossfont_reports import show
    show(composites=False)

if __name__ == "__main__":
    main()
