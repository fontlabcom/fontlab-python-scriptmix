---
this_file: WORK.md
---

# Issue 111 first batch

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
