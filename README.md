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

Sources remain in the examples archive until native acceptance. `migration.json`
records Apache-2.0 provenance and hashes. Owned-double tests pass outside FontLab;
these scripts have **not yet been verified in the native host**.
Run `./test.sh` for the host-free tests.

A failed scan or table refresh invalidates selection until a complete rescan
succeeds. Partial results are cleared; explicit selection calls also refuse them.
