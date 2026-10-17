---
this_file: README.md
---

# fontlab-python-scriptmix
Small and useful scripts for FontLab
## Installation and Reports

Copy the contents of `Scripts` into your FontLab Scripts menu folder. Keep the category subfolders, such as `Reports` and `Font Info`; FontLab supports one folder level. Use FontLab 9's Python 3.11 with `fontlab-fly` and `fontlab-fontlabapp` (including `scripting`) available in its Python environment. No third-party UI package is needed.

Open a font, then run Empty Glyphs, Open Contours or Font Overview from Reports. The dialogs are modeless: edit the font and Rescan/Refresh when needed. Empty Glyphs can hide intentional whitespace. Select chosen rows, or leave rows unselected to select all results. Selection refuses results after changing the current font; rescan first. Reports read all masters without changing geometry. Closing a report disconnects its signals. Re-running replaces its old window. Close also destroys the native dialog after its event finishes. All eight reports share this lifecycle code through `fly.ap.scripting`.

Sources stay archived until full reconciliation; `migration.json` records exact Apache-2.0 provenance/hashes and WORK.md retains native acceptance receipts.

A failed scan or table refresh invalidates selection until a complete rescan succeeds. Partial results are cleared; explicit selection calls also refuse them.

## Reports: second migration batch

Live Glyph Info follows the selected glyph twice a second, with per-master metrics, outline/component/anchor counts and Pause. Glyph Table CSV offers all or selected glyphs, sortable widths/counts, Copy CSV and a modeless UTF-8 CSV save chooser. Label Statistics shows mark colours and suffix groups; Add to selection preserves the current selection. Nodes Near Zones checks transformed on-curve nodes across masters with selection scope and a 1–30 unit tolerance. Unicode Coverage includes untouched-block filtering, progress bars and block selection. Explicit selection is bound to the font that supplied the rows.

All five retain the original interactions and pass their original native scenarios, including the live timer and owned Close, on FontLab9.0.9784.

## Font Info tools

The Font Info menu includes Glyph Order Preview and Export, Master Metrics Table, Names and Credits, Unicode Ranges and Codepages, Bump Font Version and Calculate Vertical Metrics. All original controls, embedded Unicode data, assessment notices, export, previews and the metric diagram are retained.

Names changes style on the original current master and credits font-wide. Master Metrics edits every displayed master. Version bump optionally appends a dated note to every master. Vertical Metrics defaults to hhea and Win; Typo is optional because it also moves FontLab's own ascender/descender lines. Its bounds
are captured on open; reopen after outline changes. Glyph Order exports UTF-8
text without reordering the font; Unicode coverage reports without editing it.

