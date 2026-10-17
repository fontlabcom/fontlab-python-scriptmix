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

## Host-free distribution checks

Run with Python 3.11 through uv and an explicit current App requirement:

```sh
SCRIPTMIX_APP_REQUIREMENT=/path/to/current-app.whl ./test.sh
# If App 0.2.7 or newer is available from your package index:
SCRIPTMIX_APP_REQUIREMENT='fontlab-fontlabapp>=0.2.7' ./test.sh
```

The wheel is suitable for offline/development testing when pytest and its
requirements are already cached by uv. Tests resolve installed App sources
without importing FontLab/Qt binaries. For source development, optionally set
`SCRIPTMIX_APP_SOURCE=/path/to/app/src/fontlabapp`; the explicit dependency is
still required. Missing helper files fail the run.

Every default run checks all 30 destination hashes, exact menu paths/depth,
Python 3.11 syntax and provenance metadata. It does not audit absent originals.
To additionally check every original source hash, provide the workspace root
containing the manifest's `fontlab-python-examples` paths:

```sh
SCRIPTMIX_APP_REQUIREMENT=/path/to/current-app.whl ./test.sh --original-source-root /path/to/workspace
```

Missing or mismatched originals fail this requested audit. Original hashes and
product script bytes are unchanged.


## Names inspection and selection tools

Names contains Case Pairs, Character Info, Character Set Compare, Glyph Finder
and Select by Mark. Keep counterparts, add mark groups, use language presets,
search names/globs/Unicode and copy characters or missing sets. Character Info
follows selection every 500 ms and paints the current master outline beside
system text; closing stops the timer. No Pause control existed in this original.

These five reuse App's lazy Names panel, table, guarded signals and selection
helpers. Use Fontlabapp 0.2.6 or newer; the `v0.2.6` tag includes
`names_dialog_type`. Supply a wheel built from that tag to the test runner;
package-index availability is separate. For source development, use a current
wheel requirement plus `SCRIPTMIX_APP_SOURCE` pointing at the updated source
directory. Complete
refreshes bind actions to their original font; switched/closed fonts, missing
names and failed refreshes refuse selection before clearing it. No font design
or metadata edits occur. Originals remain untouched and all 25 provenance pairs
are audited. All five pass their original native workflows, complete saved-font/history
invariance and switched/closed selection refusals. Close destroys their native
dialogs; the live specimen fits tall accents and side overhangs. All 25 tools pass
216 native workflow checks together. Clipboard has host-free proof only.

## Read-only Kerning tools

Kerning contains Classes Browser, Compare Masters, Pair List Browser, Missing
Pairs and Text Preview. Browse class members and all-master values, flag missing,
sign-changing or jumping pairs, filter exact sides with `=T`, sort numerically,
and export the actual shown order to UTF-8 CSV through an owned modeless chooser.
Missing Pairs expands characters, names and @classes and retains Copy list.
Text Preview draws actual transformed outlines and advances with native effective
kerning, master/size controls, Kerning and Show values. Oversized proof fits its
complete ink, including accents and overhangs. No font data is written.

Use App 0.2.7 helpers from the tagged source or a built wheel. Package-index
availability is separate. During
source development set both the explicit current wheel requirement and
SCRIPTMIX_APP_SOURCE to the updated App source directory. Tests cover all 30
provenance mappings; prior 25 mappings are unchanged. All original files remain
in the archive. All five pass native workflows, complete saved-font/history invariance, actual
save-dialog export, live proof and Close destruction. All 30 tools together pass
247 native workflow checks.
Exceptions Finder and Pairs From Text remain later complete editing tools.
