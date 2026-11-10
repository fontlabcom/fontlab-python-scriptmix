---
this_file: WORK.md
---

# Work in progress

Earlier WORK.md (351,871 bytes, SHA256 `184a196981e6f26ac94f24b9f222de1fc72a39e81ebf74acbf683a103304305e`) is archived on the owner's workspace data volume (not public) under `issue250/work-archives/` (Issue 250). Completed work is in CHANGELOG.md; open work is in TODO.md and PLAN.md.


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
