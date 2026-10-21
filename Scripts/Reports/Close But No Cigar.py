# this_file: Scripts/Reports/Close But No Cigar.py
# SPDX-License-Identifier: MIT AND Apache-2.0
"""Report nearly correct angles, stem lengths and node positions in every selected glyph's first layer.

Select glyphs in a Font or Glyph window, then run this script. The modeless,
read-only report offers selectable text, Refresh and Close. It uses the first
layer in each selected parent, not the selected or active layer, and that layer's
associated named master's PostScript stems and ascender, cap height, x height
and descender. Every own contour and node, including handles, is checked.

Original strict boundaries and exact-value exclusions remain: angles within
2 degrees of 0/180/+90/-90, stem lengths within 5%, and coordinates within
2 units of zero or the four metrics. Exact match to any stem suppresses all
near matches for that orientation. Duplicate targets and selected occurrences
remain ordered. Components are omitted; own shape transforms are applied.

Simon Cozens' glyphmonkey wraps last-to-first even for open paths; this report
retains that edge and its 50-step cubic-length sampling (last sample below 1).
It repairs the cubic angle method/property bug. Empty contours are safe.
Quadratic/malformed segments, generated/projective shapes, unknown associated
masters and unreadable or changed sources refuse the entire report. Refresh
clears failed results. No Output, font, selection, history, preference, clipboard
or file writer runs. Native getter preservation and lifetime remain pending.
Requires FontLab 9 Python 3.11, Fly and App 0.2.93.dev0 or later.
Adapted from Simon Cozens' Close But No Cigar.py and glyphmonkey.py (MIT).
Complete source hashes, contract, fixes and licence are in NOTICE and provenance.
"""


def main() -> None:
    """Open the shared owned report lazily, within FontLab's import deadline."""
    from fly.ap.near_miss import show

    show()


if __name__ == "__main__":
    main()
