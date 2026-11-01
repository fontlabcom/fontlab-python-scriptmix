# this_file: Scripts/Reports/Smallcap Consistency.py
# SPDX-License-Identifier: Apache-2.0
"""Report missing smallcaps, orphan smallcaps and capital kerning-group differences.

What it does:
    Count exporting upper, lower and smallcap glyphs. List missing .sc/.smcp
    and .sc/.c2sc counterparts, orphan smallcaps, missing capitals/lowercase
    and left/right smallcap-to-capital kerning-group differences.

How it works:
    Capture detached metadata from the current font and master. Use Unicode
    case mappings with alternate suffixes intact, including ligatures and
    multi-character mappings. Exact SC suffix particles identify smallcaps.
    The public.skipExportGlyphs compatibility list defines export scope;
    this is not a guarantee about FontLab's binary exporter. Unknown name
    mappings and ambiguous groups appear separately. A three-second budget
    refuses partial reports; synchronous getters are checked on return.

Why this design:
    Keep both modern and legacy checks from mekkablue's Check Smallcap
    Consistency while correcting its Boolean counterpart test. A report
    exposes incomplete sets without changing glyphs, selection or history.

How to use:
    Open a font and run Reports > Smallcap Consistency. Read the named
    sections in the non-modal report. Run again after changes to refresh the
    same owned report window. Close the report when finished.

Benefit:
    Find gaps in a smallcap set and its kerning groups before proofing.

Credits:
    Workflow: mekkablue, Glyphs-Scripts/Smallcaps/Check Smallcap Consistency.py,
    Apache-2.0. This FontLab implementation does not copy the original body.
"""

from typing import Any

import fly.ap.reports as reports
import fly.ap.smallcap_capture as smallcap_capture


def main() -> Any:
    """Capture afresh before opening or replacing the owned report."""
    report = smallcap_capture.current_report()
    return reports.show_report(
        report, title="Smallcap Consistency", key="report_smallcap_consistency"
    )


if __name__ == "__main__":
    main()
