# this_file: Scripts/Metrics/Zero-Width Marks.py
# SPDX-License-Identifier: Apache-2.0
"""Launch the preserved Zero-Width Marks sample.

Purpose: The preserved sample describes this task:
Set the advance width of combining marks to zero, keeping or re-placing
their outlines.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Metrics > Zero-Width Marks in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/metrics_zero_width_marks.py
"""

from pathlib import Path


def main() -> None:
    """Dispatch the preserved sample only when explicitly run."""
    from fly.ap.rescued_examples import launch

    launch(Path(__file__).resolve().parents[2] / "rescued/samples/metrics_zero_width_marks.py")


if __name__ == "__main__":
    main()