Apply uses the last complete preview, refuses closed/switched fonts and changed
source values, validates the entire plan before writes, preserves the active
master and rolls back attempted fields on failure. Failed previews disable Apply.
Names and current-master vertical metrics also refuse a master switch. No-op plans add no history. The shared metadata helper notifies only the package and
its master container. Fontport's existing history protocol may add an extra
no-op Undo checkpoint. All six pass their original native scenarios on FontLab
9.0.9784. All four editors pass one-step Undo, Redo, saved metadata reopening and
complete font-data preservation. Native tests also verify no-op history and
switched-font refusal. Shared panels load lazily through Fontlabapp; each tool
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
# Proof needs App0.2.10 helpers; build the current checkout:
uv build /path/to/app --out-dir /path/to/dist
SCRIPTMIX_APP_REQUIREMENT=/path/to/dist/current-app.whl ./test.sh
```

Cached uv requirements permit offline wheel tests. Sources resolve without native
binaries; development may set `SCRIPTMIX_APP_SOURCE=/path/to/app/src/fontlabapp`
alongside the explicit dependency. Missing helpers fail the run.

Every default run checks all 54 destination hashes, exact menu paths/depth,
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

These five use App0.2.6's lazy panel, tables, signals and selection helpers.
Complete refreshes bind actions to their original font. Switched/closed fonts,
missing names and failed scans refuse selection before clearing it. Native
workflows, full saved-font/history invariance and owned Close pass. The live
specimen fits tall accents/overhangs; clipboard has host-free proof only.

## Read-only Kerning tools

Kerning contains Classes Browser, Compare Masters, Pair List Browser, Missing
Pairs and Text Preview. Browse class members and all-master values, flag missing,
sign-changing or jumping pairs, filter exact sides with `=T`, sort numerically,
and export the actual shown order to UTF-8 CSV through an owned modeless chooser.
Missing Pairs expands characters, names and @classes and retains Copy list.
Text Preview draws actual transformed outlines and advances with native effective
kerning, master/size controls, Kerning and Show values. Oversized proof fits its
complete ink, including accents and overhangs. No font data is written.

These require App0.2.7 helpers. Native workflows, complete saved-font/history
invariance, actual save-dialog export, live proof and Close destruction pass.
Exceptions Finder and Pairs From Text are editing tools described below.

## Kerning editors

Copy Between Masters retains replace/missing/matching modes and checked targets.
Pair Editor edits every master cell, adds either-side partners and deletes with
blank cells; invalid text is ignored while other valid cells remain staged.
Scale Values, Round Values and Remove Small Pairs retain current/all-master scope,
zero options, sorted previews and exact original rounding rules.

These tools require App0.2.8 helpers from a tag/current built wheel or the
source override above; index publication is separate. The writer validates every master,
uses one native history batch, preserves explicit zero/absence and refuses
fractional source history and final values outside +/-2*positive finite UPM.
Apply refuses changed pairs/classes/masters or a
switched/closed font; Refresh recovers failed reads. Close shares owned cleanup.
Allfive pass original native scenarios, complete saved-font deltas, firstUndo/Redo,
reopen, safety andClose (receipts in WORK.md).
The two additional editors need App0.2.9 helpers from that same wheel/source recipe.
Exceptions Finder lists broader class overrides, offers Tick redundant/Untick all
and removes exactly ticked rows. Pairs From Text resolves characters and /name
words into unique adjacent pairs; Set/Add uses displayed effective kerning on
current/all masters, marking explicit glyph values versus inherited class values.
Both pass native controls, full-font Undo/Redo/reopen andClose. All37tools pass
301workflow/99preservation/94safety checks; all37mappings pass. Full archive
migration, cleanup, additional tools/reporters and docs remain open.

## Proof tools (source milestone)

Glyph Grid compares selected glyphs in font order on every master, with one
scale fitted to full outline/component bounds, a zoom slider and Reload selection.
Reload deliberately adopts the current font/selection; zoom stays bound to the
original font. Text By Master preserves per-master advance-only widths, editable
text and size/scroll controls. Waterfall keeps the selected master, ordered sizes
(4–400px), /name tokens and red missing-glyph boxes. Neither text tool adds kerning.
Word Finder retains the exact English/Latin list, case/length/required/allowed
letter filters and Copy words. Native clipboard calls remain excluded by D8.

Proof needs App0.2.10 from that wheel/source recipe; missing helpers fail.
Ordinary refresh/paint/Copy refuses a closed or switched
font and clears incomplete results. Opening native reads start after status/Close
exist; failed initial scans stay empty, diagnosed and closable. Close clears view hooks
and deletes the owned dialog. Native original oracles/painting/Close and exact
font/workspace/history pass; all41core tools pass336workflow/107preservation checks.
Full Issue111 migration, archive cleanup, additional tools/reporters/docs stay open.

## Masters reports

Masters contains Overview, Width Chart, Glyph Weight Chart and Compatibility Check.
Overview shows ordered axis locations/metrics/angles, highlights differences and switches master on double-click.
Width Chart retains12labelled glyph lines; Weight Chart retains10groups, per-master bars/legend and a units² table.
Area uses12-step curves, counter nesting and transformed components; overlaps count twice. Missing widths are absent, missing weight layers0.
Compatibility retains selected/whole-font scope, expandable structural counts, anchor names/component order, auto notices and Select ✗ Glyphs.

Use an App wheel built from the current checkout, or that wheel with its updated source override; earlier wheels lack these helpers.
All four stay bound to their original font. Failed reads stay visibly diagnosed and closable; changed source/master domains or Whole-font membership refuse actions.
Native acceptance on FontLab9.0.9784 passes43original workflows,8complete font/workspace/history checks,
12realpaint controls (axis coverage/six-event settling),24opening faults,43safety and actualClose4/4.
All67exercised source hashes match; fresh chart screenshots confirm the713clipping fix. Font design/history is preserved.
App480/actual-wheel Scriptmix413 and163installed tests each for wheel/sdist pass; all63Appproduction files match.
All45mappings pass; the prior41menu bytes/rows stay exact. Separate chooser8+7checks use fix1 artifacts with unchanged chooser/common source. Same-wheel all41prior tools pass; combined45:379workflows/115preservation/166safety/116error controls/Close45.
No package-index publication is implied. Full Issue111/archive cleanup and held7Names editors stay separate; original sources remain retained.

Metrics and outline inspectors: Spacing String Preview, Width Table, Contour Order View and Node Statistics retain complete controls, raw winding/counts, actual outlines/advances, all masters and exact flagged selection; lazy `inspectors_api()`/dialog/views share lifecycle, snapshots and painter containment.
Installed-wheel FontLab 9.0.9784 acceptance passes41 original workflows/8 complete saved font/design/classes/metadata/workspace/history/master checks/10 paint/24 opening/59 safety/Close 4;70 source hashes match and imports restore; Node has its exact fresh post-seed baseline. Seven images were inspected; all 15 final images are byte-identical to retained v1.
App 497 source and actual-wheel Scriptmix 501 passed, 1 skipped;180 installed tests each for wheel/sdist pass on arm64Python3.11.14. All 66 production files and49 mappings match; previous 45 menus/rows stay exact and72 wheel/116 sdist entries pass license/NOTICE/privacy audits.
Same-wheel prior 45regression passes379 workflow/115 preservation/166 safety/116 error controls/Close 45,113 source hashes and import restoration; combined 49 native:420/123/225/150/Close 49. Historical 15 chooser receipts use unchanged code; no fresh chooser run is claimed. Use an App wheel built from the current checkout; `SCRIPTMIX_PYTHON=cpython-3.11-macos-aarch64-none ./test.sh` selects the host architecture. Full 130-stem/archive/held 7 Names work stays open; no original removal or index publication.

## Read-only Components (native acceptance)

Compatibility compares ordered component lists across masters and selects mismatches.
Count Badges draws placed outlines with own contour/component/auto counts per master.
Missing Bases groups missing glyphs/layers and unnamed bases; its simulated scan is retained.
Report preserves every composite layer, offsets, current/all-master filtering and Copy CSV.
Where Used indexes all masters in font order, with search, row selection and Select all.
Use a current App wheel with lazy components helpers; actions reject changed source/font/master/membership and Close releases signals/paths.
FontLab9.0.9784 passes33original workflows/10complete font/workspace/history checks,5paint/30opening/80stale/16painter/6selection controls/Close5;81hashes and restored imports match. Eight images were inspected; valid falsey-current A retains its badge fallback.
App506source tests, actual-wheel Scriptmix620/1skip, Git-free619/2skips and189installed tests each for wheel/sdist pass;69runtime files and54source pairs match, prior49menus/rows exact. License/NOTICE/privacy audits pass75/120payload entries; clipboard tests use a fake only.
Same-wheel prior49passes420workflow/123preservation/225safety/150error controls/Close49; combined54native:453/133/305/201plus6selection/Close54. Historical chooser receipts remain separate.
Reviewed Appv0.2.13/Scriptmixv1.0.9 releases pass independent downloaded-tag/native acceptance;54/130released,76pending(held7Names+69other stems). All originals remain; full migration/archive cleanup/additional tools/reporters/docs stay open.
