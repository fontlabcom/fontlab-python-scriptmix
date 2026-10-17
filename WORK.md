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
