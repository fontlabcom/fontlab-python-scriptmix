---
this_file: WORK.md
---

# Issue 111 first batch

## Controller acceptance: second Reports batch

47Python3.11 tests pass; review APPROVE without blocking findings. Original five
scenarios pass on FontLab9.0.9784 through the installed helper wheel:42checks,
including all205CSVrows and actual file export, live glyph follow/width+10,
Rafi2702-glyph mark/suffix/Add selection, transformed zone nodes and Unicode
block counts/selection. Screenshots of every tool reviewed and readable. All
owned dialogs/fonts clean up; live timer stops. Host sys.path/module identities
restore after the run. Evidence in workspace ecosystem evidence:
issue111-reports-batch2-v1/summary.json. No original source removed.

Added three complete modeless reports and a provenance manifest. Original source
files were not modified. Shared helpers protect stale-font selection and validate
all names before clearing. Seven host-free report tests exercise calculations,
missing-font refresh, stale-font selection and manifest integrity. Native proof
is pending.

Commands: `rtk proxy uv run --no-project --with pytest python -m pytest -q fontlab-python-scriptmix/tests .worktrees/issue111-app/tests/test_scripting.py`
(from workspace root): exit 0, 13 passed. Scoped Ruff initially corrected
imports/formatting; a subsequent run passes (exit 0).

Controller native acceptance (2026-10-17): all three original scenarios pass in
FontLab9.0.9784 against the installed helper wheel. Empty Glyphs6, Open Contours6
and Overview14 independent checks pass; all dialogs/fonts cleaned up. Screenshots
reviewed for readable text/tables and complete controls. Evidence in workspace
verification/issue-101-ecosystem/evidence/issue111-reports-v1/summary.json.
Initial runner refused an unsaved owner font (exit76); owner saved/closed it,
then guarded run exited0 without a crash. Source files remain retained in `_old`.
Fresh controller Python3.11 tests11pass; app310pass; wheel helper6pass and47
production files match source bytes. Fix review: original P1 addressed, no new
blocking findings. Native/GUI claims refer only to these three report scripts.

## Issue 111 review round 1

Fixed failed-refresh selection: invalidate the prior snapshot before native
access, scan into local rows, populate the full table, then publish rows/id. Any
scan or display exception clears partial table data, keeps selection disabled,
and rejects direct select_rows calls. Four regression cases first failed against
the old code (genuine RED retained), then passed after this fix. No native run.

## Issue 111 second Reports migration (2026-10-17)

Preserved five complete Apache-2.0 report implementations and original scenario
keys. Ported imports to fly and package-id-bound selection helpers. Scans resolve
the current package afresh; no closed retained package is dereferenced. UI scans
use local results until full display completes. Add merges current selection
only after validating the computed font id. Live timer stops and all owned
signals disconnect on close; the CSV chooser closes and deletes with its report.

Tests-first RED: `rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project
--python 3.11 --with pytest python -m pytest -q
fontlab-python-scriptmix/tests/test_report_batch2.py` exited 1: nine failures,
including five genuine requested-module existence assertions. After migration,
35 tests pass (exit 0), covering real layer/CSV/Unicode calculations, all five
success/no-font/scan/display paths, stale selection, Add and close teardown.
Scoped Ruff initially exited 1; native slot guards were documented and fixture
imports/unused doubles fixed; scoped check and format now exit 0. Final all-tests
command and result are recorded in task-3b-report.md. Native runs not performed.


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

Verification: app `rtk proxy env PYTHONPATH=.worktrees/issue111-app/src fontlab-fontlabapp/.venv/bin/python -m pytest -q .worktrees/issue111-app/tests`: exit 0,315 passed13.01s; Scriptmix `rtk proxy uv run --python 3.11 --no-project --with pytest python -m pytest -q fontlab-python-scriptmix/tests`: exit0,55 passed0.10s. Scoped Ruff and both git diff --check exit0. Exact RED/GREEN and source hashes: `.superpowers/sdd/issue-111/task-2b-report.md` at workspace root.


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

## 2026-10-17 — Issue111 Features source checkpoint

Six complete Features tools retain their original controls, proofs, Copy and
search/filter interactions. Shared App FeaturesDialog extends the existing
FontInfoDialog shell/lifecycle. Build uses App's lazy Fontport ordered feature
writer, exact source/current-font/reference validation and existing native
history safety checks. No source archive or prior14tool bytes changed.

RED: `rtk proxy bash -c 'cd fontlab-python-scriptmix && ./test.sh'` exit1,
6requested-file failures/83existing passes. Actual Fontport integration caught
a missing LF in the generated final feature block (1failed5passed); fixed
Build's preview, then6passed. Other failed setup/style attempts are retained in
workspace `.superpowers/sdd/issue-111/task-3d-report.md`.

