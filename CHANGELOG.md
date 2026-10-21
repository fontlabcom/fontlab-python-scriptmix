---
this_file: CHANGELOG.md
---

## Unreleased — 2026-10-21 — Metrics, Names, Anchors and Masters editors

Add 27 tools, 22 of them non-modal panels; the active menu grows from 123 to 150
(81 additional tools). All are source candidates with offline tests; native
FontLab acceptance is pending for every one.

- Metrics: Italic Sidebearings, Round Advances, Centre In Advance, Zero-Width
  Marks, Tabular Width and Scale Advances, adapted from the author's own
  samples. Preview panels; Apply plans again from the live font; outlines move
  in place; Scale Advances gives the odd unit to the right sidebearing.
- Names: Glyph Tags, Mark Color Palette, Suffix Tool, Batch Rename, Batch Glyph
  Notes, Glyph Notes and Unicode From Names, adapted from the author's own
  samples. Every write rescans the font, never reads the fgGlyph getter and
  reads each value back.
- Anchors: Rename Bulk, Center Horizontally, Place From Bounds, Snap To Metrics,
  Round To Grid, Delete By Name and Mirror Across Masters, adapted from the
  author's own samples. Origin moves and duplicate names are refused; new pins
  get the name-derived appearance.
- Masters: Display Next Layer, Display Previous Layer, Duplicate Current Layer,
  Use Layer As Master, Transform Background, Selection To All Backgrounds and
  Select Different Colour, independent rewrites after Pedro Arilla's Glyphs
  scripts (Apache-2.0). Transform Background and Selection To All Backgrounds
  are panels; the other five run once from the menu.
