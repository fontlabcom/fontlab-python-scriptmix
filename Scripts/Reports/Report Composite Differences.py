# this_file: Scripts/Reports/Report Composite Differences.py
# SPDX-License-Identifier: MIT AND Apache-2.0
"""Report Composite Differences using the current font as the original reference.

Open two or more fonts. Only the first other open font is compared, using each font selected named master. Ordered component names and source-order missing glyphs are reported; only exact .sc/.pcap suffixes are excluded from missing rows.
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
    show(composites=True)

if __name__ == "__main__":
    main()
