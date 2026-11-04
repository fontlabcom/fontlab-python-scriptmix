# this_file: Scripts/Utilities/Reference Image Viewer.py
# SPDX-License-Identifier: Apache-2.0
"""View a reference image beside your font, with zoom and fit controls.

What: Opens a modeless image viewer for the artwork you design from: a
specimen scan, a sketch or a photograph of lettering. Open a local image file
and zoom in and out, fit it to the window or return to its normal size. The
viewer scrolls around the image and keeps the zoom centred. A print command
sends the image to a printer at native pixel size.

Use: Run Utilities > Reference Image Viewer. Choose File > Open and pick an
image. Zoom with the menu or its shortcuts, or use Fit to window. Choose File >
Print only when you want a paper copy. Close the window when you are done.

Safety: The viewer reads the image file you choose and writes nothing to it.
It does not read or write font data, selection, history, preferences,
clipboard or Output text. Printing happens only when you choose Print and
confirm the printer dialog. If printing needs a scratch file, it is created in
a private temporary folder owned by the viewer, and the viewer removes that
folder when it closes. Open, print and help dialogs are asynchronous and
belong to the viewer.

Source: Original workflow built on the shared App image viewer
(fly.ap.qt.images.viewer.model), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.
"""

from typing import Any


def main() -> Any:
    """Open the shared image viewer, or replace the one already open."""
    from fly.ap.qt.images.viewer.model import show

    return show()


if __name__ == "__main__":
    main()