- Shared rules: one Undo step per font edit, auto layers never notified, bases
  of auto layers refused where the operation could re-resolve them, and no
  UpdateAll call (fl#8537). The Names, Anchors and Masters writers also refuse
  while native glyph updates are pending.
- Tracking: 27 rows in additional-tools.json, four NOTICE sections, 20 rows in
  PORTING-BACKLOG.md marked as source candidates, and generated catalogue pages.

## Unreleased — Categories to XML Lib Key candidate

Add Simon Cozens' complete ordered Mark/base UFO lib fragment workflow using
the existing Glyport category policy through Fly and a shared read-only App
snapshot panel. Escape XML glyph names; reject observed source changes and
incomplete captures. Source/artifact controls are tracked separately from pending
native preservation, lifecycle and release acceptance.

## Unreleased — complete Italic Angle candidate

Add Masters > Italic Angle through the shared App editor. Retain ordered master
spins, original ranges/precision, staged gauge, pending counts and helper/class
interfaces. The candidate manifest has69rows; the preceding68rows and70existing
menu payloads remain unchanged. Released scope remains68/130 until final gates.
Known unsafe native blueScale history refuses changing batches before writes
(fl#8531); no-op batches and the original safe multi-master workflow remain.

## v1.0.18 — 2026-10-18 — two additional foreground reporters

Add Sidebearing Direction Marker and Duplicate Anchor Rings, requiring
fontlab-fontlabapp0.2.23 or newer. Retain the original68migration rows; the two
additional tools have separate provenance/native evidence and do not change
the130sample denominator. Downloaded-tag verification follows this release.

## Unreleased: additional foreground reporter candidates

- Add Sidebearing Direction Marker and Duplicate Anchor Rings through App's
  shared owned lifecycle. Retain explicit direction/handle and foreground scope.
- Track their exact provenance/native evidence separately from68/130sample
  migrations. Full775tests/1historicalskip and two-menu100%coverage pass.
- The prior68 regression passes after the shared App date correction:552original
  checks,196preservation/history and Close68, with extended safety/fault controls.
  Release/downloaded-tag verification remains pending;68/130 stays unchanged.

# Changelog

## .141 reviewed-source integration candidate

Combine complete typed Symmetry/Cutoff with the current numeric workflows and
the basic Character Map initial viewport. Preserve every prior runtime/menu and
all original filters, pair order, type identities and existing native holds.
Source/artifact evidence does not qualify native/font-history behavior.

## Unreleased — selection context test fixtures

- Model the verified regular Font-window ancestry in the two shared host-free
  fixtures. Exercise actual App selection refusal with an active Glyph window.
- Keep all68Scriptmix menus, runtime modules and migration records byte-exact.

## v1.0.17 — 2026-10-18 — anchor-copy refusal layout

- Fit the owned dialog when a refusal explanation appears; keep a short footer
  status. The anchor preview, explanation and Close controls remain separated.
- Retain the preceding tags unchanged: their numerical acceptance passed, but
  the visual gate rejected overlapping refusal text before canonical promotion.
  New native geometry checks and independent fresh-tag acceptance are required.

## v1.0.16 — 2026-10-18 — Copy Anchors From Glyph

- Retain full L1 source completion, merge/replace, width scaling and master scope.
  Preconstruct native values, preserve existing pins and stabilize new appearance.
  Bind raw coordinates, widths, expressions, selection and every option.
- Refuse automatic dependants before mutation (fl#8512), and existing-anchor
  origin moves that native Redo cannot restore (fl#8527). Keep original previews.
  Installed candidate passes11original/7complete persistence/130native controls
  and Close. Prior67 regression, App597, Scriptmix770+1skip and280installed
  tests per wheel/sdist pass. Downloaded-tag R053 follows release.

## v1.0.13 — 2026-10-18 — compact Master Switcher

- Add original ordered master/location buttons, exclusive current emphasis and
  first9shortcuts on the guarded owned Masters shell. Preserve all60released tools.
  Native original5/preservation2/additional43 pass on3/25masters, including
  actual key events and lifecycle/fault controls. Prior60same-runtime regression
  passes. Source and candidate acceptance reviewed; fresh-tag acceptance follows release.
  Preserve package-master semantics; no editor-layer switching claim.

## v1.0.12 — 2026-10-18 — live Node Coordinates

- Port complete selected-node coordinate/pair tables,400ms polling and Copy.
  Follow active glyph/master edits with guarded font binding and owned cleanup.
  Accept490combined native workflows/145preservation checks andClose60; retain24new timer/Copy/fault/font-boundary controls. Independent downloaded-tag R053 pending.

## v1.0.11 — 2026-10-18 — read-only glyph reviews

- Fix original native feature iteration: use fgOTLayout.keys() tags, not its
  sequence code values; eliminate392false candidates and retain exact395Rafi
  list/selection. New native-shaped tests and unchanged original oracle pass.
- Accept combined59native:483workflow/143preservation/407safety/294error plus
  22selection/layout andClose59; retain all originals and the full130scope.

- Add complete Select Unreferenced Glyphs and Interpolation Preview source tools.
  Preserve candidate/reference rules, all controls and full interpolation painting.
- Reuse guarded lifecycle, source snapshots and safe painters; retain previous57
  menus/rows exactly. Source/artifact/native/prior57 pass; release/R053 pending.

## v1.0.10 — 2026-10-18 — read-only Anchors

- Add complete Anchor Cloud, Anchor Compatibility and Mark Attachment Preview
  source tools with shared raw anchor snapshots and existing owned lifecycle/
  geometry/painter boundaries. Preserve original controls and all54prior mappings.
- Reject stale data without rejecting intended selector changes; retain exact
  None paint diagnostics, explicit current-glyph fallback and complete cleanup.
  Source/artifact/native/prior54 gates pass; integration/release/R053 pending.
- Fix late-binding tree columns after native image review: expose every master
  and missing-anchor cell, with source and native width/count regression checks.
- Accept combined57 native:473workflow/139preservation/368safety/261error plus
  16selection/layout andClose57. Preserve previous54menus and all original inputs.
- Correct the carried Components NOTICE status to its verified release receipts.

## v1.0.9 — 2026-10-18 — read-only Components

- Accept all five installed-wheel native workflows and prior49regression: combined54
  passes453workflow/133preservation/305safety/201error controls,6selection andClose54.
  Fix falsey-current fallback, retain exact empty Compatibility scope and safe painters.
  Source/artifact/privacy checks pass; downloaded-tag R053 is recorded separately.

- Fix the measured CountBadges empty-selection fallback for a valid falsey native
  CurrentGlyph. Resolve selected/current names with original is-not-None rules;
  keep Compatibility's exact selection and prior Proof/scripting helpers unchanged.
  Source proof: App506, Scriptmix620/1skip, Git-free619/2skips; fix2artifact/native
  confirmation remains parent-owned and pending.

- Fix source-review F1: Compatibility's selected scope keeps empty selection;
  CountBadges alone retains its original current-glyph fallback.
- Fix source-review F2: reuse ProofView painter activation/finalization containment,
  exact None success and explicit owned fallback cleanup/Close release. Source-only
  regression proof: App505, Scriptmix618/1skip, Git-free617/2skips; native/artifact
  re-review remains pending. Prior49menus and mappings stay exact.

- Add five complete L1 component inspectors, preserving original UI, ordering,
  selection, simulation, pure CSV oracle and complete native badge drawings.
- Share lazy calculations and existing owned Proof/Names lifecycle; guard exact
  font/master/membership/source drift, opening/paint errors and Close cleanup.
- Append five mappings (54 total) and immutable Git-free prior49 provenance/menu
  byte checks; preserve the prior45 invariant and all original sources.
- Source tests only; independent review, artifacts, native preservation/painting/
  safety/Close and prior49 regression remain pending. No release is claimed.

## v1.0.8 — 2026-10-18

- Fix the prior-45-menu invariant test after commit and in Git-free downloads.
  It now checks a literal canonical digest of immutable v1.0.6 provenance,
  all 49 current rows and the 45 released menu hashes without calling Git.
- Add rejection tests for changed source/destination provenance and menu bytes.
  Explicit arm64 Python 3.11 checks pass: source 504 tests/1 skip and a separate
  Git-free standalone copy 503 tests/2 skips, both against the stable App v0.2.12 wheel.
  No runtime helper, menu, migration or dependency changes. Keep v1.0.7 intact;
  the corrected standalone test distribution requires a new release tag.


## v1.0.7 — 2026-10-18

- Add complete Spacing String Preview, Width Table, Contour Order View and Node
  Statistics with original controls, defaults, class/key/helper interfaces and
  exact native scenario data. No original source is changed or removed.
- Reuse lazy App helpers, existing Proof/Names/Masters lifecycle, actual transformed
  outlines, raw node-polygon winding and contour/node counts. Preserve zero,
  missing and auto values and numeric width sorting.
- Guard initial scans, exact source/current-master/ordered-master domain and
  Whole-font membership. Failed reads/paints clear results and handles, retain
  Close and diagnosis, drain repaint queues and allow explicit same-font recovery.
- Append four provenance pairs (49 total); previous 45 menus/rows remain exact.
  Source/fix review, installed-wheel native acceptance and artifact audits pass:
  41 original workflows,8 complete preservation,10 paint,24 opening,59 safety,
  actualClose 4;70 source hashes and imports match. Node uses its fresh post-seed baseline.
- App 497/actual-wheel Scriptmix 501 passed, 1 skipped and180 installed tests each for wheel/sdist
  pass;66 production files,72 wheel/116 sdist entries and license/NOTICE/privacy match.
- Same-wheel45 prior-tool regression passes379 workflow/115 preservation/166 safety/
  116 error controls/Close 45,113hashes and import restoration. Combined 49 native:
  420 workflow/123 preservation/225 safety/150 error controls/Close 49. Historical 15 chooser
  receipts are retained; no new chooser run occurred. Full 130/archive/held 7 Names stay open.


## v1.0.6 — 2026-10-17

Fix2: native screenshot inspection exposed an inherited tick endpoint defect.
Shared nice_ticks now covers the native plotted range, including max713,
while preserving nice steps and bounded generation. Complete original chart
commands have axis-bounds regressions. Scoped source review and native screenshots pass.

Fix1: refresh scans the actual ordered master domain and refuses mid-scan changes;
Whole-font actions recheck complete ordered glyph membership; repeated failed
chart invalidation schedules at most one clear repaint. New regressions retain
explicit refresh recovery and captured Selected scope. README frontmatter fixed.
Independent fix review and the four-tool native/artifact gates pass.

- Add complete Overview, Width Chart, Glyph Weight Chart and Compatibility Check,
  retaining original controls/defaults/keys/classes, labelled lines and bars,
  structural tree, master-axis order, limits and native DRIVE interfaces.
- Share original twelve-step transformed contour areas/counter nesting, missing
  width/weight semantics and own-contour signatures through lazy App helpers.
  Reuse existing owned panel/signal registry/paint containment, with visible
  initial-read failures, exact source/master action guards and native-handle cleanup.
- Bound tick generation for equal huge ranges so tiny floating increments cannot
  loop forever; normal original chart ticks and numerical meaning remain.
- Keep all41previous menu bytes and provenance rows exact, append four new pairs,
  retain originals/dependencies and consolidate README within200lines.

Installed-artifact acceptance on FontLab9.0.9784 passes43original workflows,
8complete font/workspace/history checks,12real paint controls (axis coverage and
six-event settling),24opening faults,43safety and actualClose4/4. Fresh charts
confirm the clipping fix;67exercised hashes match. App480,actual-wheel Scriptmix413,
163installed wheel/163sdist tests and63production-file parity pass. All45mappings
pass with prior41rows/menu bytes exact. Separate chooser8+7checks use fix1
artifacts with unchanged chooser/common source. Same-fix2-wheel regression of
all41prior tools passes336workflows/107preservation/123safety/80error controls/Close41;
106source hashes verify and imports restore. Combined45:379workflows/115preservation/
166safety/116error controls/Close45.
Full Issue111/archive cleanup and held7Names editors remain separate.

## v1.0.5 — 2026-10-17

Native installed acceptance: all41core tools pass336workflow/107preservation,
123safety,80writer/error controls andClose41; separate15chooser checks pass.
All41hash mappings and60Appsource bytes pass. Full archive migration staysactive.

- Retain complete Glyph Grid, Text By Master, Waterfall and Word Finder tools,
  sharing real transformed paths, exact advance-only runs, original word data,
  filters and guarded owned UI through lazy App0.2.10 helpers.
- Fit Grid's common scale to wide overhangs and tall accents/components; preserve
  deliberate Reload font/selection adoption and refuse automatic stale refresh.
- Clear failed previews, contain painter/callback/finalization errors and retain
  original controls/keys/scenario globals. Copy has host-free coverage; native
  clipboard remains excluded. Installed native/artifact acceptance passes.

### Task3j fix1 — contain all opening font reads

- Build empty controls/status/Close before binding/id/selection/maps/characters/
  master reads; diagnose early failures in a closable invalid panel.
- Retry initial loads through existing guarded controls without adopting a
  different known font. Preserve explicit Grid Reload adoption and Waterfall's
  initial active-master choice with signal state restored in finally.
- Add23actual constructor/recovery/failed-state Close/stale-binding regressions;
  independent source review and installed native/artifact reacceptance pass.

## v1.0.4 — 2026-10-17

Review fix: retain a completed batch's applied outcome, original cause and
Undo/Refresh guidance across all later display/preview failures. Preflight and
partial-write diagnostics stay distinct. Both selected editors reuse the shared
preview-table builder while retaining exact headers and checkbox callbacks.

Add complete Exceptions Finder and Pairs From Text menu workflows. Share original
class precedence, word parsing, explicit/effective previews and ticked plans in
lazy App0.2.9 helpers. Reuse complete snapshot-bound preflight/history writing,
including zero/absence and native save/reopen range refusal; retain all controls,
manual checkboxes, Refresh and owned Close. Failed reads clear pair/value previews.
Append two exact provenance mappings without changing prior35. Host-free tests
pass; all37native tools pass301workflow/99preservation checks,94safety,32writer
and12postwrite controls,15chooser checks andClose37. Full archive migration
and cleanup remain active.

## v1.0.3 — 2026-10-17

Refuse changing batches whose final pairs on any master exceed twice the font's
positive finite units per em: FontLab's load pipeline otherwise clamps them and
adds a mark. Signed32/history validation remains; no values are silently clamped.
Valid corrections/deletions of existing extremes work; true no-op stays untouched.

Add Copy Between Masters, Pair Editor, Scale Values, Round Values and Remove
Small Pairs through shared lazy App plans, snapshots and native batch writing.
Preflight all masters/classes/glyphs and whole-unit history before any mutation;
retain explicit zero, unrelated pairs and active master. Failed reads/stale
previews disable Apply and offer Refresh. Invalid cell text never enters the
staged map; other valid edits remain. All35tools pass280native workflows,85
preservation/history checks,82safety checks,32writer controls,7actual-export
checks andClose35/35. Archived sources stay unchanged; full issue111 stays open.


## v1.0.2 — 2026-10-17

Add Classes Browser, Compare Masters, Pair List Browser, Missing Pairs and Text
Preview under Kerning. Require App0.2.7 helpers. All30tools pass247native workflows,
50preservation/history,52safety,7actual-save-dialog checks and nativeClose.
Host-free171tests and30provenance pairs pass. Remaining editors/archive migration,
new tools/reporters and final cleanup remain open; original inputs stay retained.


## v1.0.1 — 2026-10-17

Add Case Pairs, Character Info, Character Set Compare, Glyph Finder and Select by
Mark. The live outline specimen fits tall accents and side overhangs. Require
App 0.2.6 helpers; tests accept an explicit tag-built wheel without assuming index
publication. All 25 tools pass 216 native workflows, 40 preservation/history checks,
44 safety checks and native Close destruction. Host-free tests: 151 passed.
The full archive migration, new scripts/reporters and final cleanup remain open.


## Unreleased — Names inspection tools

- Share lazy Names panel/table/lifecycle and complete-refresh selection guards.
- Preserve five original tools, Unicode/language data, live outline proof,
  copy, keyboard and row actions; keep/add selection validates all names first.
- Retain all source originals; native verification of this batch is pending.


## v1.0.0 — 2026-10-17

First 20 practical tools: eight Reports, six Font Info panels and six Features
panels. Install current Fontlabapp helpers and fly in FontLab 9's Python 3.11.
The five editors pass complete preservation, Undo/Redo and saved-font reopening.
All 20 tools pass 183 native workflow checks and native Close destruction.
Host-free tests are portable: 113 pass from an isolated archive with the actual
App v0.2.5 wheel; original-source auditing is explicit and fails closed.
This release is a verified migration milestone. The remaining archive migration,
additional tools/reporters and workspace-wide cleanup are still in progress.


## Unreleased

- Five more complete Reports tools pass original native scenarios on9784:
  Live Glyph Info, Glyph Table CSV, Label Statistics, Nodes Near Zones and
  Unicode Coverage.42independent checks, screenshots and cleanup pass; full
  Python3.11 test suite47passes. Source provenance remains recorded.

- Migrate Empty Glyphs, Open Contours and Font Overview with original tables,
  filters, multi-master calculations and persistent modeless lifecycle.
- Clear stale display data on no-font refresh and bind selection to scanned id.
- Record source hashes/license and add host-free behavior tests.

## Issue 111 review round 1

Fixed failed-refresh selection: invalidate the prior snapshot before native
access, scan into local rows, populate the full table, then publish rows/id. Any
scan or display exception clears partial table data, keeps selection disabled,
and rejects direct select_rows calls. Four regression cases first failed against
the old code (genuine RED retained), then passed after this fix.

Controller native acceptance: all three reports pass their original scenarios
on FontLab9.0.9784 through the installed helper wheel, with26independent checks,
reviewed screenshots and complete owned font/dialog cleanup.11host-free tests
pass on Python3.11. This is the first issue111 batch; broader work remains open.

## Issue 111 second Reports batch

- Migrate Live Glyph Info, Glyph Table CSV, Label Statistics, Nodes Near Zones
  and Unicode Coverage with original UI, scans, scope, timer and CSV behavior.
- Invalidate snapshots before host access and publish only after full display;
  reject selection after a font switch or failed refresh. Preserve Add selection.
- Retain originals and record hashes/provenance; add owned-data behavior tests.
- Native acceptance remains pending for these five scripts.


## Issue 111 task 2b — shared script dialog lifecycle (2026-10-17)

Shared `fontlabapp.scripting` helpers handle guarded Python callbacks,
identity-checked registry removal, explicit native close handling and deferred
widget deletion. All eight Reports use them through `fly.ap.scripting`; CSV
passes its owned chooser and Live Glyph Info its timer. No new dependencies.

Controller acceptance passed on FontLab 9.0.9784 using the installed wheel:
all eight original scenarios, 68 independent checks, and actual Close-button
native destruction for every dialog. Registry cleanup and host import-state
restoration pass. The old immutable source released its registry entry but
remained native-live while a wrapper was retained; the new source destroys it.
App 315 tests, Scriptmix 55 tests and 11 installed-helper tests pass; all 47
production files match wheel bytes. Evidence: workspace ecosystem evidence,
`issue111-lifecycle-v1/summary.json`. No owner site-packages install or new tag.


## Issue 111 task 3c — complete Font Info sources (2026-10-17)

Migrated all six Font Info tools with full original UI/data and mutation paths.
Preserved original KEY/registry interfaces and all eight existing Reports sources.
Applied shared fly aliases/current-package access, guarded slots and deterministic
close/destruction. Full previews bind Apply to the original package, retain the
actual edit plan, refuse stale old fields and invalidate after failed previews.
Names/current-scope metrics bind their master. No glyph/layer notifications.

API review: Fontport NativeFontBackend.set_info_many and its info-backend tests
provide the measured checkInitHistoryState(0) + [package, mastersContainer()]
history protocol, but not an explicit multi-master plan or rollback. App fontui
FontInfoEditor stages through Fontport and eagerly imports PythonQt, so it is not
a reusable script-core editing API. Added a bounded shared write_font_info helper
only in the App worktree, without dependencies. No-op plans produce no history;
whole plans validate first; native old values are retained for exact rollback.

Tests-first RED: Scriptmix initial test_font_info.py exited1 (14 failures; six
requested-tool existence assertions). App initial direct import errored during
collection; corrected explicit module import then two genuine missing-helper
assertions failed (exit1). App regression for normalized-empty rollback failed
against implemented code (None became empty text); fixed by retaining actual
native preflight values. Three native-boundary regressions then failed for huge
integers/null/surrogate text; bounded numeric comparison and Unicode validation
fixes pass. Rollback-failure fixture initially expected failure from a no-op
setter; corrected to apply a changing field whose restore setter raises.

Focused GREEN: Scriptmix21tests and App7tests pass. Full Scriptmix76tests pass.
Exact commands/final source hashes are in the workspace task-3c-report.md.
Native runs, Undo/Redo, chooser interaction and full saved/reopened metadata
proof are pending the controller; no native calls/commits/package installs made.


## Issue 111 task 3c review round 1 — shared Font Info shell

Extracted the repeated six-tool layout, palette/heading/status/footer, guarded
callbacks, failed-preview invalidation, current-font/master checks, preview guard,
table rendering and default close into App's private FontInfoDialog. The public
`fly.ap.scripting.font_info_dialog_type()` loads it only when a tool runs; importing
scripting remains host-free. Per-tool controls, preview calculations, plans,
master-bound choice and mutation actions stay in Scriptmix. The glyph-order
modeless chooser, single callback/reuse and owned-child close cleanup are retained.

This shell adapts Apache-2.0 sample code. Its SPDX/provenance is retained in the
new source and NOTICE, with LICENSE-APACHE-2.0 and combined distribution license
metadata preserving the existing BSD-3-Clause/MIT terms. No dependencies added.

Tests-first: six Scriptmix AST assertions failed against copied safety methods
(exit1;22prior tests passed); App factory assertion failed before implementation
(exit1;three related fixture assertions also failed). The Apache-metadata test
then failed before metadata/provenance changes (exit1;fourpanel tests passed).
App tests exercise the actual shared constructor styling/layout/control wiring,
callback argument handling, safety/master checks, numeric table alignment,
missing-font/failed-setup disabling and separate-process lazy host-free import.
Scriptmix imports the actual shared base against owned native/Qt doubles and
retains all calculation/mutation/chooser tests.

Full Scriptmix tests:83passed0.11s,exit0. Full App/scoped Ruff/hash receipts and
updated production freeze are recorded in the workspace task-3c-report.md.
Native acceptance of the refactored bytes remains controller-owned; prior v4
native receipts belong to the preceding production hashes. No native runs,
installs, commits or edits to Reports/canonical App occurred in this round.


## Controller acceptance: six Font Info tools

Task review and two scoped fixes pass: shared App panel extraction and concise
export status. Fresh Scriptmix83tests, App328tests, installed shared-helper24tests,
48wheel/source matches and14manifest pairs pass. Native installed-wheel results:
all14original workflows153checks; four mutators24metadata/preservation/one-Undo/
Redo/reopen checks;12no-op/preflight/stale-font checks;8actual chooser exports;
Close destroys14/14native dialogs and releases registry. Paths/module identities
restore; owned fonts close. Raw workspace UUID/title changes are independently
predicted without normalizing any font-design data.

Final Glyph Order-only status fix passed original15checks,chooser8checks and
Close again; screenshot confirms count/filename fits. Earlier all14tool bytes
except that status line remain unchanged. Source/native evidence is retained in
workspace issue111-font-info-shared-v3 and issue111-font-info-footer-v1. App
0f3f896 is reviewed and integrated into its canonical branch. Source archives
remain intact; full issue111 migration, cleanup, additional tools/reporters and
documentation/final review are still pending. No release tag or owner-site
install was performed.

## Unreleased — six Features tools

Migrate the six complete feature tools with original controls and Apache-2.0
provenance. Reuse the App panel lifecycle and Fontport's ordered feature writer
for actual suffix appends. Bind Apply to the complete source snapshot and glyph
references; preserve unrelated source/order/prefix/classes, reject stale plans
and contain proof painter errors. Native acceptance remains pending.

Task3d review fixes: share host-free suffix/FEA calculations, document concrete
row contracts, and load the Feature Code Viewer from exact ordered VFJ source
instead of native index iteration/synthesized prefix. Native rerun pending.


## Controller acceptance: six Features tools

Initial task review required shared pure calculations and useful typing/docs.
Native v1 additionally exposed blank feature bodies in the viewer. Fix1 review
passes: host-free App feature_code calculations are shared through fly; viewer
uses exact persisted prefix/ordered sources rather than raw native iteration.
Genuine regressions and fixes are retained in workspace task-3d-report.md.

Fresh Python3.11 source347App13.02s/110Scriptmix tests pass; installed helper,
shared panel/writer and calculation tests43pass;50production files match wheel.
20provenance source/destination pairs match. Wheel56entries and sdist94entries
retain shared sources, licenses and NOTICE; ignored scratch/venv/archive payload
is excluded. Fontport v1.0.2 source confirms the required ordered API exists.

Native installed-wheel six-tool v2 passes30workflow checks,6Close destructions,
and Build's six full feature-only/preservation/one-Undo/Redo/reopen checks.
All20tool v2 additionally passes183workflow checks,30persistence checks across
five editors,12no-op/preflight/stale-font safety checks andClose20/20. Actual
App/Fontport source paths are asserted; App/fly/Fontport imports restore. Every
owned font closes and no host crash occurs. Screenshots of all six reviewed:
real alternate outlines, complete scrollable tables/source, working highlights.

Evidence: workspace issue111-features-v2 and issue111-tools20-v2. Suffix clipboard
scenario is explicitly adapted to actual preview under D8; clipboard remains
native-unverified. All20-v1 reached20workflow/5editor-persistence passes then a
cold native chooser hit FontLab's5sRPC deadline. This unchanged chooser already
passes independently on the same Scriptmix source hash (footer-v1); all20-v2
tests lifecycle/safety separately. Failure receipts retained; no performance
claim or speculative source fix. Feature-source mutation does not compile or
prove shaping: test generated code in FontLab's Features panel.

Full issue111 archive migration/cleanup, further practical and broader scripts,
package cleanup, new reporters and docs/finalreview remain open. No original
source removed, owner environment install, publication or release tag.

## Issue 111: portable host-free checks

Resolve actual App helper sources from an explicit installed dependency or source
override. Distribution checks always cover 20 scripts; original-source hashes
are an explicit fail-closed workspace audit. Document wheel-based uv testing.

## Issue 111 Names review fix 1

Fit complete Character Info outlines including tall accents and side overhangs
inside the padded proof area while keeping baseline/labels/system proof.
Centralize exact Font window selection reads and correct character-list docs.
Host-free geometry regression passes; native fix rerun remains pending.

## 2026-10-17: Names native acceptance

Independent source review and fix review pass. The corrected native Wacute
screenshot shows the complete accent inside the outline frame; tall-accent and
side-overhang geometry regressions pass. Original constant expressions, presets
and signal callbacks match all five source tools. The shared shell supplies the
per-script heading label and lifecycle.

The installed App wheel passes the combined 25-tool run on FontLab 9.0.9784:
216 original workflow checks, 40 full preservation/history checks, 12 editor
safety checks, 32 switched/closed selection checks and actual Close destruction
for all 25 dialogs. All owned fonts close and App/fly/Fontport imports restore.
The Names checks compare every saved font/format field and dirty/Undo/master;
owned workspace UI changes are recorded separately. The live timer stops.

Fresh Python 3.11 checks: App 350, Scriptmix 151, installed App helpers 46.
All 25 source/destination hashes pass; the prior 20 mappings are unchanged.
Wheel 57 and sdist 95 entries contain 51 byte-identical source files, complete
licenses and updated NOTICE; private paths and scratch payloads are excluded.
Evidence: workspace issue111-tools25-v1, names-source-fidelity.json and the
source/fix reviews. Clipboard and chooser timing have no new native claim.
Full issue 111 remains active; no archived input is removed.

## Issue 111 Names dependency guidance fix 2

Require App0.2.6 in test-runner guidance and document tag-built wheels separately
from package-index availability. Refuse resolved helper trees missing the Names
panel. The installed final-wheel suite passes151tests with25provenance pairs;
product scripts and manifest are unchanged.

## Issue 111 read-only kerning implementation (native acceptance pending)

Add Classes Browser, Compare Masters, Pair List Browser, Missing Pairs and Text
Preview with every original control and original registry/class interfaces.
Share the lazy panel shell, guarded callbacks, validated selection, all-master
explicit pair/class reads and effective native kerning layout through App.
Preserve explicit zero versus missing pairs, numeric sorting and shown-order
UTF-8 CSV. The owned modeless chooser reports pair count and basename in a
wrapping status label. Proof fits complete transformed ink with actual advances
and native class fallback; paint and cleanup failures are contained. Invalid
or switched-font snapshots refuse selection, export and Copy. These five are
read-only; Exceptions Finder and Pairs From Text remain later editor work.
No native acceptance, publication or archive-removal claim in this milestone.

## Issue 111 Kerning review polish

Clarify Missing Pairs data types/coverage and Text Preview empty-state docs without
changing behavior. Make the new public work-log commands portable and retain exact
private receipts separately. App source remains identical to the native-tested wheel.

## 2026-10-17: Kerning native acceptance

Source and scoped fix reviews approve. Five kerning tools pass 31 independent
native workflow checks, ten complete saved-font/history checks, eight stale
class-selection checks, seven actual chooser/export checks and Close 5/5.
Screenshots show real wrapped accented outlines, native kerning positions,
master flags, class members, coverage and a concise export footer. Original
constant expressions and signal callbacks match all five originals.

The combined 30-tool run on FontLab 9.0.9784 passes 247 workflows, 50 complete
font/preservation/history checks, 52 safety checks, seven actual save-dialog
checks and native destruction of every dialog. Five informational composite
notes are retained separately from test counts. Clipboard invocation/check is
explicitly excluded under D8; Copy remains host-free tested. Exact exported CSV
UTF-8/CRLF bytes match independently read MCP values in native table order.

Python 3.11: App359 and Scriptmix171 tests pass; installed App helpers55 pass.
All30 source/destination mappings pass; the prior25 are unchanged. Wheel58 and
sdist97 entries contain52 exact source matches, licenses and NOTICE, with private
paths/scratch excluded. Public work-log recipes are portable; private exact
receipts are retained separately. Evidence: workspace issue111-tools30-v1 and
issue111-kerning-v1. Full issue111 and all remaining editors stay active; no
archived input or owner environment installation is changed.

## v1.0.14 — 2026-10-18 — complete guide panels

- Add complete Font Guides Panel, Grid Generator and Metric
  Reference Lines on the shared owned UI. Refuse unsafe automatic dependants
  before history. Safe edits restore complete fonts and prior Undo state.
  Native27original/21persistence/167controls/Close3 pass; all61prior tools pass
  on the same installed runtime. Artifact/source acceptance reviewed; fresh-tag
  acceptance follows release. Retain every original and the full Issue111 scope.

## v1.0.15 — 2026-10-18 — complete guide rewrite editors

- Add complete Clear Glyph Guides, Copy Guides Between
  Masters and Guide List Editor. Preserve retained native guide properties/hints,
  preconstruct whole batches and refuse unsafe dependencies/nonfinite cells.
  Native19original/21persistence/162controls/Close3 and prior64same-runtime
  regression pass. Current580App/756Scriptmix/263installed per artifact pass.
  Source/artifact/native acceptance reviewed; independent fresh-tag R053 follows
  release. Retain every original and the full Issue111 scope.


## Unreleased — issue120 tabular width report

Add a practical Apache-2.0 Pedro Arilla tabular-width report through shared App
and Fly. Compare actual selected active-master advances exactly; retain original
row statuses, counts and time heading. Use a modeless read-only snapshot with
Refresh and owned Close; diagnose empty, missing or changed sources. Preserve
owner Output content. Source/consumer/artifact checks pass; native acceptance
and release remain pending. This is additional to the130sample inventory.


## Unreleased — component recipe report candidate

Adapt Simon Cozens' MIT Recipe Dumper into shared App logic and a typed lazy
Fly menu. Preserve ordered/duplicate layer and component records, mixed layers
and original line endings; do not synthesize offsets or transforms. Native
capture currently binds Font-window selection on the active master, with stale
source/carrier/deadline guards. The owned modeless report supports Refresh,
clear failure diagnosis and Close. Original editor-tab/repeated/multi-master
selection and native acceptance remain open; the130sample count is unchanged.
Angularizzle remains an explicitly unfinished named priority requirement.


## Unreleased — Angularizzle workflow candidate

- Add the original Min plane/Keep detail/Process/Cancel workflow with ordered
  repeated selections, first-master targets, saved defaults and bound previews.
- Refuse stale or unsupported source plans before history; retain diagnosed
  recovery state after late native failures. Native acceptance remains pending.
- Restore actual overwritten target paths on Cancel, repairing the original
  cross-layer restoration defect. Closing keeps Process results.


## Unreleased — Recipe Dumper selected-layer adapter

Read actual ordered Font/Glyph-window layers through App’s shared selection
provider, retaining repeated editor slots and their layer choices. Compare
component reads and fence final selection/context before publishing. Native
qualification and complete font preservation remain pending.


## Unreleased — Tabular Width Checker selected layers

Use the shared Font/Glyph-window selection reader. Preserve editor repeats and
each slot’s layer choice; compare exact actual advances against the first
occurrence. Fence source/selection/context under one deadline before reporting.
Native selected-layer order/focus/preservation qualification remains pending.


## Issue120 M1 candidate

- Add licensed Slobzheninov Point Counter with complete foreground-layer/repeated-selection reports and explicit quadratic counting repair. Native acceptance remains pending.
- Expose the report through a typed Fly menu; original69 migration records remain unchanged.


Issue120 Q1 candidate: add all-open-font/all-master Vertical Metrics Reporter, eight exact stored values, unset/zero distinction, complete-source fences and owned Refresh/Close text panel. Native acceptance pending.

Issue120 R1 candidate: seven complete random-proof generation/tab workflows; preserve all4,991dictionary entries, draw order, casing and whitespace. Explicit current-font repair; native acceptance pending.

Issue120 T1 candidate: eight selected-glyph context proofs with exact order/repeats/contexts/blank lines, explicit native named symbols and a fresh-tab writer fence. Native qualification pending.

Issue120 W1 integration candidate: 93 practical and 61 preserved-source menu facades consolidated without copying/executing archive bodies. Native and distribution acceptance remain pending.

Issue120 Y2: verify current App completion hooks with accurate dialog-signal
doubles and real host-free helper loading; four actual Proof completion controls.
All practical/archive menus and provenance unchanged; no new native acceptance.

Issue120 Z1: complete Text Simplifier candidate with regex-class filtering,
input/read-only output/character fields, autosave/reopen, selective Reset,
original-font optional proof tab, resizing/geometry and owned completion.
Native PythonQt/settings/tab/whole-font-history qualification remains pending.

Issue120 Z2: complete selected-master Tallest and Shortest and all-foreground
Highest & Lowest Glyphs candidates share exact extrema/native capture and new
per-symbol layer tabs. Stable ties/repeated winners/zero/large coordinates are
preserved; missing layers are never created. All-layer coordinate results use an
owned panel with Run Again and survive a diagnosed tab failure. Shared NamesDialog
subtitle colour now follows palette changes. Native qualification remains pending.


Issue120 Z4: complete Why You Not Compatible? report candidate compares every
adjacent foreground-layer pair for each selected occurrence: ordered path/node
counts/types plus anchor/component name sets. Keep repeated groups, master-first/
auxiliary order and source messages; fix foreign first-glyph labels and global
path suppression, and sort displayed name sets. Owned Refresh/Close replaces
Output writes. These source checks are not an export-compatibility certificate.
Actual native topology/order/read/cache/font/history/reopen acceptance is pending.


## Issue120 current documentation Z5

A source-backed catalogue documents all158 current menu scripts without importing them. Hash-named build snapshots retain complete sources even when filenames contain parentheses, accents or apostrophes. Runtime menu bytes are unchanged.


## Issue120 documentation quality Z7

Documentation SDK tests now live under tests_docs and run in the locked documentation environment. Runtime tests stay on Python3.11. The real push gate combines both measurements without exclusions or a reduced threshold. No runtime menu body changes. All1070runtime/root tests pass with1existing skip, plus4SDK tests. The fixed coverage scope now includes the complete src_docs production root and all prior Scripts; the accepted baseline commit is unchanged.

These local gates do not establish native/font/history/reopen or site-publication acceptance. Exact commands and retained failures are in the parent verification/issue-120/docs-quality-z7/.


## Issue120 Z9 — bracket-layer report and proof candidates

Both Reset Type Studio source workflows now scan the complete current font's
foreground layer names and transitive component dependencies. Shared App core,
full-source observations and report/tab routes preserve both original groups.
The report explains overlap and counts a distinct total; the proof sorts names
and uses explicit glyph symbols, avoiding orphan slashes. Apache attribution
and the full licence are retained. Source originals are never executed.

Owned Qt6 controls and host-shaped boundary tests are offline evidence only.
Native PythonQt, dependency/cache/read preservation, complete saved-font/history
and actual symbol/layer mapping remain pending under D25. No native acceptance,
canonical merge, live install, tag, release or site publication is claimed.

## Issue120 Z24 — browser notices

Add source-bound full texts and provenance for named frontend components, including transitive JavaScript dependencies, icons, shared theme inputs and external font responses. Keep the full transitive/publication review explicitly open; runtime assets and retained archives are unchanged.

Z24 preservation found that the previous docs output path cleaned the authored integration guide in the isolated worktree. Restored the exact tracked guide, retained the earlier generated output in private evidence, and changed output to `.build/site/`. A tests-first regression rejects overlapping authored/output directories. No canonical source was changed. Fresh strict-build/preservation evidence is required below.

## Issue120 Z26

Preserve exact upstream notice bytes through Git filters, fresh checkout and archives; add a CRLF distribution regression. Source manifests and pending publication scope remain unchanged.

## Unreleased — isolate temporary notice repositories

- Clear Git's documented repository-local environment for temporary notice
  distribution commands and bound each child call to10seconds.
- Exercise inherited hook context with both default and alternate parent indexes;
  require byte-exact preservation of parent config, refs, index, objects, files
  and caller environment. Keep every notice/filter/checkout/archive assertion.
- Preserve all upstream notice payloads and existing attributes/manifests.
  Source-only correction awaits fresh independent review; no new commit/push.


## 2026-10-20 — curated active menu

Keep 99 practical tools in one-level Title Case menus. Retire 61 archive
dispatchers from active Scripts; preserve every unfinished tool and source hash
in the visible porting backlog. Prevent stale sibling bytecode in active menus.
Regenerate the catalogue from actual menu sources. Native acceptance for new
candidates, the original 130-sample migration and the broader scope remain open.


Known already-current migration rows now resolve idempotently through the same
reviewed move overlay as historical rows. Preserve manifest bytes and source
metadata. Unknown or ambiguous routes and changed hashes/bodies are refused.


## N48 — anchor-copy helper typing

Declare the existing rounded integer-point and optional native-glyph types in
Copy Anchors From Glyph. Add short purpose docstrings without changing executable
statements or imports. The glyph annotation is quoted and uses the existing
Fly-backed fontlab alias. Record the two exact source edits in menu-revisions.json;
current menu hashes and exact historical release bytes remain independently
verifiable. Historical migration rows and original-source hashes are unchanged.

## 2026-10-21 — three contour tools in the curated menu candidate

Add only the reviewed Select Contours, Select Small Contours and Select Partial
Contours facades and their exact independent Pedro Arilla provenance. The
curated source menu grows from99to102; its original99files remain byte-exact and
all61archived dispatchers remain excluded. Preserve menu_layout.current_rows,
owner-compatible manifest representations and every existing frontend notice.
Native acceptance and the full retained Issue120 requirements remain pending.


## N51 — combine reviewed contour menus and anchor typing

Combine source-reviewed and independently pushed N39 contour menus with N48
anchor helper annotations/docstrings. Retain the exact 99 N48 menu bytes and add
exactly 3 N39 menus, with their existing attribution and pending-native scope.
The source union introduces no additional runtime edits. The original 127 active
origins remain retained; all sample/archive backlogs and native gates stay open.

Full installed App0.2.73/Fly source checks pass 982 tests/one explicit skip plus
10 documentation SDK tests. The unchanged quality gate reports 94.95% aggregate
changed-production coverage above all configured 80% floors. A private owner
overlay rehearsal retains the raw manifest, 13 literal files and 2 bounded historical/
current-view test adapters plus 7 merged owner docs; it repeats 982/1 + 10 tests and
the strict offline build. Canonical application and native acceptance remain
controller-owned and pending. Exact receipts live outside the public tree.

## Unreleased — complete reporting pair candidate
Add first-master node compatibility counts/first differences and own-path SVG
commands with shared Refresh/Close panels. Fix original false-compatible cases;
retain unconditional Z policy and refuse unsupported whole reports. Native pending.


## N68 Same Kerning Groups proof candidate

Implement the complete first-selected-glyph left/right peer proof, independent class maps, font order, explicit named peers, literal labels and original empty/singleton diagnosis. Native acceptance pending.


N68 repair round1 (.82): preserve first selected parent only, without layer or later slot/block-ID reads. Peer-side resolution is conditional on current groups; no-group diagnosis skips the peer inventory. Prior .79/N75 failures retained; 53 focused controls pass. Whole ordinary artifact/native qualification receipts: verification/issue-120/kerning-group-proof-z31/repair-round1/. Native acceptance remains pending.


## N105 Close But No Cigar (.93 source candidate)

Complete ordered all-selected-parent/first-layer near-angle, horizontal/vertical
stem and six node-position checks, with explicit associated-master data and
strict original boundaries/exclusions. Shared modeless Refresh/Close report;
no Output/font/selection writers. Numeric cubic angle repaired; original curve
sampling/open wrap preserved. Tests, source/API calibration and ordinary
archive verification: workspace verification/issue-120/near-miss-z35/.
Native acceptance, root review and delivery remain pending.

## Issue120 N119 — complete duplicate-anchor source candidate

Retain the complete original all-master duplicate removal workflow, exact first-in-layer/name-family/coincident policies, opening-selection scope and auto-layer skips. Direct original pin removals use preflight and one final layer/glyph notification; partial failures remain explicit for Undo. Native one-Undo, whole-font/history/dirty/save/reopen and lifetime acceptance remain pending. No native/live/canonical operation occurred.


N97 Text Holder candidate (.91): full editable/resizable floating window; literal
Find first/highlight; UTF16-correct selected-or-whole replacement; Save stays
open, Save & Close, Ignore & Close; owned-path UTF8 persistence and window size.
Source/licence disposition retained; no original body is copied or executed.
No native calls or user-store validation. Native acceptance remains pending.

N97 geometry repair: preserve initial content500×400 separately from source
NS frame min500×400/max1200×800. Persist decorated frame sizes, restore client
sizes by measured chrome and map literal Cocoa origin(0,500) through complete
primary logical screen geometry/current frame height after first show; no
availableGeometry, DPR scaling or silent clamp. Prior .91 commits/artifacts
are retained in attempt2; no immutable final .91 freeze existed before repair.
27 focused actualQt5 controls pass; independent geometry controls pass bothQt5
andQt6. Native qualification remains pending on root final combined .92.

N97 final source fidelity: use normal Qt.Window with stays-on-top and explicit
title/system/close/minmax hints, matching original Vanilla Window/NSWindow
role rather than Tool/NSPanel hide-on-deactivation behavior. Preserve literal
button ampersands, full frame constraints, Cocoa origin and saved frame sizes.
Producer28 actualQt5 controls and independent32controls perQt5/Qt6 pass;
ordinary final .91 artifacts and full declared147/42 gates are bound separately.
Native acceptance remains pending on root combined .92, never claimed for .91.

N97 literal-Unicode repair revision4: frozen8433...candidate retained as failed
source attempt after independent NBSP/LS/PS Find/Save counterexamples. Added
text_holder_editor with undo-aware native block separator provenance; literal
block.text reads preserve NBSP/LS and distinguish PS/LF. Controlled text ingress,
local mime copy/paste, native Return, IME, selection merge and Undo/Redo preserve
literal text; original disk universal-newline read remains unchanged. Four
owned modules; complete App milestone scope grows148, Scriptmix stays42, no
sample denominator changes. Qt5/Qt6 focused51controls each pass at this stage.
Native acceptance remains pending on root combined.96 onto.94; .92 prep is
historical and .91 remains a private source candidate, never native acceptance.

N97 ownership repair revision5: independent pinned PythonQt virtual-return source
identified an ownerless Python-QMimeData lifetime seam (host binary equivalence
unproven). The copy factory now returns the explicit nativebase Qt-owned object;
its lazy source fragment is materialized before clear/setText, preventing a
later default MIME read from overwriting the literal payload. Constructor-route
tripwire is RED on revision4 source/GREEN now.52producer Qt5/Qt6 controls pass.
Revision4 ordinary archives eef6ac94.../305df303... and full148/42 gates remain
retained as a prior source attempt, with no immutable candidate promotion.
Fresh revision5 ordinary artifacts/full unchanged gates bind this repair.

## N145 .118 Point Counter literal selection repair

Import complete Reza master-layer report on reviewed .106, preserving its prior workflows.
Reuse unchanged Text Holder literal editor read-only; preserve NBSP/LS/PS and UTF16 selections.
F1 RED, complete artifacts/consumer/coverage results are recorded after verification. Native pending.

N145 final .118 source/artifact gates:27focused controls pass source Qt5/Qt6
and all4installed Qt/archive lanes;4actual public Fly/menu literal-MIME controls pass.
Both complete7consumer graphs pass13752tests/3existing skips. Original whole scopes
182App/45Scriptmix/70Examples pass80statement AND80branch perfile, zeroexclusions.
Scriptmix15SDK/docs tests and strictbuild pass; unchanged .106 Examples docs coverage
is reused byte-exact with explicit attribution, no write to that frozen tree.
F1selection RED and readonly IME REDs retained. Literal helper byte-exact to .106;
report-local IME ignores all preedit/commit. New report PythonQt/native probe pending.
Exact commands/exits/archives/receipts: verification/issue-120/point-counter-repair-z43.
No native/canonical/push/user-store/clipboard changes. Independent review required.

Added complete Dangerous Offcurves full-font probe action and exact-layer proof tab; explicit fontTools analytic ordering adaptation.


N157 finite-probe numerical repair (.120): exact control-hull exclusion prevents
rounded solver hits for curves strictly beyond either finite probe endpoint.
Exact endpoint coordinates replace rounded backend endpoint hits only when
source fixed-coordinate equality and finite bounds prove the hit. All four
probes, strict0.05 predicate, traversal, owned result and real-layer tab workflow
remain. Ascending curve-time ordering stays an explicit adaptation; Glyphs
engine equivalence and complete FontLab native acceptance remain pending.

N160 retained first .120 artifacts as a failed attempt: an outside exact endpoint
can round onto a finite probe even with overlapping hulls. Drop numerical t0/t1
hits before restoring only valid exact source endpoints; interior roots survive.


N162 combined source candidate: The combined App0.2.122.dev0 source candidate adds Reports > Point Counter (Master Layers) and Dangerous Offcurves, preserving all prior109menus and both complete original workflows. Dangerous Offcurves uses explicitly adapted ascending fontTools curve-time intersection order; opaque Glyphs engine equivalence remains unproved. Literal text is checked after publication; a lossy literal NUL is refused and remains a native host hold. Source/artifact verification does not complete native/font-history preservation acceptance.

## Duplicate Unicodes .121 candidate

Complete whole-font checkbox cleanup editor through shared App/Fly, preserving primary-owner defaults and ordered surviving assignments. Adds stale/preflight/partial-write handling and single final history notification; original native getter/UpdateAll paths are not used. Native qualification remains pending.



N185 private source candidate: complete all-master Kerning Cutoff action retains inclusive[-250,100], explicit pair kinds and per-master counts; repairs earlier-master-only notification with the qualified batch writer. Native qualification pending.


N193 test compatibility: the owned kerning fixture exposes the resolved package search path instead of preventing genuine shared helper imports. All menu bodies and runtime requirements unchanged.


## Unreleased .137 — Complete typed kerning symmetry

Add the complete Science Gothic 28-target/378-comparison Symmetry writer with lossless explicit glyph/group identities, sequential class aliases and zero deletion. Preserve original # and case-sensitive Ctr master exclusion. Cutoff retains its distinct all-native-master policy. Native qualification pending.

N226: private .145 coherent union on reviewed .141; complete admitted CopyAnchors/shared scalar-style reader .144 and TextHolder/literal helper .139revision3 retained. Fresh artifacts/full consumer/Qt/whole-original coverage verification pending; full native qualification remains separate. No host/canonical/live install writes.

N235: integrate complete reviewed literal TextHolder/anchor tools, both literal Find Files profiles and generic Qt table items without replacing prior workflows; host acceptance remains pending.

## N236 — complete four kerning proofs

Add Hoefler Lowercase, Hoefler Uppercase, KernKing and KernSym through shared App/Fly. Keep all five exact licensed texts and KernKing two-tab order. Preserve Output. Ordinary artifact/current consumer/whole-module verification follows; full native tabs/font/history acceptance remains pending.

### N228 — paired whole-font background cleaning candidate

- Add distinct all-layer and declared-master background removal tools through Fly/App.
- Remove original whole mask objects; reject ambiguous mapping and automatic dependencies before history.
- Contain partial native failures with one final notification and explicit Undo diagnosis. Native acceptance pending.

### N239 — background failure and active-state repair candidate

- Always attempt one final notification after attempted removal, aggregate individual pre/post stamp and notification errors.
- Use nonassigning active resolver; active/locked backgrounds remain explicitly unsupported original-domain gates.
- Prepare survivor identities in checked per-glyph passes before history, and fence final staged sources/queue.
- No native acceptance or reconstructed background rollback.

N248 complete .153 union retains reviewed .148 and all four .149 proof workflows/five licensed texts, both complete .151 background cleaners and final admitted .152 Character Map contrast. Preserve full original workflow/coverage denominators and all prior menus. Active/locked backgrounds remain UNACCEPTED; all native font/history/reopen gates stay open. No canonical/native/live installation/push.

- Private .159 integrates complete Raise Ascender with reviewed .157 failed-Close lifetime repair; all original font/history domains remain pending.

- Private .159 includes complete reviewed Perpendicular Guides: selected nodes and component centre guides, first-selected-layer scope, transformed geometry and retained carriers; native full-font/history acceptance remains pending.