Final `rtk proxy uv run --python 3.11 --no-project --with pytest python -m pytest
-q fontlab-python-scriptmix/tests`: exit0,108passed. Final `rtk proxy env
PYTHONPATH=.worktrees/issue111-app/src:fontlab-fontport/src
fontlab-fontlabapp/.venv/bin/python -m pytest -q .worktrees/issue111-app/tests`:
exit0,334passed,13.06s. Both final interpreters are Python3.11. Scoped Ruff
check/format and both repository diff checks exit0;20manifest hash pairs pass.

Wait, but: source tests cannot prove native Undo, source persistence or actual
widget destruction. Those gates, original scenarios and screenshot review stay
with the controller. No native runs, owner-site installs or commits were made.
Production sources frozen with SHA256 in the task report. Full issue111 scope,
archive cleanup and final docs/release work remain open.

## Task3d round1 review fixes — 2026-10-17

Extract duplicated suffix/FEA/name validation into host-free App feature_code,
consumed through fly.ap by the current Build/Suffix/Ligature tools. Preserve the
original helper import surfaces and alternate-name pair ordering. Add concrete
calculation row types and docs for class exclusion, suffix counts, recipe Ready
limits and exact feature source order.

Fix the measured Feature Code Viewer native boundary: native iteration returned
positions and raw prefix synthesized classes. It now displays the complete exact
read_feature_blocks snapshot, preserving prefix text and ordered source blocks.
A genuine new RED calls the actual viewer.setup against iterator[0,1]/blank
get_feature and synthetic prefix doubles; it failed on the incorrect sources
before the fix, then passed on exact independent blocks. No native execution or
blind performance optimization was performed in this round.

Commands: `rtk proxy uv run --python 3.11 --no-project --with pytest python -m
pytest -q fontlab-python-scriptmix/tests/test_features.py -k viewer_uses`: exit1,
1failed25deselected (RED). Final full Scriptmix command without the selection:
exit0,110passed0.11s. `rtk proxy env
PYTHONPATH=.worktrees/issue111-app/src:fontlab-fontport/src
fontlab-fontlabapp/.venv/bin/python -m pytest -q .worktrees/issue111-app/tests`:
exit0,347passed13.06s. Direct shared-helper tests account for13new App checks;
shared identity and actual viewer boundary add2Scriptmix tests. A pre-freeze run
had109passes/1expected stale-manifest failure; refreshed only Features hashes.
Scoped Ruff check/format pass;20source/destination hash pairs verify. Updated
production hashes are in the workspace task3d report. Native acceptance of these
revised bytes remains the controller's task.


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

## Task 3e: portability

Baseline isolated archive reproduced RED: 6 passed / 3 App lookup errors (exit1).
Removed private checkout defaults; installed App files resolve without native
imports before module doubles. Added three dependency resolution regressions.
Default checks retain 20 destination hashes, menu paths, syntax and provenance;
--original-source-root explicitly enables all20 original hash checks.
Product sources and migration.json remain unchanged. Exact verification commands
and final isolated results are in workspace .superpowers/sdd/issue-111/task-3e-report.md.

Verification (all commands prefixed `rtk proxy`):
- `bash -c 'cd fontlab-python-scriptmix && SCRIPTMIX_APP_REQUIREMENT="$PWD/../.local/issue111-app-features-fix1-dist/fontlab_fontlabapp-0.2.1.dev75+g0f3f8962b.d20261017-py3-none-any.whl" ./test.sh --original-source-root ..'`: exit0,113passed;20source/destinationpairs.
- Archived committed checkout outside workspace: same wheel with `./test.sh`,
  exit0,113passed;20destinationhashes. No originals/siblings present.
- Explicit missing-original and mismatched-original probes: each exit1,
  1failed/112deselected (expected); no silent skip.
- `uvx ruff check tests`, `git diff HEAD^ --check` and
  `git diff 86a48ce --exit-code -- Scripts migration.json`: exit0.
One initial Ruff run found two import-order issues; fixed and reran successfully.
No native run: product bytes unchanged. No push/release or owner environment edit.

## Issue 111 task 3f — Names sources frozen for native review

Five new complete Names tools preserve the original registry/class/method
interfaces, controls, language data, keyboard/row/copy actions and outline proof.
Shared lazy App shell/table/font access, guarded signals and complete-refresh
snapshots replace duplicated lifecycle/selection logic. Validate every requested
name and original font identity before clearing selection; Keep/Add retained.
Live Character Info refreshes even for same-name font/master changes and stops
on Close; original has no Pause control. Painter errors and error hooks remain
contained and painter ends in finally. No metadata/design/master writes.

