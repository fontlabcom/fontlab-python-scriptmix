---
this_file: README.md
---

# fontlab-python-scriptmix
Small and useful scripts for FontLab

## Reports (issue 111 first batch)

Copy the contents of `Scripts` into your FontLab Scripts menu folder. Keep the
category subfolders, such as `Reports` and `Font Info`; FontLab supports one folder level. Use FontLab 9's
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

## Font Info tools

The Font Info menu includes Glyph Order Preview and Export, Master Metrics
Table, Names and Credits, Unicode Ranges and Codepages, Bump Font Version and
Calculate Vertical Metrics. All original controls, embedded Unicode data,
assessment notices, export, previews and the metric diagram are retained.

Names changes style on the original current master and credits font-wide.
Master Metrics edits every displayed master. Version bump optionally appends a
dated note to every master. Vertical Metrics defaults to hhea and Win; Typo is
optional because it also moves FontLab's own ascender/descender lines. Its bounds
are captured on open; reopen after outline changes. Glyph Order exports UTF-8
text without reordering the font; Unicode coverage reports without editing it.

Apply uses the last complete preview, refuses closed/switched fonts and changed
source values, validates the entire plan before writes, preserves the active
master and rolls back attempted fields on failure. Failed previews disable Apply.
Names and current-master vertical metrics also refuse a master switch. No-op
plans add no history. The shared metadata helper notifies only the package and
its master container. Fontport's existing history protocol may add an extra
no-op Undo checkpoint. All six pass their original native scenarios on FontLab
9.0.9784. All four editors pass one-step Undo, Redo, saved metadata reopening and
complete font-data preservation. Native tests also verify no-op history and
switched-font refusal. Shared panels load lazily through Fontlabapp; each tool
keeps its own controls and actions. Glyph Order uses an owned modeless save
chooser and reports the exported count and filename.


The six Font Info panels now share App's lazily loaded FontInfoDialog shell via
fly.ap.scripting.font_info_dialog_type(). Existing controls/actions and the owned
export chooser are unchanged. Native workflows, editor persistence and Close
destruction pass on the current shared implementation.

## Feature tools

Features contains Alternate Preview, Build Suffix Substitution, Classes Browser,
Feature Code Viewer, Ligature Finder and Suffix Report. They preserve the
original master proof, filters, selection, literal search/highlights and Copy
controls. Proof rows use one outline scale per master and wrap large families.

Build previews actual suffix substitutions and appends them to the requested
feature, retaining prefix, ordered unrelated features and classes. Apply binds
to the original font, complete feature source and referenced glyphs. It uses
Fontport's existing ordered writer and Undo safety checks through App, skips
no-ops and reports unexpected native failures as possibly partial. Install
App's optional `fontedit` dependency for Build and Feature Code Viewer; native
`fontpr` must be available. The viewer reads exact stored prefix/ordered blocks,
rather than native iterator values or synthesized class-prefix text.
It does not compile features: test the result in FontLab's Features panel.

These six tools pass their native scenarios and actual Close destruction.
The builder passes complete feature-only saved deltas, one-step Undo, Redo and
reopening. All20migrated tools pass183workflow checks together on FontLab9.0.9784.
Clipboard operations remain host-free tested; native checks inspect the actual
suffix preview under the owner's clipboard exclusion.
No export chooser is needed: these six originals provide Copy, not file export.
