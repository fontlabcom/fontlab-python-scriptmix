# this_file: Scripts/Metrics/Copy Metrics From Reference.py
# SPDX-License-Identifier: Apache-2.0
"""Launch the preserved Copy Metrics From Reference sample.

Purpose: The preserved sample describes this task:
Give the selected glyphs the sidebearings or the advance width of a
reference glyph.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Metrics > Copy Metrics From Reference in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/metrics_copy_from_reference.py
"""

from pathlib import Path


def main() -> None:
    """Dispatch the preserved sample only when explicitly run."""
    from fly.ap.rescued_examples import launch

    launch(Path(__file__).resolve().parents[2] / "rescued/samples/metrics_copy_from_reference.py")


if __name__ == "__main__":
    main()
