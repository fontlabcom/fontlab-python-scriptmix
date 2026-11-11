---
this_file: WORK.md
---

## C7 inspector menus — current round

Added workflows #16 and #18 with lazy direct App/Fontport imports and capture-once
fake-font dispatch tests. Catalogue changes append two rows; existing historical
hash oracles stay unchanged. Baseline focused cohort: 71 passed, one retained
skip. Changed focused cohort: 81 passed, one retained skip; new scripts each
100% statements and branches. Added four paired real-composition menu tests;
menu/composition/public-docstring cohort: 15 passed. Pinned Ruff 0.14.10 is clean.
Controller full Scriptmix gate: 4,631 passed, two retained skips. Independent
review found no remaining source blocker. Generated documentation retains only
the two new pages and index additions; immutable links await a containing commit. Native and ordinary artifact checks remain in TODO.

## WP08 current lane

Candidate launchers and retirement evidence are present; original menus and
frozen provenance remain intact. Full acceptance is blocked and old-menu
removal has not begun. Exact commands, coverage and failed inventory gates are
retained in the lane WP08-REPORT.md and .wp08-evidence/gates/; no tests were
weakened or skipped. The orchestrator owns integration and the WP01 fix.

# Work in progress

## Lane C6 — workflow 6 Interpolation Preview

Implemented the owned, read-only two-master designspace preview and both launchers.
Independent review passed, including the full-suite API-map/demo convention fixes.
Scriptmix full suite: 4,626 passed, 2 skipped. Changed-file Ruff and whitespace checks pass.
Coverage: preview 99.37% lines / 94.44% branches; sequence and both demos 100%.
Native FontLab and ordinary-artifact qualification remain open. No Git mutations,
Fontport writes or native operations. Exact commands, earlier failures and evidence
are recorded in the lane's C6-REPORT.md (App repository); the orchestrator owns delivery.

Earlier WORK.md (351,871 bytes, SHA256 `184a196981e6f26ac94f24b9f222de1fc72a39e81ebf74acbf683a103304305e`) is archived on the owner's workspace data volume (not public) under `issue250/work-archives/` (Issue 250). Completed work is in CHANGELOG.md; open work is in TODO.md and PLAN.md.


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

## Retained prior-lane WP01 evidence

## WP01 — truthful transitions (2026-11-11)

Scope: additive source accounting and historical-byte resolution only. No Scripts
bytes, immutable manifests/pins, Git refs/index, FontLab installations or native state
changed. All 271 source identities use containing commit
`4c2f6f81dabe9fe75b432fe2dfe50bfb10bf69c9`; source hashes are verified against Git,
not merely against the worktree. A shared destination is valid with distinct
(tab, optional action) identities. Every acceptance remains proposed, with false
behavior/native parity. Sixty-four targets and three proposed retirements are
future routing decisions, not an active-menu reduction.

Tests first: existing menu-layout/history suite passed 25. Added regressions then
failed as expected (18 existing passed, 1 failed, 23 setup errors for absent APIs).
After implementation the focused suite passed 78 with zero failures/skips:

```sh
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 COVERAGE_FILE=../.wp01-evidence/scriptmix-focused.coverage /Volumes/Falstaff4T/fontlab-scripting-data/issue250/venv-smx/bin/python -B -m pytest -q -p no:cacheprovider -p pytest_cov --cov=menu_layout --cov-branch --cov-report=json:../.wp01-evidence/scriptmix-focused.json tests/test_menu_layout.py tests/test_migration_history_sources.py tests/test_curated_delivery.py tests/test_components.py::test_released49_rejects_changed_menu_bytes tests/test_inspectors.py::test_released45_fixed_manifest_rejects_changed_menu_bytes
/opt/homebrew/bin/ruff check --no-cache menu_layout.py tests/test_menu_layout.py tests/_migration_history.py tests/test_curated_delivery.py tests/test_migration_history_sources.py
```

Complete production module `menu_layout.py`: 176/182 statements (96.70%),
95/102 branches (93.14%); no exclusions. Ruff clean. Existing three lambda
assignments in the changed menu-layout test became equivalent local functions to
meet the changed-file Ruff rule; no oracle was weakened. The controller owns the
full exact gates and independent review evidence. Initial `uvx` attempts failed
on prohibited default tool-cache writes and unavailable isolated offline metadata;
the installed Ruff binary supplied the focused lint check.

Archive decision: `pyproject.toml` declares a scripts-only installation, no runtime
package (`packages=[]`, uv `package=false`). Existing `rescue-index.json` tracks
private historical input bodies, not the reviewed current menu payloads; generated
`.build/menu-sources` is not a durable archive. Reuse the existing external
preserved-source approach with an explicit `FONTLAB_MENU_ARCHIVE` directory of
`<full-sha256>.bin` data. No corpus or archive payload is shipped by WP01. Future
packaging must audit/provision this archive before removing menus in Git-less
installs. `source_bytes` and `released_bytes` verify every recovered payload and
never execute it. `consolidation_rows` additionally certifies the full inventory
against Git and refuses certification when Git is unavailable; a single recovered
historical payload does not imply inventory, implementation or native acceptance.

Open: controller full gates/review, later source-route parity, genuine archive
packaging and real FontLab PythonQt acceptance. No commits or source removals.

Full-suite feedback retained two legacy corruption-oracle failures: new bare-menu
hash validation raised ValueError before the old callers could assert their
historical error contract. Scoped that new refusal to explicit consolidation
ledgers; no-ledger raw-byte behavior remains unchanged. Both original tests are
unchanged and pass in the final focused 78-case run. The controller repeats the
full suite after this fix.

### Final complete prepared suite

From the WP01 lane root:

```sh
sh .wp01-gates/prepared-suite.sh fontlab-python-scriptmix final-rerun
```

Result: **4,662 passed, two existing skips, zero failures**, 95.23 seconds. The
unchanged repository `repos.sh` `run_suite` arguments ran through prepared
environment provisioning. Evidence is in
`.wp01-gates/fontlab-python-scriptmix-final-rerun/suite.log` at the lane root.
Full `menu_layout.py` coverage: 178/182 statements (97.80%), 97/102 branches
(95.10%), zero exclusions. Changed historical test helper coverage is 34/34
statements (100%) and 7/8 branches (87.50%). The gate owner restored 270 generated
catalogue pages after verifying unchanged Scripts bytes; these generated changes
are not delivered as WP01 source-link edits. Independent review approved the
implementation and the preserved legacy corruption-oracle contract.

The canonical `quality.sh coverage` wrapper was **not run**: it hardcodes writes
to evidence/cache locations outside this lane. The full prepared suite is an
explicit provisioning equivalent, not a canonical G-Scriptmix pass. The gate
also built and installed an App wheel into lane-local test storage; no FontLab
installation changed. Canonical wrapper qualification remains a controller task.
Native/live acceptance, future archive packaging and later tool-route parity
remain open. No test was weakened, skipped or removed to obtain this result.
