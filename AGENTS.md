---
this_file: AGENTS.md
---

## Current scope — 2026-11-05

Issue 230 documentation reconciliation is current. Issue 123 remains paused. The qualified Issue 207 isolated candidate is separate from canonical source, installed artifacts, native acceptance and publication. Reconcile that candidate with later work before integration. Issue 210 specifies future architecture; Issue 211 retains unfinished follow-up checks. Retained dated receipts describe their original source and acceptance surface only.

Canonical source inspected for this proposal: `852976b71613`. This is a dated source observation, not an installed or native acceptance claim.

Retain current Issue 208/M12 user tools and frozen provenance while reconciling Issue 207 cleanup and current App APIs.

Qualify the complete original tool denominator and owned native/history/lifetime checks; distinguish the 350-script classified offline smoke from actual native acceptance.

## Organization and checks

`Scripts/` contains user actions; `tests/` checks source contracts/provenance; `docs/` and `src_docs/` hold documentation; `tests_docs/` checks its build. Frozen manifests identify original source pairs.

Use README prepared arm64 Python 3.11 runtime-cohort recipe, or set `SCRIPTMIX_APP_REQUIREMENT` to a reviewed App wheel/checkout before `sh test.sh`. Add matching peers with `SCRIPTMIX_EXTRA_REQUIREMENTS`. Run `tests_docs` separately with pytest, mkdocs-codeinclude-plugin 0.3.1 and PyYAML.

# Scriptmix rules

Practical FontLab tools; menu scripts call shared App helpers through Fly.

- Target Python 3.11 arm64. Use `--python cpython-3.11-macos-aarch64-none`;
  plain `3.11` can select Intel Python on this Mac. Keep imports lazy.
- Use canonical App domain paths such as `fly.ap.core.scripting` and
  `fly.ap.masters.inspect.model`. The migration oracle is App's `_legacy.ALIASES`.
- `Scripts/<Title Case Category>/<Tool>.py` is the only menu depth FontLab accepts.
- General UI and shared native helpers belong in `fontlabapp`. Fontport holds
  fontParts/UFO code only; Glyport holds Glyphs.app code only. Use `fly.ap`
  for App and `fly.fp.feature_blocks` for feature source. Never load a sibling
  script as a runtime library.
- Test prerequisites and the complete environment exports are in README.
  Use a prepared arm64 3.11 test `.venv`, with pytest, installed matching App
  and Fontport packages, and App test dependencies. Only Fly uses a sibling
  source path; leave App/Fontport source overrides unset. Do not replace the
  documentation `.venv` (Python 3.12 or later).

```sh
VIRTUAL_ENV="$SCRIPTMIX_TEST_VENV" uv run --active --no-project \
  --python cpython-3.11-macos-aarch64-none \
  python -B -m pytest -q -p no:cacheprovider tests
uv run --no-project --python cpython-3.11-macos-aarch64-none \
  --with pytest --with mkdocs-codeinclude-plugin==0.3.1 --with PyYAML \
  python -B -m pytest -q -p no:cacheprovider tests_docs
uv run --no-project --python cpython-3.11-macos-aarch64-none \
  --with ruff==0.14.10 ruff check --no-cache --target-version py311 \
  Scripts tests tests_docs menu_layout.py src_docs/build.py
```

Ruff 0.14.10 reports 87 existing findings in this scope. Do not apply automatic
fixes to historical scripts. Export an external `UV_CACHE_DIR` as in README.

`migration.json` is a frozen v0.2.0 record, not current pins.

## Host limits

- PythonQt widgets live in `QtGui`, not `QtWidgets`. Do not create QApplication,
  start an application event loop or load a second Qt binding inside FontLab.
- Disconnect owned signals and stop timers before widget destruction. Wrap
  native slots in plain functions; mixed native/bound-method disconnect can
  crash. End every active painter in `finally`; contain paint exceptions.
- Native wrappers can lose Python subclass state. Keep table state separately;
  do not add attributes to native widget instances. Call protected native
  event handlers through the explicit native class.
- Never notify automatic layers. Never call `UpdateAll` or clear the process
  glyph-update queue. Retain the shared guards for automatic dependants;
  disclose pending updates and their possible date changes (issue 8537). An Undo notification needs the layers and glyph together.
- Use the shared font-id helper for fontpr: its font_id is FontGate fgId,
  not the package object's id. Selection writes require an active Font window.
- Avoid `flGlyph.fgGlyph` in metadata scans: it can erase the note mirror.
  Clone operations can lose raw node flags, shape notes and corner smoothing;
  use shared repaired-copy helpers. Keep the changing-anchor-to-origin refusal.
- Deferred host work survives a client timeout. Enforce deadlines in host work.
  Native tests need a dedicated document-free session and owned fonts/widgets.

Offline tests, stubs and standalone Qt runs are not native proof. Verify the
exact loaded App/menu files inside FontLab. Check complete font state, actual
Undo/Redo, saved/reopened files, stale-font refusal, painting and Close. Existing
release receipts do not qualify changed tools or a new dependency combination.

Work only in this worktree. Keep canonical checkouts, owner files and FontLab
site-packages untouched; editable installs are owner-managed. Use read-only
`GIT_OPTIONAL_LOCKS=0 /opt/homebrew/bin/git --no-optional-locks` for inspection.
No branch/index/tag changes, commits, cleanup or publication without a current
request. Preserve historical paths, hashes and full licence notices. Never
execute or redistribute third-party reference bodies during inspection. Use
external scratch space; never write temporary files in the repository root or
`/private/tmp`. Archive deletion requires owner confirmation.

## Milestones and delivery

Read [PLAN.md](PLAN.md), [TODO.md](TODO.md) and [WORK.md](WORK.md) before work.
Make the smallest complete MVP for one named acceptance task. Find all callers,
tests, fixtures, exports and documentation first. Use graph impact before source
symbol edits; confirm stale or unknown graph results against current source.
Keep product work in isolated successors and preserve the owner's checkout.

Run this repository's exact checks and the unchanged 80% gate for each complete
changed production module. Use an independent review before a milestone commit.
Under the current owner task, commit and push reviewed, passing milestones;
verify remote heads rather than inferring delivery from local tracking refs.
Before main integration, reconcile concurrent work and all consumers, run graph
change analysis and repeat the required acceptance on the combined source.

Before removing obsolete branches or files, prove integration, retain recoverable
unique work and check fresh owner/worktree attachments. Preserve sealed reports,
licences, archives and private data. Do not rewrite history by implication.
Remove verified completed work from PLAN/TODO and record scoped evidence in
CHANGELOG. Keep implemented-only native/artifact checks open in TODO. Issue 123
remains paused; no instruction here authorizes driving the owner's FontLab,
installing into its user folder or publishing a site.
