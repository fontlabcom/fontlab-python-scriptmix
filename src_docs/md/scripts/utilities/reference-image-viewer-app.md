---
this_file: src_docs/md/scripts/utilities/reference-image-viewer-app.md
tags: ["Utilities"]
categories: ["Utilities"]
---

# Reference Image Viewer App

View a reference image beside your font in the shared App shell.

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

Run **Utilities > Reference Image Viewer App** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `531d0489346bd551a76b8b57e30b2324594eed3614512eeb78debe3bce01f907`

[Python source at `8852124d9fe2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8852124d9fe2b69cf663e1c6db8d6db4bf5e8454/Scripts/Utilities/Reference%20Image%20Viewer%20App.py)
