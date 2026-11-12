---
this_file: src_docs/md/scripts/utilities/reference-image-viewer.md
tags: ["Utilities"]
categories: ["Utilities"]
---

# Reference Image Viewer

View a reference image beside your font, with zoom and fit controls.

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
confirm the printer dialog. Qt's print dialog can send the image to a printer
or write a PDF to any path you pick there. If printing needs a scratch file,
it is created in a private temporary folder owned by the viewer, and the
viewer removes that folder when it closes. Open, print and help dialogs are asynchronous and
belong to the viewer.

Source: Original workflow built on the shared App image viewer
(fly.ap.qt.images.viewer.model), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.

Run **Utilities > Reference Image Viewer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `457e2b3ccec7b7c6261d7c3100ca8db9264208a85c8f7730f27d6df906e065fe`

[Python source at `cca80db1b47f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/cca80db1b47f998bbbf4a26427a1e5949ccf7230/Scripts/Utilities/Reference%20Image%20Viewer.py)
