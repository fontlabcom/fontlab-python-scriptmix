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

## Task 3f dependency guidance fix 2

Align runner/README minimum guidance with App0.2.6, which contains the Names
helpers. Explain tag-built wheels without claiming package-index availability.
The shared source resolver now requires _names_dialog.py alongside the existing
four helpers. Scripts, migration and App bytes remain unchanged from the
controller-verified freeze. No native calls, commits, pushes or installs.

Missing-helper regression: a temporary source tree containing only the four old
helpers was accepted before the fix (probe exit1, expected RED); after adding the
Names check the same probe exits0 and reports "Missing Names helper refused
explicitly." No new test-file scope or dependency was introduced.

Exact verification commands from workspace root:
- `rtk proxy uv run --no-project --python 3.11 --with pytest python /tmp/issue111-missing-names-check.py fontlab-python-scriptmix/tests/conftest.py`: RED exit1 (incomplete helpers accepted); GREEN exit0.
- `rtk proxy bash -c 'cd fontlab-python-scriptmix && env -u SCRIPTMIX_APP_SOURCE SCRIPTMIX_APP_REQUIREMENT="$PWD/../.local/issue111-app-names-fix1-dist/fontlab_fontlabapp-0.2.6.dev0+g8e4463d52.d20261017-py3-none-any.whl" ./test.sh --original-source-root ..'`: exit0,151passed in0.14s;25source/destinationhashes, installed final wheel only (no source override).
- `rtk proxy uvx ruff check fontlab-python-scriptmix/tests/conftest.py`: exit0,All checks passed.
- `rtk proxy git -C fontlab-python-scriptmix diff --check`: exit0.
- `rtk proxy git -C fontlab-python-scriptmix diff --exit-code HEAD -- Scripts migration.json`: exit0; native product bytes unchanged.

## 2026-10-17 Task3g: complete read-only Kerning source implementation

Implemented five complete originals: Classes Browser, Compare Masters, Pair List
Browser, Missing Pairs and Text Preview. All original controls, KEY/registry and
class/method interfaces remain. Shared lazy KerningDialog reuses the Names shell,
exact guarded callbacks, selection validation and close lifecycle. Named-master
explicit items/groups retain @names, class sides, fractions and explicit zero.
Native effective get(names) supplies kerning precedence, rather than adding a
second calculator. Fontport's existing reader targets the current master and
UFO-normalized group names; its editor and optional dependency are unnecessary
for these inspectors. Native pyfontgate/fgkerning.cxx lines627-634 and675-702
confirm explicit items versus effective get(names). Local QtGui stubs consulted.

Every outgoing action validates the complete snapshot's font; unknown names
fail before clearing selection. Failed native/table/proof work clears partial
rows, classes and paths and disables selection/Copy/export. Pair List exports
actual shown numeric-sort order through an owned modeless chooser; wrapping
status reports count and basename. Proof materializes actual transformed
outlines before publication and fits all ink, tall accents and overhangs with
native pen positions; painter construction/draw/end and failing error hooks
are contained. No native calls, owner installs, commits, pushes or original
archive writes occurred. Exceptions Finder and Pairs From Text stay editors in
later full-scope work. App minimum guidance targets forthcoming0.2.7 without an
index-publication claim. Portable tests use explicit0.2.6wheel plus source override.

Wait, but: an arbitrary long proof could still overflow when fixed label gaps
exceeded the whole canvas. The fitting helper now bounds label space too;
200-row overflow and tall/side-overhang checks retain every glyph. Painter-end
errors now invalidate the proof just as drawing errors do. These are host-free
receipts only, not native acceptance.

