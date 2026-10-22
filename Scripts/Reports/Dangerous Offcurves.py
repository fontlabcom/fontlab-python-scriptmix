# this_file: Scripts/Reports/Dangerous Offcurves.py
# SPDX-License-Identifier: Apache-2.0
"""Find dangerous offcurves throughout every glyph and foreground layer.

Scan all own paths, including auxiliary and empty layers, without selection
filtering or component decomposition. Each first offcurve retains the original
four-node neighbour window (also for open/quadratic paths), four finite axis
probes at ±10000, all-four-hit gate and any strict distance below0.05 units.
Open a genuine new tab containing every distinct matching exact layer in stored
order, and show every per-curve finding in an owned selectable result window.
No matches gives the complete original diagnosis. Close and rerun for a fresh
scan. No font, selection, history, clipboard, preferences or Output writer runs.

Requires App[fontui]>=0.2.117.dev0 and public Fly in FontLab9 Python3.11.
fontTools analytic intersections use ascending curve t for first-result choice,
an explicit adaptation of unspecified Glyphs ordering. Exact endpoints and
finite-line bounds use the shared geometry code; coincident intersections follow
the geometry backend. A failure yields
no partial report; failed tab creation can leave a new owned tab.

Adapted from Alex Slobzheninov's Bug fixing/Dangerous Offcurves.py,
Apache-2.0; upstream attribution and exact source pin are retained in NOTICE.
"""


def main() -> None:
    """Run the complete all-font action through the lazy public Fly facade."""
    from fly.ap.dangerous_offcurves import show

    show()


if __name__ == "__main__":
    main()