Test-first RED: five missing requested files, 113 existing tests passed (exit1).
Intermediate runs exposed one test tuple-unpacking mistake, manifest20 awaiting
update and a copied-fixture closure mistake; corrected. Final 35 new Scriptmix
checks include actual action inputs, direct failed refreshes for all five tools,
Unicode/case/charset/glob/mark calculations, stale/closed fonts, missing names,
copy, transformed outline parts, timer teardown and failing painter/error hook.
Two App Add-selection regressions added. Earlier App full run347 passed; final349.
All original twenty manifest entries unchanged; append five, exact menu depth.
No archived source writes, native calls, owner installs, commits or push.
Native original workflows, screenshots, font invariance and actual destruction
remain pending controller verification. Freeze report includes every changed and
new file hash: workspace .superpowers/sdd/issue-111/task-3f-report.md.

Verification from workspace root:

```sh
rtk proxy bash -c 'cd fontlab-python-scriptmix && SCRIPTMIX_APP_REQUIREMENT="$PWD/../.local/issue111-app-v0.2.5-dist/fontlab_fontlabapp-0.2.5-py3-none-any.whl" SCRIPTMIX_APP_SOURCE="$PWD/../.worktrees/issue111-app/src/fontlabapp" ./test.sh --original-source-root ..'
# exit 0: 148 passed in 0.14s; all 25 source/destination pairs audited.
rtk proxy bash -c 'cd .worktrees/issue111-app && ./test.sh -q'
# exit 0: 349 passed in 12.91s.
rtk proxy uvx ruff check fontlab-python-scriptmix/Scripts/Names fontlab-python-scriptmix/tests/test_names.py fontlab-python-scriptmix/tests/test_reports.py .worktrees/issue111-app/src/fontlabapp/scripting.py .worktrees/issue111-app/src/fontlabapp/_names_dialog.py .worktrees/issue111-app/tests/test_scripting.py
# exit 0: All checks passed.
rtk proxy git -C fontlab-python-scriptmix diff --check
rtk proxy git -C .worktrees/issue111-app diff --check
# each exit 0.
```

## Task 3f review fix 1 — complete Character Info proof fitting

Controller reports all five original scenarios pass33checks on the initial
native build with complete saved font/history invariance. Its Wacute screenshot
revealed the left accent clipped: vertical fitting only used master metrics and
horizontal centering only used advance. New actual Specimen.draw regressions
reproduced RED (2failed/1passed/148deselected): tall accent y=-79 and overhang
x=-17.2..319.2 escaped the padded left frame. Fit the union of actual transformed
path bounds, advance, metric frame and baseline in both axes; reserve labels and
retain system proof/painter containment. GREEN:3passed/148deselected. Native
screenshot/geometry acceptance of this fix remains pending controller rerun.

Corrected comparison-list Unicode describe docstring. Select by Mark's retained
font_window_selection interface now thin-wraps shared exact-selection access,
with no current-glyph fallback; the existing fallback helper uses that reader.
App gains an exact-empty-selection regression. No other behavior changed.
No native calls, owner installs, commits or pushes in this fix.

Commands from workspace root (all exit0 unless noted):
- `rtk proxy bash -c 'cd fontlab-python-scriptmix && SCRIPTMIX_APP_REQUIREMENT="$PWD/../.local/issue111-app-v0.2.5-dist/fontlab_fontlabapp-0.2.5-py3-none-any.whl" SCRIPTMIX_APP_SOURCE="$PWD/../.worktrees/issue111-app/src/fontlabapp" ./test.sh -k "fits_tall_accents or mark_selection_reader"'`: RED exit1,2failed/1passed; GREEN exit0,3passed.
- Same environment and `./test.sh --original-source-root ..`:151passed (0.14s),25provenance pairs; original20unchanged.
- `rtk proxy bash -c 'cd .worktrees/issue111-app && ./test.sh -q'`: full App results in freeze report.
- `rtk proxy uvx ruff check fontlab-python-scriptmix/Scripts/Names fontlab-python-scriptmix/tests/test_names.py fontlab-python-scriptmix/tests/test_reports.py .worktrees/issue111-app/src/fontlabapp/scripting.py .worktrees/issue111-app/src/fontlabapp/_names_dialog.py .worktrees/issue111-app/tests/test_scripting.py`: All checks passed.
- `rtk proxy git -C fontlab-python-scriptmix diff --check` and `rtk proxy git -C .worktrees/issue111-app diff --check`: each exit0.

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

Controller native command uses fl-native.sh --mutating --lane issue111-tools25, FL_RESTART=1, PYTHONDONTWRITEBYTECODE=1, installed final App wheel, all 25 manifest scripts and --verify-close --verify-safety --verify-names-safety. Exact argv/exit0: issue111-tools25-v1/native-command-receipt.json.