Verification recipes from workspace root (portable placeholders; exact private receipts retained in the workspace task-3g report):
- `rtk proxy env SCRIPTMIX_APP_REQUIREMENT=/path/to/current-app.whl SCRIPTMIX_APP_SOURCE=/path/to/updated-app/src/fontlabapp fontlab-python-scriptmix/test.sh tests/test_kerning.py`: RED exit1,5missing-filefailures/151pass.
- Intermediate full suite: exit1,164pass/2fail (new category missing from test set and installed-only portability probe required a helper absent from supplied0.2.6wheel). Added Kerning category and explicit resolver helper subset for the installed baseline probe; default/source checks still fail closed on missing Kerning helper.
- `rtk proxy env SCRIPTMIX_APP_REQUIREMENT=/path/to/current-app.whl SCRIPTMIX_APP_SOURCE=/path/to/updated-app/src/fontlabapp fontlab-python-scriptmix/test.sh --original-source-root ..`: GREEN exit0,171passed in0.15s;30source/destinationmappings. Prior25exactly unchanged (compared to HEAD JSON).
- `(cd .worktrees/issue111-app && rtk proxy env UV_LINK_MODE=copy uv run --python 3.11 --extra test python -m pytest -q)`: exit0,359passed in13.71s (original350plus9new).
- `rtk proxy uvx ruff check fontlab-python-scriptmix/Scripts/Kerning fontlab-python-scriptmix/tests/test_kerning.py fontlab-python-scriptmix/tests/test_reports.py fontlab-python-scriptmix/tests/test_portability.py fontlab-python-scriptmix/tests/conftest.py .worktrees/issue111-app/src/fontlabapp/scripting.py .worktrees/issue111-app/src/fontlabapp/_kerning_dialog.py .worktrees/issue111-app/tests/test_kerning_scripting.py`: exit0.
- `rtk proxy git -C fontlab-python-scriptmix diff --check` and `rtk proxy git -C .worktrees/issue111-app diff --check`: each exit0.

Native original scenarios, actual chooser/Close, full saved-font/history invariance
and installed-wheel proof await controller verification. Source report/freeze:
workspace .superpowers/sdd/issue-111/task-3g-report.md and task-3g-freeze.json.

## Task3g fix1: concrete types, precise docstrings and portable receipts

Typed Missing Pairs coverage inputs and Cartesian-product outputs concretely;
kept the native FontLab package wrapper Any. Explained zero-valued coverage,
side-specific classes and input ordering, and clarified Text Preview's empty
state. Product behavior is unchanged: AST comparison against the before-fix1
snapshot passes after removing only type annotations/docstrings. All52App source
modules remain byte-identical to the frozen native wheel. Refreshed only the two
script destination hashes; all prior25mappings remain exactly unchanged.

Replaced personal home paths in the new public WORK command recipes with clearly
labelled portable placeholders. Exact original receipts remain in the private
workspace task-3g report. Both public Markdown trees have no personal home paths.

Verification from workspace root:
- `rtk proxy env SCRIPTMIX_APP_REQUIREMENT=/path/to/current-app.whl SCRIPTMIX_APP_SOURCE=/path/to/updated-app/src/fontlabapp fontlab-python-scriptmix/test.sh --original-source-root ..`: exit0,171passed in0.15s; exact private invocation in task-3g-report.md.
- `rtk proxy uvx ruff check 'fontlab-python-scriptmix/Scripts/Kerning/Missing Pairs.py' 'fontlab-python-scriptmix/Scripts/Kerning/Text Preview.py'`: exit0.
- Both repository `rtk proxy git -C <repository> diff --check` commands: exit0.
- Before-fix1 behavior AST,52module wheel-byte comparison and public-doc path audit: exit0.

Controller reports native5acceptance:31workflow,10fullfont/history,7chooser/CSV,
8staleclass-selection and Close5/5, with5screenshots inspected. This worker made
no native calls, commits, pushes, owner installs or App source changes. Fix1 adds
no new behavior requiring another native run; controller decides integration.

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

Native command through fl-native.sh --mutating --lane issue111-tools30 with FL_RESTART=1, PYTHONDONTWRITEBYTECODE=1 and installed App wheel runs all30 manifest scripts with --verify-close --verify-safety --verify-names-safety --verify-kerning-safety --verify-kerning-chooser. Exact argv/exit0 retained in issue111-tools30-v1/native-command-receipt.json.

## 2026-10-17 Task3h: five complete Kerning editor sources

Implemented Copy Between Masters, Pair Editor, Scale Values, Round Values and
Remove Small Pairs, retaining original controls, source/target/mode choices,
per-master cells, add/delete, zero options, preview ordering, counts and original
KEY/class/method/registry interfaces. App owns shared pure plans and rounding,
complete native pair/class/master snapshots, one all-master writer, lifecycle,
Refresh recovery and Scale/Round rendering; Scriptmix enters through fly.ap.

