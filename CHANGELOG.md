---
this_file: CHANGELOG.md
---

# Changelog

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
