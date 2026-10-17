---
this_file: README.md
---

# fontlab-python-scriptmix
Small and useful scripts for FontLab

## Reports (issue 111 first batch)

Copy the contents of `Scripts` into your FontLab Scripts menu folder. Keep the
single `Reports` subfolder; FontLab supports one folder level. Use FontLab 9's
Python 3.11 with `fontlab-fly` and `fontlab-fontlabapp` (including `scripting`)
available in its Python environment. No third-party UI package is needed.

Open a font, then run Empty Glyphs, Open Contours or Font Overview from Reports.
The dialogs are modeless: edit the font and Rescan/Refresh when needed. Empty
Glyphs can hide intentional whitespace. Select chosen rows, or leave rows
unselected to select all results. Selection refuses results after changing the
current font; rescan first. Reports read all masters without changing geometry.
Closing a report disconnects its signals. Re-running replaces its old window.
Close also destroys the native dialog after its event finishes. All eight
reports share this lifecycle code through `fly.ap.scripting`.

Sources remain in the examples archive until the full migration is reconciled.
`migration.json` records Apache-2.0 provenance and hashes. All three reports passed
their original native scenarios in FontLab 9.0.9784 with the installed helper
wheel: 26 independent checks, screenshot review and owned-window/font cleanup.
Run `./test.sh` for the host-free tests.

A failed scan or table refresh invalidates selection until a complete rescan
succeeds. Partial results are cleared; explicit selection calls also refuse them.

## Reports: second migration batch

Live Glyph Info follows the selected glyph twice a second, with per-master
metrics, outline/component/anchor counts and Pause. Glyph Table CSV offers all
or selected glyphs, sortable widths/counts, Copy CSV and a modeless UTF-8 CSV
save chooser. Label Statistics shows mark colours and suffix groups; Add to
selection preserves the current selection. Nodes Near Zones checks transformed
on-curve nodes across masters with selection scope and a 1–30 unit tolerance.
Unicode Coverage includes untouched-block filtering, progress bars and block
selection. Explicit selection is bound to the font that supplied the rows.

All five retain the original interactions and Apache-2.0 provenance. Their
original scenarios pass on FontLab9.0.9784:42independent checks, reviewed
screenshots and owned font/dialog cleanup, including the live timer. Host-free
tests for all eight reports pass on Python3.11 (47tests).