The writer stages every selected master before notification. It validates name
structure/existence/class side, whole signed32 values, nonblank history label,
original current font and exact scanned pairs/classes/masters. It preserves
explicit zero versus absence using native seed/scale and restores all unrelated
nonzero pairs in that master. Fractional source history on any master is refused;
no-op adds no history. Only package/master/kerning containers enter the shared
before/after checkpoint. Native writes/readback may be partial on failure and say
so while retaining the after checkpoint. Failed/stale previews clear partial
staging and disable Apply; invalid cells remove only their own invalid stage and
leave other valid edits available. Rebuilding the editable table retains staged
and invalid text. Failed refresh after a write cannot overwrite the error with
success counts. Optional dependencies remain lazy and no package is added.

Wait, but: checking changed master membership before the original-font guard
would read a closed package. The final snapshot guard checks current font first.
A post-write preview failure could also have hidden success or raised a None
count error; explicit outcome feedback now separates it from successful refresh.
These are owned-host/source checks only. Original scenarios, installed/native
complete-font deltas, one real Undo/Redo, saved reopening and actual Close remain
pending controller verification. No original source, owner install, commit or
remote branch was changed. All35source/destination hashes pass; prior30unchanged.

Portable verification recipes from the workspace root (private exact invocations
and initial failures retained in the workspace task-3h-report.md):
- `rtk proxy env SCRIPTMIX_APP_REQUIREMENT=/path/to/current-app.whl SCRIPTMIX_APP_SOURCE=/path/to/updated-app/src/fontlabapp fontlab-python-scriptmix/test.sh`: RED exit1,5missing-editor failures with171existing tests passing.
- `(cd .worktrees/issue111-app && rtk proxy env UV_LINK_MODE=copy uv run --python 3.11 --extra test python -m pytest -q)`: final exit0,399passed in13.88s, including40new owned batch/planning tests.
- `rtk proxy env SCRIPTMIX_APP_REQUIREMENT=/path/to/current-app.whl SCRIPTMIX_APP_SOURCE=/path/to/updated-app/src/fontlabapp fontlab-python-scriptmix/test.sh --original-source-root ..`: final exit0,215passed in0.24s,35provenance mappings and Python3.11syntax/menu checks.
- `rtk proxy uvx ruff check <changed Python files>`: exit0,All checks passed.
- `rtk proxy git -C fontlab-python-scriptmix diff --check` and `rtk proxy git -C .worktrees/issue111-app diff --check`: exit0.

Forthcoming App0.2.8 helper guidance/resolver checks are explicit; use a current
wheel plus source override until its artifacts exist. Native acceptance is
unchecked in PLAN/TODO; full130-stem migration and other archive collections
remain active, with all originals retained.

## Task3h range fix — retain values across native reopening

Controller's owned native persistence control found signed32 endpoints save but
reopen clamped to +/-2*UPM with a mark. The native load pipeline in
Proteus/workspace2/ioengine.cpp12898–12941 confirms it clamps all masters on load.
Following the controller's recorded ruling, the shared writer now validates the
ENTIRE final font's kerning against inclusive +/-2*current positive finite UPM,
including masters not edited by the batch, before history/writes. It refuses
clearly, never clamps. Valid correction/deletion of existing extreme pairs is
allowed; no-op bypasses the new range check and stays untouched. Existing
signed32 and fractional-history safety stays; Fontport is unchanged.

Tests first:13range/UPM failures and7allowed/repair/no-op controls; real PairEditor
Apply also reached history initialization before refusal. After the shared
preflight,60owned App batch tests and the real Apply refusal pass. Final full
suite counts and exact private receipts are in task-3h-report.md. No native
calls, commits, agents or archive writes occurred. Controller owns focused native
limits verification and the final combined35tool gate.

Range-fix final Python3.11 suites:App419passed in13.73s;Scriptmix216passed in0.34s with all35provenance mappings; changed-file Ruff and both diff checks pass. Native acceptance remains with the controller.

## Controller acceptance: five Kerning editors and full35 gate

Source, wording and native range-fix reviews PASS. Native9784 original5 pass33
workflow checks and35exact wholefont/oneUndo/Redo/reopen checks; switched/closed
Apply safety30 and actualClose5 pass. Complete combined35gate passes280workflow,
85preservation/history,82safety,32writer controls,7realexport-dialog checks and
Close35/35. Ten composite notes are separate information, never assertions.
All93exercisedsource/dependency hashes match; all56App sources matchinstalledwheel.

App419source/60ownedbatch tests pass; installedwheel115 andinstalledsdist115pass
with pytest sourcepath disabled. Scriptmix216tests pass againstthe actualfinal
wheel, withall35source/destination hashes. Both distributionsretain licenses,
NOTICE andprivatepath/scratch exclusions. Five native UI screenshots and final
plain-language invalid-cell feedback inspected; controls/counts/actions visible.

