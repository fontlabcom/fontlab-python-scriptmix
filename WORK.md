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
