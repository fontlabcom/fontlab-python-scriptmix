# this_file: Scripts/Contours/Placeholder Glyphs.py
# SPDX-License-Identifier: Apache-2.0
"""Launch the preserved Placeholder Glyphs sample.

Purpose: The preserved sample describes this task:
Create empty placeholder glyphs from pasted glyph names or characters, on
every master.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Contours > Placeholder Glyphs in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/generate_placeholder_glyphs.py
"""

from pathlib import Path


def main() -> None:
    """Dispatch the preserved sample only when explicitly run."""
    from fly.ap.rescued_examples import launch

    launch(Path(__file__).resolve().parents[2] / "rescued/samples/generate_placeholder_glyphs.py")


if __name__ == "__main__":
    main()