Richer native testing found a host save/reopen domain mismatch: signed32 endpoints
persist in memory/history but load clamps beyond2UPM and addsmark1 (fl#8522).
Final writer refuses a lossy finalbatch before anyhistory/write, neverclamps.
Native controls prove inclusive +/-2UPM persistence, oneunitoutside refusal,
existing/newzero, nonzero->zero, glyph/class/bothclass zeros, staleclass/pairs,
fractionalhistory onuntouchedmaster and exact fullfont preservation. Known extra
no-op history row remains permitted underD18; oneUndo restores allfontdata.

Controller commands use rtk proxy: installed PYTHONPATH scratch roots and pytest
-o pythonpath= over seven helpertest files (115passed,exit0,0.31s each); Scriptmix
explicit SCRIPTMIX_APP_REQUIREMENT currentwheel test.sh --original-source-root
workspace (216passed,exit0,0.27s). Exact native argv/exit0 and previous failures
are retained privately in issue111-tools35-v1, kerning-edit-v1 and
kerning-preflight-v2/v3/v4.
No owner-site install, original input removal or Fontport contract change.
Full130-stem/archive migration, additional tools/reporters/docs remain open.

## Issue111 Task3i selected Kerning editors — source milestone

Exceptions Finder retains all-master/current scope, first broader class-pair
precedence, redundant/manual checkboxes, Untick all and Remove ticked. Pairs From
Text retains word/slash-token parsing, reading-order unique adjacency, effective
versus explicit previews, manual checkboxes and Add/Set for selected masters.
Shared lazy App0.2.9 plans reuse the complete snapshot-bound writer and owned
panel. No new dependency or Fontport change. Complete-master final range,
zero/absence, fractional-history and stale guards stay centralized. Read errors
propagate instead of being shown as an absent zero.

Tests first: two missing tools RED with216existing passes (exit1). Eight new App
checks cover precedence/zero/manual deletions, parsing and native effective reads,
Add/Set, empty selection/no-history, late invalid preflight and honest partial
native-write failure. New real menu-method tests exercise stale font/pairs/classes/
masters, actual checkbox state through shared guarded callbacks, failed preview,
post-write read errors and inherited owned Close. One RED caught list-pair previews
surviving shared invalidation; it now clears both pair lists and value maps.
A second test setup correction used AVA (the prior AV pair was explicitly zero
and correctly bypassed effective reads) and supplies the normal subtitle control.

Final portable commands (exact private argv/receipts in workspace task-3i-report):
- App checkout: `rtk proxy .venv/bin/python -m pytest -q`: exit0,427passed13.52s.
- Scriptmix checkout: `rtk proxy env SCRIPTMIX_APP_REQUIREMENT=/path/to/current-app.whl SCRIPTMIX_APP_SOURCE=/path/to/updated-app/src/fontlabapp ./test.sh --original-source-root /path/to/workspace`: exit0,238passed0.27s.
- `rtk proxy uvx ruff check <changed Python files>`: exit0, all checks passed.
- `rtk proxy git -C <App checkout> diff --check` and the Scriptmix equivalent: exit0.
All37exact source/destination hashes pass; prior35rows/menu bytes are unchanged.
Original TITLE/KEY/MODES constants and all signal callbacks match AST comparisons.
Scriptmix README198lines, dependency/helper guidance forthcoming0.2.9, no index
publication claim. Official local pyflpackage.cpp833/838 declarations and existing
scripting native get semantics were inspected; no new Qt API was introduced.

Wait, but: host doubles prove source contracts only. Installed native original
scenarios, seeded Exceptions baseline, full-font deltas, one native Undo/Redo,
saved reopening, safety, real controls/screenshots and native Close are controller
acceptance work and remain unchecked. Full130stems/othercollections/archive
cleanup, additional tools/reporters/docs stay active. No native calls, owner
installs, archive writes, agents, commits or pushes occurred in this task.

## Task3i review fix1 — completed writes and shared tables

P2: the shared seven-editor Apply boundary now retains a known successful write
across every later exception, including UpdateAll, post-write tick collection and
refresh. The message reports that kerning was applied, keeps the original cause
and offers Undo/Refresh. It resets the write marker before preflight so an earlier
success cannot relabel a new refusal; partial-writer diagnostics stay unchanged.
Staging/results clear and Apply disables before the guarded callback reports it.
P3: both selected editors reuse the existing shared table builder; exact headers,
manual checkbox callbacks and Exceptions240minimum remain. Prior35menus unchanged.

Tests first: five genuine failure-injection REDs through actual inherited guarded
callbacks, with two preflight/partial-error controls passing. The seven focused
cases then pass after the shared fix. Original26frozenfiles and initial report
were verified and copied to the workspace task-3i-before-fix1 directory before
edits. Native/artifact reacceptance stays controller-owned; full results and
snapshot delta are retained in task-3i-report/fix1-freeze. No native call, owner
install, archive edit, commit or push occurred.

Fix1 final direct verification uses the same portable full-suite commands above:
App427passed13.82s, Scriptmix245passed0.34s with all37provenance hashes; changed
Python Ruff and both diff checks exit0. Seven new guarded-callback controls pass;
original constants/callbacks and prior35mapping/menu bytes remain unchanged.
Native acceptance of these changed bytes remains pending controller rerun.

## Controller Task3i acceptance

Source/fix1 reviews SPEC PASS/QUALITY APPROVED. Installed final wheel native
combined37 gate:301original workflow checks,99complete preservation/history,
94safety (12FontInfo+32Names+8classes+42editor staleApply),32writer controls,
12post-write failure controls,15realchooser/export checks andClose37/37pass.
96source/dependency hashes match;importsrestored,ownedfontsclosed. Both selected
editors retain originalnativeoracles and14exactfullfont/firstUndo/Redo/reopen
checks. Owned UpdateAll failure injection proves honest completed outcome and
exactUndo/Redo;nativefunctionrestored in finally. Earlier chooser timeout retained
in tools37-v1, boundedcalls pass in tools37-v2, no waivedoracles.

App427source/123installedwheel/123installedsdist tests andScriptmix245against
actualwheel withno sourceoverride pass;37provenance hashes pass.57App sourcefiles
match both artifacts;licenses/NOTICE/privacy checks pass. Exact rtk proxy argv,
exitcodes,freezes/reviews andsnapshots retained in issue111-tools37-v2 and
kerning-remaining-fix1-v1 workspaceevidence. Bothnative tickedscreenshots checked.
Full130stems/othercollections/archivecleanup/newtools/reporters/docs stayactive.
No owner-siteinstall ororiginalinput removal. Controller prepares D12/D17 release.

## Task3j — four Proof tools, source milestone

Glyph Grid, Text By Master, Waterfall and Word Finder retain all original
controls, defaults, classes, keys, registry entries and scenario-accessed globals.
App shares actual transformed outline assembly, advance-only text, exact original
English/Latin words and filters, three native painters, scroll/footer composition,
complete-scan guards and existing owned dialog lifecycle. Grid fits one scale to
all full bounds; deliberate Reload adopts current font/selection. Automatic
refresh/paint/Copy refuses switched/closed fonts before cached-wrapper access.
Paint create/draw/hook/end errors clear incomplete results; inactive devices and
false end() results are diagnosed. Copy is host-free tested only (D8).

Tests first: App baseline427pass14.11s; Scriptmix baseline245pass0.28s.
Four missing menus produce RED4fail/245pass; later inactive-painter/false-end
controls produce RED2fail/282deselected before their minimum guard fix.
Final direct source verification, all exit0:
- App cwd: `rtk proxy ./test.sh`:441passed13.92s (14new shared-helper cases).
- Scriptmix cwd: `rtk proxy env SCRIPTMIX_APP_REQUIREMENT=../.local/issue111-app-v0.2.9-dist/fontlab_fontlabapp-0.2.9-py3-none-any.whl SCRIPTMIX_APP_SOURCE=../.worktrees/issue111-app/src/fontlabapp ./test.sh --original-source-root ..`:284passed0.32s (245baseline +39new).
- Workspace cwd: `rtk proxy uvx ruff check .worktrees/issue111-app/src/fontlabapp/proof.py .worktrees/issue111-app/src/fontlabapp/_proof_views.py .worktrees/issue111-app/src/fontlabapp/_proof_dialog.py .worktrees/issue111-app/tests/test_proof.py fontlab-python-scriptmix/Scripts/Proof fontlab-python-scriptmix/tests/test_proof.py fontlab-python-scriptmix/tests/conftest.py fontlab-python-scriptmix/tests/test_reports.py fontlab-python-scriptmix/tests/test_portability.py`:allchecks passed.
- Workspace cwd: `rtk proxy git -C fontlab-python-scriptmix diff --check` and
  `rtk proxy git -C .worktrees/issue111-app diff --check`:exit0 each.
All41provenance hashes pass; prior37rows/menu bytes unchanged. Original signal
connection expressions are AST-identical; strict audit checks exact original
constants/embedded words. README197lines; helpers require forthcoming App0.2.10
or explicit current source override/current built wheel; no index claim.

Attempts retained: initial focused run36pass/1test-double failure (base Widget.text
was mistaken for a text control), corrected by checking setText; next focused
42pass/1opening-failure fixture failure (default text had no encoded characters,
so injected findName was never reached), corrected to inject glyph_run. First
App test launch from workspace root failed because no root test.sh exists; one
later edit/format/wc batch used Scriptmix cwd with workspace-relative paths and
failed before writes, then ran correctly from workspace. Initial Ruff failures
were native-boundary BLE001 comments, unused descender/import sorting/export
annotations; all corrected. lean-ctx binary and rules file are absent; rtk proxy
was used. No failing product behavior is being waived.

Wait, but: owned doubles and external Qt mathematical paths prove source
contracts only. Source review, built wheel/sdist/license/privacy/byte audits,
unchanged native original scenarios and exact path bounds, real screenshots and
controls, complete saved-font/history invariance, stale/read/paint safety and
actual native Close remain controller gates. No native runs, owner installs,
canonical App edits, commits/pushes, archive writes/removal or child agents.
Full130stems/othercollections/cleanup/reporters/docs remain open. Detailed exact
commands and all changed/untracked hashes are in the workspace Task3j report
and freeze; no source promotion is authorized by host doubles alone.

## Task3j fix1 — R1 initial native-read containment

The independent review correctly found that earlier initial_refresh covered
late proof scans only: package/current/id, selection/maps/characters and master
reads could escape before a closable panel existed. All29frozen files and the
original report/freeze were hash-verified and snapshotted before edits under the
workspace task-3j-before-fix1 directory; original task-3j-freeze.json is unchanged.

Proof constructors now build safe empty state and complete status/Close/controls
before any font read. The existing snapshot wrapper includes the whole initial
source load: bind current/id, read per-tool state, recheck identity, then scan.
Failed early reads discard incomplete caches, leave an invalid empty diagnosed
panel and preserve any known bound id for guarded retry. A binding failure before
an id is obtained has no identity to retain. Grid explicit Reload intentionally
resets initial binding so it can adopt current font/selection or no font.
Waterfall publishes original master choices/active-master default with signals
blocked and previous block state restored in finally; no signal recursion or
native active-master change is introduced. Defaults, aliases, every original
_connect expression, prior37menu bytes/mapping rows and native oracles remain.

Tests first: actual constructor/main RED15fail/284deselected0.31s, covering
current-package and id for allfourtools plus selection/maps/characters/master
list/active-master errors. Each injected read asserts that Close/status already
exist. Those15then pass with guarded retry, registry publication and Close.
Four additional cases close directly while the initial read still fails; four
prove automatic retry refuses a different known font while Grid Reload can
explicitly adopt it. Focused final23pass/284deselected0.09s.

Fresh full source checks, exit0 each:
- App cwd `rtk proxy ./test.sh`:441passed13.61s.
- Scriptmix cwd `rtk proxy env SCRIPTMIX_APP_REQUIREMENT=../.local/issue111-app-v0.2.9-dist/fontlab_fontlabapp-0.2.9-py3-none-any.whl SCRIPTMIX_APP_SOURCE=../.worktrees/issue111-app/src/fontlabapp ./test.sh --original-source-root ..`:307passed0.43s (284old +23new).
- Workspace cwd `rtk proxy uvx ruff check .worktrees/issue111-app/src/fontlabapp/proof.py .worktrees/issue111-app/src/fontlabapp/_proof_views.py .worktrees/issue111-app/src/fontlabapp/_proof_dialog.py .worktrees/issue111-app/tests/test_proof.py fontlab-python-scriptmix/Scripts/Proof fontlab-python-scriptmix/tests/test_proof.py fontlab-python-scriptmix/tests/conftest.py fontlab-python-scriptmix/tests/test_reports.py fontlab-python-scriptmix/tests/test_portability.py`:allchecks passed.
- `rtk proxy git -C fontlab-python-scriptmix diff --check` and
  `rtk proxy git -C .worktrees/issue111-app diff --check`:exit0 each.
All41mapping pairs pass strict originals audit; prior37rows/menu bytes unchanged;
allfour original signal action expressions remain AST-identical. Initial lint
flagged the new test-only class tracking list (RUF012); ClassVar annotation and
proper docstring placement corrected it before final lint. No product failures
waived. New fix1 freeze records every file/status/hash and explicit old/new delta.

Wait, but: these results prove the bounded source fix only. Parent reported that
pre-fix native four-tool originals/full-font/stale/paint/Close checks passed,
and that a broader41tool run later hit an unrelated chooser deadline. Neither
is native evidence for these changed bytes. Parent owns scoped review, rebuilt
artifacts and native reacceptance. No native calls, commits/pushes, owner installs,
archive writes/removal, canonical App edits, Fontport/Glyport changes or agents.
Full Issue111 remains active; no native/promotion TODO is ticked by this fix.

## Controller Task3j acceptance

Source/fix1 reviews SPEC PASS/QUALITY APPROVED. Final installed-wheel core41
gate passes336original workflow checks,107complete preservation/history,123safety
(94prior+29Proof),32writer/12postwrite/12paint/24opening errorcontrols andClose41/41.
All103exercised source/dependency hashes match;importsrestored,ownedfontsclosed.
Separate fresh same-wheel realchooser/export gate15checks passes. Earlier full41
andfocusedchooser calls hit5s native deadline; splitting launch/mode/open into
separate bounded calls retains everyoracle andpasses. Thosefailures remainretained.

Proof4 originaloracles pass35checks,8strictcompletefont/workspace/history,29stale/
explicitReload,12realpaintfail/recovery and24nativeearlyopening controls. Native
function injections alwaysrestore functions/aliases; eight diagnosedinvalidvisible
panels close with actualQObjectdestruction/registryrelease andfont/historyexact.
All15Gridcells, transformedAacute, fullampersandlastrow, textweights/widths and
missingglyphboxes visuallyinspected. Clipboard remainsnative-excludedD8.

App441source/137installedwheel/137installedsdist tests andScriptmix307against
actualwheel withno sourceoverride pass;41provenance hashes pass.60Appsourcefiles
matchboth artifacts/installs;licenses/NOTICE/privacy audits pass. Exactrtkproxy
commands/exitcodes/freezes/reviews in tools41-v2, proof-fix1-v1 andproof-choosers-v2
workspaceevidence. Full130stems/othercollections/archivecleanup/newtools/reporters/
docs stayactive; no originalremoved orowner-siteinstall. ControllerpreparesD12/D17.

## Task3k: seven complete Names editors — source-only handoff

Bases: App541a399c4155c057e286b60af6b9bd992386a643 / Scriptmix
2b1ad7599862631a13a536c57a5c26ecc73ffe5e. All work stays in the existing App
issue111 worktree and Scriptmix feature branch; no canonical App edits or native
calls. Seven original Names editors retain every control/default, KEY/class,
scenario-facing method/alias, original auto-layer rename refusal/warning and
34_connect expressions (loops retain their original connections). The shared
Names shell/table/signals/Close helpers are reused through lazy fly.ap; pure
plans, complete snapshots and bounded native writes are shared in App0.2.11
helpers. No new dependency or Fontport/Glyport contract is introduced.

Safe empty status/Close/control construction precedes the complete initial font,
identity, selection, names, master and component scans. Explicit original Reload/
Rescan actions may rebind. Ordinary callbacks retain the original identity and
refuse closed/switched fonts before cached-wrapper access. Snapshots bind all
names/masters/selection/classes, relevant complete values, layer roles/component refs
and note/mark layer values. Notes bind the current editor and displayed entries;
a newly seeded previously undisplayed note remains allowed, matching the original
S-note scenario. A note-list double-click updates the baseline after its explicit
selection change. Rename refresh updates auto links before planning.

The entire batch preflights before checkpointing or writes. Empty/no-op/refused
plans add no history. The existing before/after non-auto layer/glyph list is
retained, adding plain component dependants for rename history. Native tags are
QSet values, so snapshots canonicalize them and readback compares sets. Partial
writes retain confirmed names/native cause and Undo guidance; completed writes
retain their outcome across UpdateAll/scan failures or a post-write font switch.
No native persistence/history claim follows from these owned host doubles.

Baseline, fresh evidence and exact commands (all `rtk proxy`):
- App cwd `.worktrees/issue111-app`, `./test.sh`:441passed13.68s exit0.
- Scriptmix cwd, `env SCRIPTMIX_APP_REQUIREMENT=../.local/issue111-app-v0.2.10-dist/fontlab_fontlabapp-0.2.10-py3-none-any.whl ./test.sh`:307passed0.37s exit0.
- RED: same Scriptmix requirement, `./test.sh tests/test_names_editors.py`:7failed/307passed0.34s exit1; all seven requested menu files absent.
- App RED `./test.sh tests/test_names_batch.py`:collection error exit2 before helper existed; initial from-import fell through App's native alias resolver. Switched the test to explicit import_module, then implemented the helper.
- Interim App `./test.sh` before class/signal self-review:480passed13.99s exit0 (441prior+39new).
- Interim Scriptmix `env SCRIPTMIX_APP_REQUIREMENT=../.local/issue111-app-v0.2.10-dist/fontlab_fontlabapp-0.2.10-py3-none-any.whl SCRIPTMIX_APP_SOURCE=../.worktrees/issue111-app/src/fontlabapp ./test.sh --original-source-root ..`:490passed0.76s exit0 (307prior+182Names+1portability).
- Interim plain portable run with the same explicit wheel/source override but no originals option:490passed, exit0 (elapsed in handoff report).
- Workspace scoped `uvx ruff check` and `uvx ruff format --check` over all18changed/new Python files:exit0, allchecks passed/18already formatted.
- `git -C fontlab-python-scriptmix diff --check` and `git -C .worktrees/issue111-app diff --check`:exit0 each.
- 48strict source/destination mappings pass; previous41rows/menu hashes unchanged.
  All7original signal AST expression lists match. Scriptmix README199lines.

Failure attempts retained in task-3k-report.md: initial source lookup used the
collection root instead of samples/; a later patch command used Scriptmix cwd
for workspace-relative paths and changed nothing before correction. Intermediate
new tests caught the note explicit-selection baseline and a test that incorrectly
treated Duplicate's explicit Rescan as automatic refresh; fixed product/test
respectively, no oracle waived. Initial Ruff flagged reexports/imports/blanket
native catches/test-only unused bindings; corrected with explicit exports,
intentional boundary annotations and scoped fixes. README length assertions206,
then200failed until useful content was compacted to199. Final checks pass.

Wait, but: source doubles cannot prove native firstUndo/Redo, component persistence,
full-font deltas or actual native dialog destruction. Parent owns independent
review, artifacts/privacy/license checks, unchanged original native oracles,
post-seed baselines, full saved-font/history/Close gates, D12/D17/R053 and releases.
All seven native acceptance/review tasks stay unchecked. No owner-site install,
commit/push/tag, archive write/removal, clipboard/preferences mutation, native call
or agent delegation occurred. Full130stems/othercollections/archive cleanup/
additional tools/reporters/docs/finalreview remain open. Freeze/report live in
workspace `.superpowers/sdd/issue-111/task-3k-{freeze.json,report.md}`.

Final self-review also addressed explicit class-change staleness: App RED
`rtk proxy ./test.sh tests/test_names_batch.py -k classes` failed1/39deselected
(0.03s,exit1), then complete all-master group memberships/modes were bound using
the existing native groups API. Three further RED population tests failed
3/497deselected0.10s (exit1) because original tree/table/combo code left signals
blocked on rendering errors. The shared standard-library context manager now
restores each widget's previous signal-block state in finally; allthree recover.
Original controls/actions/signals stay intact. These are additional recorded
failures, not native proof or waived oracles.

Final frozen-byte source verification, exit0 each:
- App cwd `rtk proxy ./test.sh`:481passed13.95s (441prior+40new).
- Scriptmix cwd `rtk proxy env SCRIPTMIX_APP_REQUIREMENT=../.local/issue111-app-v0.2.10-dist/fontlab_fontlabapp-0.2.10-py3-none-any.whl SCRIPTMIX_APP_SOURCE=../.worktrees/issue111-app/src/fontlabapp ./test.sh --original-source-root ..`:500passed0.82s (307prior+192Names+1portability).
- Same explicit wheel/source command without originals option:500passed0.67s.
- Scoped Ruff check/format-check:18files pass/alreadyformatted; both nested Git
  diff checks and `rtk proxy sh -n fontlab-python-scriptmix/test.sh` pass.
48 mappings, previous41rows/menu hashes and all7original signal-expression lists
pass. Scriptmix README199lines. Native/installed/review/release tasks remain open.
