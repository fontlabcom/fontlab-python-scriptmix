# this_file: Scripts/Utilities/Reference Image Viewer App.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Utilities · Reference Image Viewer App
"""View a reference image beside your font in the shared App shell.

What: Opens the same read-only image viewer as Reference Image Viewer, inside
the shared App window with an About tab (source links and credits) and a Close
button. Open a local image, zoom, fit to window, return to normal size or print.

Use: Run Utilities > Reference Image Viewer App. Choose File > Open and pick an
image. Close the window with Close, Escape or File > Exit. If cleanup is
refused, the window stays open and Close can be retried.

Safety: Reads only the image you choose and writes nothing to it. It does not
read or write font data, selection, history, preferences, clipboard or Output.
Printing happens only after you confirm the printer dialog. Run it from the
main UI thread; the viewer owns its dialogs and removes its scratch folder.

Source: Original workflow on the shared App image viewer, Apache-2.0
(fly.ap.fontui.reference_images). Requires the App with WP08 S64 assembly and
fontlab-fly in FontLab 9 Python 3.11.
"""

from typing import Any


def main() -> Any:
    """Open the Reference Image Viewer app."""
    from fly.ap.fontui.reference_images import show

    return show()


if __name__ == "__main__":
    main()
