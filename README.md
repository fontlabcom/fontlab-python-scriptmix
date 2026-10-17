---
this_file: README.md
---

# fontlab-python-scriptmix
Small and useful scripts for FontLab

## Installation and Reports

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
no-op Undo checkpoint. Native scenarios, one-step Undo/Redo, saved metadata reopening, complete
font preservation, no-op history and switched-font refusal pass on9784. Shared panels load lazily through Fontlabapp; each tool
keeps its own controls and actions. Glyph Order uses an owned modeless save
chooser and reports the exported count and filename.

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

Native scenarios/Close and builder feature-only deltas/Undo/Redo/reopen pass.
Clipboard operations remain host-free tested; native checks inspect the actual
suffix preview under the owner's clipboard exclusion.

## Host-free distribution checks

Run with Python 3.11 through uv and an explicit current App requirement:
```sh
SCRIPTMIX_APP_REQUIREMENT=/path/to/current-app.whl ./test.sh
# Names editors need forthcoming App0.2.11; build the updated checkout:
uv build /path/to/app --out-dir /path/to/dist
SCRIPTMIX_APP_REQUIREMENT=/path/to/dist/current-app.whl ./test.sh
```

Offline tests require uv-cached pytest/dependencies. Tests resolve App sources
without importing FontLab/Qt binaries. For source development, optionally set
`SCRIPTMIX_APP_SOURCE=/path/to/app/src/fontlabapp`; the explicit dependency is
still required. Missing helper files fail the run.

Every default run checks all 48 destination hashes, exact menu paths/depth,
Python 3.11 syntax and provenance metadata. It does not audit absent originals.
To additionally check every original source hash, provide the workspace root
containing the manifest's `fontlab-python-examples` paths:

```sh
SCRIPTMIX_APP_REQUIREMENT=/path/to/current-app.whl ./test.sh --original-source-root /path/to/workspace
```

Missing or mismatched originals fail this requested audit. Original hashes and
product script bytes are unchanged.

## Names inspection and selection

Names contains Case Pairs, Character Info, Character Set Compare, Glyph Finder
and Select by Mark. Keep counterparts, add mark groups, use language presets,
search names/globs/Unicode and copy characters or missing sets. Character Info
follows selection every 500 ms and paints the current master outline beside
system text; closing stops the timer. No Pause control existed in this original.

These five require App0.2.6. Complete refreshes bind actions to their original
font; switched/closed fonts, missing names and failed scans refuse selection.
Native workflows, full font/history invariance and Close pass. The specimen fits
tall accents/overhangs; clipboard has host-free proof only.

## Read-only Kerning tools

Kerning contains Classes Browser, Compare Masters, Pair List Browser, Missing
Pairs and Text Preview. Browse class members and all-master values, flag missing,
sign-changing or jumping pairs, filter exact sides with `=T`, sort numerically,
and export the actual shown order to UTF-8 CSV through an owned modeless chooser.
Missing Pairs expands characters, names and @classes and retains Copy list.
Text Preview draws actual transformed outlines and advances with native effective
kerning, master/size controls, Kerning and Show values. Oversized proof fits its
complete ink, including accents and overhangs. No font data is written.

These need App0.2.7; native workflows, font/history invariance, CSV export, proof
and Close pass. Exceptions Finder and Pairs From Text edit kerning below.

## Kerning editors

Copy Between Masters retains replace/missing/matching modes and checked targets.
Pair Editor edits every master cell, adds either-side partners and deletes with
blank cells; invalid text is ignored while other valid cells remain staged.
Scale Values, Round Values and Remove Small Pairs retain current/all-master scope,
zero options, sorted previews and exact original rounding rules.

These tools require App0.2.8 helpers; use an updated tag-built wheel
or an explicit current wheel plus the source override above. No package-index
publication is implied. The shared writer validates every master before writes,
uses one native history batch, preserves explicit zero/absence and refuses
fractional source history and final values outside +/-2*positive finite UPM.
Apply refuses changed pairs/classes/masters or a
switched/closed font; Refresh recovers failed reads. Close shares owned cleanup.
Native scenarios, saved-font deltas, firstUndo/Redo, reopen, safety andClose pass.
The two additional editors need App0.2.9 helpers (tag-built wheel or
explicit current wheel plus updated source override); index availability is separate.
Exceptions Finder lists broader class overrides, offers Tick redundant/Untick all
and removes exactly ticked rows. Pairs From Text resolves characters and /name
words into unique adjacent pairs; Set/Add uses displayed effective kerning on
current/all masters, marking explicit glyph values versus inherited class values.
Both pass native controls, full-font Undo/Redo/reopen andClose.

## Proof tools (source milestone)

Glyph Grid compares selected glyphs in font order on every master, with one
scale fitted to full outline/component bounds, a zoom slider and Reload selection.
Reload deliberately adopts the current font/selection; zoom stays bound to the
original font. Text By Master preserves per-master advance-only widths, editable
text and size/scroll controls. Waterfall keeps the selected master, ordered sizes
(4–400px), /name tokens and red missing-glyph boxes. Neither text tool adds kerning.
Word Finder retains the exact English/Latin list, case/length/required/allowed
letter filters and Copy words. Native clipboard calls remain excluded by D8.

Proof needs App0.2.10: use a wheel built from the current checkout,
or the explicit wheel plus `SCRIPTMIX_APP_SOURCE` development recipe above.
Helper detection rejects earlier wheels without those sources; no registry
publication is claimed. Ordinary refresh/paint/Copy refuses a closed or switched
font and clears incomplete results. Opening native reads start after status/Close
exist; failed initial scans stay empty, diagnosed and closable. Close clears view hooks
and deletes the owned dialog. Native original oracles/painting/Close and exact
font/workspace/history pass; all41core tools pass336workflow/107preservation checks.

## Names editors (source milestone)

Batch Rename retains plain/regex replacement and all/selected scopes. Suffix Tool
keeps add/remove/replace presets, numbered names and optional encoding removal.
Both refuse collisions and auto-layer glyphs/bases; components follow native
rename, while kerning/features retain old names. Duplicate Unicodes keeps primary
keepers and manual removal ticks. Unicode From Names retains AGL/derived aliases,
overwrite and Show unchanged. Glyph Notes browses/edits complete notes; Glyph Tags
keeps completion, counts and ticked removal. The palette's None swatch clears marks.

These seven need forthcoming App0.2.11 helpers: use an updated built wheel or the
explicit stable wheel plus updated `SCRIPTMIX_APP_SOURCE` recipe above. Full-batch
preflight skips no-ops, refuses changed displayed source and reports partial or
post-write failures with Undo guidance. Only original Reload/Rescan actions rebind.
Opening failures leave empty diagnosed Close/status UI. Native artifacts/oracles,
full-font firstUndo/Redo/reopen and Close remain pending. Previous41menus/mappings
stay unchanged; all48 source mappings retain Apache provenance.
Full130stems/other collections/archive cleanup/additional tools/reporters/docs stay open.
