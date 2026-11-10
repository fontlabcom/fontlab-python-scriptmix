# this_file: Scripts/Font UI Lab/Batch UFO Recipe Workbench.py
# SPDX-License-Identifier: Apache-2.0
"""Build an affine recipe and apply it to explicitly selected UFO directories.

What: The real transform controls provide six matrix numbers, an exact intensity
percentage, Enabled and Reset transform. There is no current-font capture or
geometry preview: the editor intentionally reports No font supplied. The batch
panel shows the actual per-file log, progress and status from its external worker.

Use: Select source UFO directories and an output directory. Configure an external
Python 3.11 or newer with Fontport through FONTLABAPP_BATCH_PYTHON before starting.
The shared show(parent=None, python=None) API also accepts an explicit interpreter.
Click Start to write `<source-name>-transformed.ufo` outputs. Editing controls or
opening this window does not start a batch. Invalid recipes and paths refuse Start.

Safety: Existing outputs are never overwritten, and outputs inside any selected
source UFO are refused, including filesystem aliases. Source files are read when
each job runs; do not edit them concurrently. Cancel takes effect between files,
so a current job may finish and completed outputs remain. A file failure can be
followed by successful files. A success row reports transform/save completion,
not independent reopened-font validation. Native-only hints and host editing
history are outside this directory-UFO transformation. Closing fences the UI and
hands an active process to the existing supervisor; handoff is not instant exit.
"""


def main():
    """Open the real recipe-only workbench without reading a current font."""
    from fly.ap.fontui.batch_recipes import show

    return show()


if __name__ == "__main__":
    main()
