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

Use README prepared arm64 Python 3.11 runtime-cohort recipe, or set `SCRIPTMIX_APP_REQUIREMENT` to a reviewed App wheel/checkout before `sh test.sh`. Add matching peers with `SCRIPTMIX_EXTRA_REQUIREMENTS`. Run docs pipeline tests with the separate Python 3.13 hash lock; legacy docs checks additionally use pytest.

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
  documentation `.docs-venv` (Python 3.13).

```sh
VIRTUAL_ENV="$SCRIPTMIX_TEST_VENV" uv run --active --no-project \
  --python cpython-3.11-macos-aarch64-none \
  python -B -m pytest -q -p no:cacheprovider tests
.docs-venv/bin/python -m unittest discover -s tests_docs -p 'test_pipeline_*.py' -v
# Run legacy pytest checks separately with pytest added to a docs test environment.
uv run --no-project --python cpython-3.11-macos-aarch64-none \
  --with ruff==0.14.10 ruff check --no-cache --target-version py311 \
  Scripts tests tests_docs menu_layout.py src_docs/build.py
```

Ruff 0.14.10 reports 26 existing findings in this scope (E402 17, E741 9), all in Scripts; tests, tests_docs, menu_layout.py and src_docs/build.py are clean (measured 2026-11-11, was 45). Do not apply automatic
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

## Public site qualification

Retain all 259 practical tools, the 350 classified source rows and the historical 68-of-130 native boundary. Source identity links and hashes must remain exact. Keep authored retained guides outside generated `docs/`. Follow README for the current exact-lock build. Independent source/privacy/legal review, actual main CI, immutable generated-output verification, settings readback and live browser checks remain required. The current 31-package/44-asset inventory is scoped evidence; the complete transitive browser licence review remains open.

## Integration rounds

After each round of important changes, integrate it into `main` and upstream:
fetch `origin/main`, build the change on top of it in an isolated branch or
worktree, and resolve conflicts by keeping both our work and teammates' work.
Never discard upstream commits, and never force-push. Run the repository's
checks on the merged result, then push to `origin main`. Record the change in
CHANGELOG.md, move verified-solved TODO.md items into CHANGELOG.md, update
PLAN.md, and continue with the next TODO.md item until the list is clear.
`install.vfpy` is shared: keep it byte-identical in every installer repository.


## Verified rounds, upstream main and continuing work

After each important implementation round, independently review and verify the complete affected scope. Reconcile the exact reviewed changes with fresh upstream `main` and concurrent team work in an isolated successor, then integrate and push the qualified milestone to upstream `main`. Preserve owner checkouts, indexes, refs and unrelated changes. Resolve conflicts from the common base while keeping both sides' valid intent; never overwrite teammate work or rewrite shared history. Re-run affected regression tests, whole-module coverage and required complete checks on the combined source before delivery.

Keep required graph and installed pre-push gates active. Invoke a package-specific gate in its qualified package context; never bypass hooks with an API ref update, `--no-verify` or force push. Verify the resulting upstream SHA and required CI for that exact commit. A main build does not authorize held private Pages deployment. Use linked pull requests where the upstream contribution policy requires them.

Move only verified solved TODO items into cumulative CHANGELOG evidence, update PLAN to the remaining work, and continue the next actionable TODO until the in-scope backlog is verified clear. Preserve unsolved requirements and history when reconciling both sides. Keep partially verified, native, artifact, ordinary-installation, history and reopen obligations explicit; source acceptance is not full workflow or whole-goal acceptance. Carry this guidance into every allowed AGENTS.md used subsequently. Exclusions, explicit pauses, native-lane and owner-installation restrictions remain in force.

## Agent workflow (Issue 250, 2026-11-10)

- Plan with `superpowers:subagent-driven-development`: one fresh implementer per task, a separate read-only reviewer, then the controller runs the gates and commits.
- Send bulk, well-specified work to Codex via the `codex-delegate` skill (`node ~/.agents/skills/codex-delegate/scripts/relay.mjs --brief BRIEF --cd WORKTREE`, in the background). Use `claude-delegate` or `cursor-delegate` for second opinions or independent lanes. Delegates never commit, push or tag.
- Work in a fresh worktree of `origin/main` on the workspace data volume; never pull, switch or reset the owner checkout. Merge `origin/main` again before pushing, keep both sides' CHANGELOG/PLAN/TODO entries, rerun the full suite, lint and graph change analysis, push through the pre-push hook where one is installed (never force), verify the remote SHA and the CI run where a workflow is configured. Held private Pages operations (workspace D41) stay held.
- Release: tag the next semver above the latest tag and publish a GitHub release. Install released, gated packages into `~/Library/Application Support/FontLab/FontLab 9/` and test live in FontLab 9. This owner route (Issue 250) supersedes, for released packages only, every older line in this guide that forbids installing into the FontLab user folder or its site-packages, owner-managed editable installs, or starting FontLab for a live test (the owner's canonical editable checkouts themselves stay owner-managed): record the previous installed distribution first so it can be restored, and never touch FontLab preferences (owner fonts and documents: see live font editing below); native work goes through the workspace `verification/issue-104/fl-native.sh` gate.
- Documents: CHANGELOG holds verified completed work; TODO only open or to-verify items; PLAN the major remaining changes; WORK.md the current round only (older WORK bytes are archived on the owner's workspace data volume, not public).
- Native defects: issues at github.com/fontlab/fl; fixes as pull requests to fontlab/Proteus, fontlab/FontGate or fontlab/pyfontgate. Never commit to the local C++ snapshot.
- Older "work directly" or "no delegation" lines in this guide are superseded by this section (Issue 250).
- Live font editing (owner, 2026-11-10; workspace D44): test, verify and edit the font open in FontLab 9, and do not stop because the owner might be working in it. Open a VFJ from `~/Desktop` first (those files are for agents), then add glyphs, kerning pairs, elements, contours, masters or whatever the test needs, and save them freely. This supersedes, for live testing, every older line here that forbids mutating owner fonts or documents or requires owned fixtures only. FontLab preferences, Output folders and global update queues stay untouched. Keep the serialized host lock (`fl-native.sh`, one native run at a time; `--mutating` now allows open fonts); do not quit or restart FontLab and do not close fonts from Python, which has crashed the host.
