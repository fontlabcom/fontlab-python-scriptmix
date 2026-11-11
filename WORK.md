---
this_file: WORK.md
---

# Work in progress

Earlier WORK.md (351,871 bytes, SHA256 `184a196981e6f26ac94f24b9f222de1fc72a39e81ebf74acbf683a103304305e`) is archived on the owner's workspace data volume (not public) under `issue250/work-archives/` (Issue 250). Completed work is in CHANGELOG.md; open work is in TODO.md and PLAN.md.

Final exact Scriptmix full suite: 4,621 passed, 2 existing skips in 57.76s. Catalogue counts/hashes and minimum menu documentation checks pass. Unrelated generated source pages restored; only the two new pages and their category links retained.


## C5 current round

Workflows 11 and 14 compose existing editors/reports and owned lifecycle with fake-font tests and Scriptmix menus. Paired menu tests: 4 passed, both new scripts 100% line and branch coverage. Changed Python files pass Ruff. Native checks remain in TODO.md; the final full-suite result is recorded below.

## Current round — Issue 234 workflows 1, 4 and 5

Completed the three Scriptmix dispatches, catalogue records, source documentation
and fake-font menu tests. Verified the complete fallback runtime suite (4,635
passes, two retained optional audit skips), focused menu/report checks (90 passes,
one optional audit skip), 100% line/branch coverage per new menu and pinned Ruff.
Exact dependency provisioning was blocked by PyPI DNS in the lane; the lander's
exact recipe on the combined origin/main tree passed 4,637 with two skips. Rechecked existing source
and catalogue hash oracles; no original menu body changed. Remaining ordinary
installation, native lifetime/preservation and source-link checks are in TODO.

Retained failed attempts: exact provisioning stopped before tests at hatch-vcs
resolution (PyPI DNS). An initial prepared fallback used the mismatched canonical
pens checkout: 26 failed, 4,588 passed, two skipped, three errors; a lane-Fontport
retry still had that pens mismatch (25 failed, 4,607 passed, two skipped, three
errors). Focused attempts with those pens recorded 18 failures (47 and then 53
passes). Matching the prepared environment's read-only pens source left one
additive catalogue count failure: 4,634 passed, two skipped, one failed; its
202-to-205 correction produced the final complete passing result above. No test
was disabled and no original hash oracle changed.

## Issue 241 — demo verification

Scope: retain the existing two menu scripts and exact source catalogue records;
verify their lazy calls to `show_tmetrics()` and `show_tglyph()` against App.
No new wrappers, dependencies or menu categories are needed.

- Exact gate attempted: source the workspace `.metaswarm/repos.sh`, set
  `NAME=fontlab-python-scriptmix`, `I` to this lane, `W` to the reference
  workspace, `REPO` to this checkout, `QUALITY_PYTHON=/opt/homebrew/bin/python3.11`,
  and a writable external `UV_CACHE_DIR`; run `configure_repo; run_suite -p no:cacheprovider`.
  Blocked before collection by PyPI DNS while resolving `hatch-vcs`; the
  lander's rerun on the combined origin/main tree passed 4,617 with two skips.
- Prepared environment substitute: `PYTHONDONTWRITEBYTECODE=1
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 QT_QPA_PLATFORM=offscreen`, lane App/Fly
  `PYTHONPATH`, the recipe's preserved archive root, and the existing arm64
  Python 3.11 `venv-smx/bin/python -B -m pytest -q -p no:cacheprovider tests
  --original-source-root <reference-workspace>`: 4,617 passed, two skipped.
  Repeated after the final App changes: 4,617 passed, two skipped in 68.05 seconds.
- The same interpreter with `coverage run --branch
  --include='Scripts/Metrics/TMetrics Window.py,Scripts/Contours/TGlyph Window.py'
  -m pytest -q -p no:cacheprovider tests/test_issue241_fontui_windows.py`:
  16 passed; `coverage report -m`: each wrapper 11/11 statements, 2/2 branches.
- `ruff check --no-cache --target-version py311` on both menu scripts and
  `tests/test_issue241_fontui_windows.py`: clean (installed Ruff 0.16.7).
- Restored only the 271 generated catalogue source-link changes produced by
  the full test run to their initial bytes; source hashes remain unchanged.

Native PythonQt/FontLab behavior and ordinary installed artifacts were not tested.
