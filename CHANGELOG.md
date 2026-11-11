---
this_file: CHANGELOG.md
---

## 2026-11-10 — Issue 234 inspector menu compositions (#16 and #18)

Added Font UI Lab entries for UFO Roundtrip Inspector and Representation and
Notification Explorer. Both lazily capture the current borrowed Fontport font
once and return the App-owned inspector; neither imports Fly. The two catalogue
rows retain source hashes and pending native acceptance, bringing this lane to
277 menus / 208 additional tools. Merged-tree Scriptmix gate: 4,660 passed, 2 skipped; tests_docs pipeline 43 OK; graph compare against origin/main: risk low, 0 affected processes. Historical 259-script and 190-row hashes remain
unchanged. Focused menu/catalogue regression: 81 passed, one retained skip;
both new scripts reached 100% statement-plus-branch coverage. Four paired menu
cases additionally invoke the real App compositions, staging/report callbacks,
notifications and cleanup; the menu/composition/documentation cohort passed all
15 cases. The complete Scriptmix gate passed 4,631 tests with two retained skips.
Independent review found no remaining source blocker. Native FontLab and ordinary
installed-artifact acceptance remain open.

## 2026-11-10 — Issue 234 workflow 6 Interpolation Preview (C6)

Added the read-only designspace-location/two-master preview composition, paired
App demo and Scriptmix menu, fake-font dispatch/lifecycle tests and catalogue/API
entries. Reuses existing designspace controls and interpolation model/painter;
unsupported off-segment locations and incompatible outlines remain explicit.
No font writes, Fontport changes, commits or publication.

Scriptmix full suite on the merged tree (origin/main 8e4738b plus this change, with App main 9826731-era siblings that carry the C2 modules; additional tools 205 to 206, menu scripts 274 to 275, recounted from the combined tree): 4,646 passed, 2 skipped, 0 failed. The pipeline pins in tests_docs (menu count 274 to 275, site files 415 to 416) were recounted. After merging origin/main 8e4738b the tests_docs suite passes (45 tests; the two modules needing pytest were not importable in the docs venv).Graph change analysis: risk low. Changed-file Ruff passes. Preview module 98% lines (158 statements, one missed) and 54 branches; sequence 100%; both launchers reach 100% of both.
Graph change analysis (detect-changes, task-owned storage): risk low, zero affected processes, not partial. Independent source review passed. Native PythonQt rendering, whole-font/history/
cache preservation and ordinary installed artifacts remain open in PLAN/TODO.
An existing batch-recipe close/cancellation test failed in an earlier App full run
and passed the final run; its receipt and separate investigation remain open.

## 2026-11-11 — C12 tests-only Ruff cleanup

- Removed all 349 requested test findings (F811 310, F841 9, E731 20, E702 10). Explicit fixture names and aliased imports retain the same host/boundary implementations and scopes; unused assignments retain their calls, lambdas become local functions, and compound statements are split.
- Cleared 26 adjacent mechanical findings (E402 22, E741 3, E401 1) so all 30 changed test/helper files pass Ruff 0.14.10. No assertions, test identities, skip conditions or existing oracles were removed or weakened.
- Measured full-scope baseline: 45 findings (E402 33, E741 10, E701 1, F401 1; Scripts 26, tests 18, tests_docs 1, menu_layout.py and src_docs/build.py 0). README, AGENTS and PLAN agree; TODO row 106 remains open.
- Official arm64 Python 3.11 runtime gate: before and after both 4,619 passed, 2 existing skips, 0 failures. All 4,621 sorted collected node IDs are identical. Independent code review approved; 2,857 assertion ASTs retained with only intentional variable renames normalized.
- All 288 protected script/JSON hashes match. Generated documentation drift from the suite was restored; no production module changed, so production line/branch coverage is not applicable. No native acceptance or delivery is claimed. See C12-REPORT.md for commands and remaining checks.

## 2026-11-10 — Issue 234 master browser menus 1, 4 and 5

Added Open Fonts and Master Overview, Master Compatibility Browser and Node
Counts Across Masters to Font UI Lab. Each menu lazily calls the shared App
composition without importing Fly. The overview passes one borrowed FontWorld;
the other two capture CurrentFont once. Catalogue hashes and additive menu
counts now cover 274 tools; the original 259 bodies and 190 catalogue rows keep
their exact hash oracles. Existing generated pages retain their previous source
links; new pages disclose that a reviewed containing commit is still required.

Prepared arm64 Python 3.11 fallback: 4,635 passed, two retained optional audit
skips; focused menu/report checks: 90 passed, one optional audit skip. All three
complete menu modules reached 100% line and branch coverage (6 statements and
2 branches each). Ruff 0.14.10 passed all nine changed Python files. The lander
reran the exact metaswarm recipe on the combined origin/main tree (with C1):
4,637 passed, two retained skips; the three menu modules pass the coverage
gate. The docs pipeline oracles (`tests_docs/test_pipeline_*`) now pin
415 generated files, 274 menus/pages and the three new search pages; the locked
ProperDocs build and 43 pipeline units pass. Native PythonQt, ordinary artifacts
and reviewed-commit documentation links remain open.

## 2026-11-11 — Catalogue immutable links are validated (Issue 250)

`src_docs/build.py` now compares each menu's bytes with the blob committed at the link revision (`git ls-tree`, git blob id) and offers the immutable GitHub link only when they match. A dirty or untracked menu keeps its page and SHA256 but states it is not committed at that revision and gets no link. Fixture roots that are not git checkouts are unchanged. No generator framework added. New tests in `tests_docs/test_source_snapshot.py`: committed, dirty and untracked menus (11 pass; `build.py` coverage 83%). Official gate with `tests_docs/test_source_snapshot.py`: 4630 passed, 2 skipped, 0 failed. Against the real checkout all 271 committed Scripts match their blobs.

## 2026-11-10 — Issue 250 live rows 85, 87 and 90 checked

Measured against the running FontLab 9 on Desktop copies: the Font Info
ttfautohint writer is impossible per font (global export options); the Metrics
composite and base move leaves the composite unchanged and Master Metrics
capHeight reads back exactly; native anchors round to integers on every step
(all masters). The three TODO rows now state the evidence and the remaining
concrete checks. No code changed.

## 2026-11-10 — Issue 241 existing demo entry points verified

Retained the two existing TMetrics/TGlyph menu demos and their catalogue hashes.
The paired App entry points remain lazy and take their current-font defaults.
Focused menu tests passed 16 cases; each complete wrapper covers 11 statements
and both branches (100%). The prepared arm64 Python 3.11 Scriptmix environment
passed 4,617 tests with two retained skips. Ruff 0.16.7 passed on both wrappers
and their focused test. The exact metaswarm recipe later passed on the combined
origin/main tree (base 4c2f6f8): 4,617 passed, two retained skips.
Native bidirectional editing, history/reopen and current installed artifacts
remain open; no release or live acceptance is claimed.

## 2026-11-10 — Ruff baseline reconciled

The documented Ruff 0.14.10 count of 87 was stale. Re-measured with the exact guide command (py311, `Scripts tests tests_docs menu_layout.py src_docs/build.py`): 420 existing findings (F811 310, E402 55, E731 20, E741 13, E702 10, F841 9, F401 1, E701 1, E401 1; Scripts 26, tests 393, tests_docs 1, menu_layout.py and src_docs/build.py 0). AGENTS.md and README.md now state the measured figure; no script or test was changed to alter it, and no automatic fixes were applied. Per-file triage remains available via `--output-format concise`. Installed pre-push gate at landing (18936e4): 4,619 passed, 2 skipped.

## 2026-11-10 — Round Advances accepts step 1

- `Scripts/Metrics/Round Advances.py`: the step spinner now runs 1 to 100 units (was 2 to 100); the docstring and published page say so. Rounding maths is unchanged; step 2 behaviour is retained and tested alongside the new step-1 case (`test_round_advances_when_step_is_one_then_whole_unit_advances`).
- Provenance: `menu-revisions.json` records the two new exact edits and the new current hash; `additional-tools.json` and the reviewed old-rows and menus digests in `tests/test_font_ui_lab_menus.py` take the new hash (reverting only that hash reproduces the previous digest). Frozen historical hashes are untouched.
- Result: official gate 4618 passed, 2 skipped, 0 failed.


## 2026-11-10 — live font editing rule (Issue 250, D44)

- AGENTS.md: agents test and edit the font open in FontLab 9, starting from the Desktop VFJs, and may save them.

## 2026-11-10 — Batch recipe filename literal passes candidate checks

Quoted the filename template in both paired demo/menu docstrings and updated
only the new Scriptmix catalogue row's source hash. Executable script ASTs and
all old tests remain unchanged; the other 200 catalogue records are exact. The
new rendered-HTML regression reuses the existing parser and now sees the full
`<source-name>-transformed.ufo` literal, after the retained genuine-HTML RED.

Candidate checks passed: App demo three cases, Scriptmix menu three; both complete
scripts cover 7/7 statement-plus-branch obligations (100%, zero exclusions). The
complete Scriptmix suite passed 4,609 cases with the same six retained skips.
Both strict documentation builds passed, followed by App 36 and Scriptmix 43
documentation units, 14 legacy checks and pinned Ruff on the three changed Python
files. These are explicit uncommitted candidate-copy checks, not a new containing
commit or live-site result. The original public rendering failure remains open
until reviewed additive delivery, genuine-commit docs, exact CI/generated parity
and a new public browser check. Source floor eight and ordinary/native/history/
reopen qualification remain unchanged. Prior diagnosis and histories are retained.



## 2026-11-10 — Batch recipe public literal defect diagnosed

P2 source commits reached main through normal hooks and exact-commit CI; the
reviewed generated outputs match all 525 rendered files. The actual public
workbench page nevertheless hides the angle-bracket filename placeholder: its
source says `<source-name>-transformed.ufo`, while visible text loses the prefix.
A private regression using the existing HTML parser fails against genuine
committed HTML (one assertion failure, no errors/skips). The correction is pending:
quote the literal in both paired docstrings, update only the new catalogue row's
source hash and add one rendered-HTML regression. All prior source/runtime and
live failure evidence remains retained. Normal fix delivery, exact CI and a new
public check are still required; no ordinary/native or source-floor promotion.



## 2026-11-10 — P2 source/test review passed; integration gates remain

Added the actual Batch UFO Recipe Workbench menu entry and catalogue row using
the shared App composition; existing frozen catalogue oracles remain unchanged.

The independently reviewed fix closes in-flight close/nested-provider acquisition
and scheduling-failure retry defects. New real-Qt regressions cover complete
fractional reopened geometry and component conjugation across layers, font/glyph
guides and metadata/resources; connected Add/Start and captured-run stability;
active-window cancellation/isolation and the existing supervisor's actual
terminate/kill/terminal cleanup; and retained primary/cleanup errors with retry
only for unacknowledged owners. Shared helpers and worker policy are unchanged.

Final source checks passed: App 12,212 cases with no skips; Scriptmix 4,609 with
six unchanged skips; affected App 524; targeted Fontport 92; pinned Ruff on all
15 changed Python files. Complete workbench coverage is 187/202 statement-plus-
branch obligations (92.5743%); demo and menu each cover 7/7 (100%), all with zero
exclusions. Independent scoped specification/quality review passed F1–F3.
Retain the original close/reentry and queue REDs, the initial missing-shaping
runtime epoch and setup failures. The new font-guideline assertion correction
compares against independently transformed info while preserving all 107 other
info fields and the complete original test prefix.

These results close the implementation and source-test portions only. Post-change
graph, ledger/controller source qualification, genuine-commit documentation,
normal main integration and exact-commit CI remain open. No new commit, push,
ordinary installation, native result or publication is claimed. Source floor
eight, full parity zero, all 8,723 obligations and the minimum eighteen workflows
remain unchanged; ordinary artifacts/two prefixes/archives and native history,
Undo/Redo/reopen, literal U+2029, canonical adoption and private Pages holds remain
separate. Earlier history and its Scriptmix intermediate-file correction stand.


## 2026-11-10 — P1 containment round delivered; P2 remains next

The reviewed [P1 round commit](https://github.com/fontlabcom/fontlab-python-scriptmix/commit/f0e7d423c4b486bd1f9f1556e444ff155cb168fe)
reached main through the normal qualified pre-push gate (24 core passes and four
retained opt-in skips). Its [exact-commit Actions run](https://github.com/fontlabcom/fontlab-python-scriptmix/actions/runs/42803269964)
succeeded. Fontport's filesystem-identity containment fix and App regressions
resolved [issue 8624](https://github.com/Fontlab/fl/issues/8624), now closed with
[verified resolution evidence](https://github.com/Fontlab/fl/issues/8624#issuecomment-6765750168).
This completes the former P1 reproduction, source-review and main-delivery tasks;
it does not implement the P2 recipe-workbench composition.

Retained source gates are Fontport 5,076 passes plus one existing corpus skip,
271 affected App passes and 96.9231% complete batch-module combined coverage with
zero exclusions, including the unchanged covered 0.5-second startup check.
The commit-bound documentation gates passed three strict builds, 114 unit checks
and 14 legacy checks. All 524 rendered files match (App 54, Fontport 60,
Scriptmix 410). Fontport's [generated docs child](https://github.com/fontlabcom/fontlab-fontport/commit/c06b0b4d68dc11853e36e3b2e5db5daa8adae242)
is a direct child of its source commit and changes only two generated docs files.
Scriptmix's [public Pages run](https://github.com/fontlabcom/fontlab-python-scriptmix/actions/runs/42803269873)
succeeded; its unchanged 410 rendered files retain the earlier nine-route browser
proof. No new browser run or native qualification is claimed.

Correction to the earlier catalogue-intermediate shorthand: of 285 Scriptmix
Markdown intermediates, 14 match, 262 tracked files differ and nine generated
files are absent from the committed tree. The 271 differences are not all tracked
revision changes. The generator uses the last commit affecting the Scripts tree
(`git log -1 --format=%H -- Scripts`), currently
`09a09447df23d87373a8e4a3fa13381dc946d337`, not the whole source commit or a per-file
revision. The qualified publication is the 410 rendered files; this is not a
695-file parity claim or a waiver for missing generated intermediates.

P2 planning now targets actual recipe-only controls plus BatchPanel results,
with no implicit font or geometry preview. Source floor eight, full parity zero,
all 8,723 obligations and the minimum eighteen workflows remain unchanged.
Ordinary artifacts/two-prefix installation, native/history/reopen, U+2029,
archives, canonical adoption and other publication gates remain open.


## 2026-11-10 — reviewed main and documentation delivery verified

The additive [X2 source commit](https://github.com/fontlabcom/fontlab-python-scriptmix/commit/3c2ecd387ba13b7cdeaa5f8e03f82dde56fed281) passed its genuine commit-bound strict documentation build and all 42 documentation unittest cases; Scriptmix also passed all 14 legacy pytest checks. Independent source/fix and graph reviews passed before normal push. The qualified installed pre-push gate passed 24 core tests with four existing opt-in skips. [Exact-X2 CI](https://github.com/fontlabcom/fontlab-python-scriptmix/actions/runs/42783723417) succeeded, and the direct [documentation-only successor](https://github.com/fontlabcom/fontlab-python-scriptmix/commit/a8a14021a3477f8a0ad11bf19b83d96c1ab282bd) preserved all non-docs source while delivering 410 generated files byte-for-byte equal to the commit-bound build.

Across App, Fontport and Scriptmix, all 524 delivered generated files match. Scriptmix's 271 differing tracked catalogue Markdown intermediates are historical source-link revisions: the build regenerates them as inputs and commits only rendered docs. This is not a claim that all 695 Scriptmix output/intermediate files match. The public Scriptmix Font UI Lab category and all eight new menu routes passed live checks, including immutable source links and source hashes. Private App/Fontport Pages operations remain held.

This closes the recorded X2 documentation, reviewed combined-main source, normal-push and exact-commit CI tasks. Earlier candidate and failure entries remain historical evidence. Source qualification remains eight workflows, full workflow parity zero, all 8,723 obligations and the minimum eighteen-workflow scope retained. Genuine archives/distributions/two ordinary prefixes, native/history/reopen, literal paragraph-separator editing, canonical adoption and remaining publication gates are not closed by this delivery.

## 2026-11-10 — Scriptmix documentation candidate corrected

Corrected menu/page counts from 261 to 269, generated output count from 401 to 410 and added exactly nine literal search routes. All 261 original script bodies, 401 prior output paths, complete-set equality, source identities and cross-date byte checks remain. Removed only the two pre-existing unused test lines exposed by pinned lint.

The strict build and 42 pipeline unittest cases and 14 legacy pytest checks pass in owned full-history X1 copies with the admitted documentation-only overlay. Pinned Ruff 0.14.10 F/py313 passes all four changed docs test files. The earlier failures remain retained. All 42 production source hashes and their full-suite/coverage bindings remain unchanged.

The completed source-only Detached Transform Preview TODO and stale source-pending clauses for Feature Source and Proof are reconciled with independent source qualification: source floor eight, full workflow parity zero. Genuine archives/distributions/two ordinary installs, native history/lifetime/reopen, literal paragraph-separator editing and canonical/publication requirements remain open.

This closes the candidate correction only. Independent fix review, post-change graph checks, an additive X2 commit and fresh X2 commit-bound documentation checks remain before normal hooked push and exact-commit CI. Generated-output promotion, full ordinary-product/native acceptance and private publication remain separate; source floor eight and zero full workflow parity are unchanged.

## 2026-11-10 — combined main-source verification

The reconciled App, Fontport and Scriptmix source passed the complete suites:
App 12,133 tests with no skips; Fontport 5,047 with one retained corpus skip;
Scriptmix 4,606 with six retained skips. The 42 complete changed production
modules reached 89.3023–100% combined coverage with zero excluded lines.
Pinned Ruff passed all 88 scoped Python files. Paired installed Plugmix consumers
passed 100 tests; the strict installed reader/lifecycle checks passed 31.

These results qualify the recorded source-test epoch only. They do not establish
full ordinary-product or native acceptance. Independent combined review, a main
commit, normal push and exact-commit remote CI remain pending. Tracked-change
graph analysis reports CRITICAL, HIGH and LOW risks; the separate staged graph
gate for 49 new paths remains pending. Documentation builds and generated-output
lineage remain separate delivery gates. Source floor eight, ten remaining source
workflows, zero full workflow parity and all 8,723 retained obligations are
unchanged. Existing ordinary/native and private-publication holds remain.

## 2026-11-10 — qualified source carried into main reconciliation

Feature Source and Proof (#10) is independently source-qualified, including
lossless supported UFO source, ordinary code view and safe refusals. Its retained
full suites passed App 10,377, Fontport 5,017 with one existing corpus skip, and
Scriptmix 4,583 with six existing skips. Detached Transform Preview (#15) is also
independently source-qualified; its retained full App run passed 10,544 and
Scriptmix passed 4,590 with six existing skips. The common final before-model
digest is included in the qualified #15 source fixture.

The minimum source floor is eight of eighteen; ten compositions still lack source,
full workflow parity remains zero and all 8,723 obligations remain. These are
retained source-epoch results, not tests of this new main union. Combined-source
tests, independent integration review, containing commits, exact-SHA remote CI,
matching ordinary artifacts, native/history/reopen and publication gates remain
open. Full literal-U+2029 editing remains pending; safe refusal is not successful
editing. Existing history below is preserved.


## 2026-11-10 — Detached Transform Preview source candidate

Port the independently reviewed detached snapshot composition with explicit target
selection, real before/after proofs, early invalidation, reentrant target handling
and owned cleanup. Source tests and independent product review are pending; the
source floor remains seven and full parity remains unqualified. Ordinary artifacts,
native FontLab and delivery remain separate.

Reconcile current #10 status: Feature Source and Proof is source-qualified with
App 10,377 passing tests, Fontport 5,017 plus one existing GetGo corpus skip and
Scriptmix 4,583 plus six existing conditional skips. Retain ordinary code view and
safe refusals; ordinary artifacts, native PythonQt5/history/reopen and full literal
U+2029 editing remain pending. Earlier entries below retain their historical scope.


## 2026-11-09 — Current feature-source documentation

Reconcile the current feature-source overview and remaining qualification plan with the passed independent code/focused review. Focused UFO source preservation and duplicate inspection are implemented; complete source suites and ordinary/native qualification remain pending. Correct current catalogue totals to 266 tools and 197 additional rows; retain the prior 196/265 baseline references.

## 2026-11-09 — Exact feature source integration candidate

Account for the Feature Source and Proof menu in the 197 additional tools and 266 menu scripts; preserve the frozen original 190 rows and 259 script-body hashes. Source qualification remains subject to independent review and complete controlled suites; ordinary and native acceptance are separate.

## 2026-11-09 — Feature Source and Proof integration candidate

Feature Source and Proof is available through `fontlabapp.fontui.feature_proof.show(font, parent=None)`. It keeps the ordinary code view, refuses unsupported input before selection loss, and quarantines opaque document changes until explicit Revert. Accepted source Apply refreshes the independent Unicode/kerning sequence once; it does not compile or shape OpenType features. The window captures one borrowed font. External changes retain dirty drafts with a warning; explicit Apply can overwrite newer source. Refresh proof retries only the view. Original paragraph separators are inspect-only. Exact all-CR source preservation remains under investigation; this candidate is not yet source-qualified. Native PythonQt/FontLab, full literal paragraph-separator editing and broader clipboard routes remain unqualified.

The mixed-EOL draft-switch loss was reproduced before repair. The existing two feature suites pass with real guarded text controls. All 183 inherited boundary controls execute on the actual new module. The actual fresh owned offscreen product run qualifies safe and unsafe Paste through native paste, standard key and native menu, plus Enter: safe source applies once, unsafe source retains the pre-call selection, and two complete fonts are checked. The source/proof controller retains both child acknowledgements and retries cleanup without replaying source writes.

Focused failures remain retained: all-CR reader synthesis can rewrite an untouched sibling, and old current-count/fake-text view tests need finite amendments. No full suite, source acceptance, installed artifact, native FontLab, canonical promotion, commit or publication is claimed. Earlier history remains unchanged below.



## 2026-11-09 — Feature-source corruption reproduced; repair pending

Confirmed App feature-source loss in a bounded, independently reviewed real
Qt6/editor/RFont/UFO-backend run: 19 cases, nine NBSP/U+2028/U+2029 stored-source
discrepancies across no-op/edit/switch, six unexpected-write cases and 12 actual
writes in total, exit 0. Unrelated two-font data and UI teardown were preserved.
This qualifies the reproduction, not a source fix or native PythonQt5 behavior.

The chosen repair direction keeps ordinary code view with qualified safe refusals;
full literal-U+2029 editing remains pending. New separator input and refused-draft
selection switching still need a safe contract and reviewed finite repair scope.
No product fix has been applied, and #10 remains without source. All six existing
source implementations, twelve remaining in the minimum eighteen, 8,723 obligations
and the prior #9 suite evidence and separate delivery gates below remain unchanged.

## 2026-11-09 — Kerning Group Explorer finite source acceptance

Independent final review and controller verification accepted #9 source and
closed both cleanup findings. Public release fences both editors/previews and
Apply callbacks immediately, then queues cleanup until actual acknowledgements;
queued interruptions retain the original exception and owners for explicit retry.
Real editor/preview callbacks and complete two-font preservation remain covered.
Arbitrary nested Qt event loops and native painting remain unqualified.

The controlled full App suite passed 10,291 tests with 100 warnings and zero
skips/errors/failures. Full isolated Scriptmix passed 4,576 with six inherited
skips and zero errors/failures. Both exited 0. The skips retain four original-source
audits requiring their explicit source root, one external rescued-source audit
requiring opt-in, and Spacing Preview's absent selection read; none is new to #9.
Generated catalogue output remains isolated test evidence. All 21 source-bound
whole-module gates remain >=80% combined with zero exclusions; the corrected
controller retains 238/244 points (97.54%).

Six source implementations (#2, #7, #13, #12, #8 and #9) leave twelve without source
in the minimum eighteen; this does not mean six fully accepted workflows. All
8,723 obligations and the 18-or-more floor remain. Complete-source archives,
genuine matched A1 wheel/sdist/rebuilt-wheel artifacts and two ordinary prefixes
remain batched after the remaining A1 source increments. Native whole-font/history,
Undo/Redo/reopen, containing revision, canonical/owner installation, remote delivery
and publication remain separate. Earlier results, failures and wrapper provenance
limits below retain their original scope and are not retroactively changed.

## 2026-11-09 — Kerning Group Explorer callback cleanup fix candidate

Public release now fences both editors, both previews and Apply callbacks
immediately, queues one cleanup attempt and returns False until real cleanup
acknowledgements complete. The previous synchronous cleanup entry remains
private for the unwound constructor and direct failure/retry checks. Actual
standalone Kerning Apply and Sequence update callbacks retain their children
until callback return. Queued cleanup contains KeyboardInterrupt/SystemExit,
retains the same exception and owners, and waits for explicit retry after failure.

Eight new failing cases reproduced the two review findings; four terminal-signal
cases already passed. All 1,488 tests in the affected 22-file App cohort now pass,
exit 0, including the twelve new cases and prior font/error/owner/ACK oracles.
One old immediate-success assertion was explicitly adapted to queued completion;
its failed run remains evidence. Complete controller coverage is 238/244 combined
points (97.54%), with zero exclusions. The other twenty exact-source module gates
remain retained, for twenty-one total. Pinned Python 3.11 Ruff checks pass.

This is a fix candidate for independent re-review. Root's controlled frozen full
App/Scriptmix pair remains pending; no full suite was rerun here. Earlier counts
and failures below remain historical. Arbitrary nested Qt event loops and native
painting are unqualified. All 8,723 obligations, the minimum eighteen workflows,
batched A1 archives/genuine artifacts/two ordinary installs, native/history/reopen,
containing revision, canonical and publication gates remain separate.

## 2026-11-09 — Kerning Group Explorer source candidate

- Compose the existing group and kerning editors over one captured font, with
  explicit Use-left/right, draft-preserving accepted-group revalidation and
  distinct member/representative-pair previews. Existing algorithms stay intact.
- Add the real App demo and lazy Scriptmix menu. Retain all four owners through
  construction/cleanup faults; fence callbacks before cleanup and defer active
  dispatch teardown with one queued request and positive ACK retry.
- Verify 1,476 affected App tests, 87 unchanged Fontport tests and 65 finite
  isolated Scriptmix tests plus one inherited skip, all exit 0. Whole-module
  combined gates are 231/234, 9/9 and 9/9, zero exclusions; retain the prior
  eighteen exact-source gates. Current counts are 196/265/95; frozen 190/259
  and original 350 classifications are unchanged.
- Keep independent review, one controlled frozen full-suite pair and all matched
  A1 artifact/ordinary, native/history/reopen, containing-commit, canonical and
  publication gates pending. No release floor or native acceptance is asserted.

## 2026-11-09 — Kerning Proof Workbench source accepted

Independent review and controller verification accept the finite Kerning Proof
Workbench source, real App demo, lazy menu and R2 repair. Both review findings
are closed: direct release fences editor/Sequence work before fallible cleanup,
and refresh captures the empty-key branch before callbacks can change it.

The controlled full App run passes 10,165 tests with 100 warnings, zero failures,
errors or skips, and exit 0. The corrected full Scriptmix run passes 4,569 tests
with six inherited skips, zero failures/errors and exit 0. Its first isolated
run remains recorded as 4,546 passes, six skips and 23 setup errors, exit 1.
The existing documented Fontport source override and a fresh isolated copy
resolved that setup issue without production or test changes. The earlier App
run's missing command/exit provenance remains historical; the new controlled
result does not retroactively reconstruct it.

The current coverage inventory has 18 unique complete-module gates, each at
least 80% combined statements/branches with zero exclusions: the fourteen prior
paths with kerning's metric replaced, plus Sequence, the window, App demo and
menu. The five current kerning-workflow results are 236/237, 249/249, 149/154,
9/9 and 9/9; the unchanged menu reuses its exact prior measurement.

Five compositions have source implementations (#2, #7, #13, #12 and #8);
thirteen of the minimum eighteen remain without source implementation. This
is not five fully accepted workflows. Next is the separately reviewed #9
Kerning Group Explorer source preparation, followed by the remaining A1 work.
Complete private archives, genuine wheel/sdist and two fresh ordinary install
checks remain pending for one reviewed matched A1 batch. Earlier A0 artifacts
qualify only their exact older bytes. Containing commits, truthful source links,
native master/whole-font/history/Undo/Redo/save-reopen, canonical adoption,
owner installation, delivery and publication remain separate. All 8,723
obligations and the 18-or-more workflow floor remain required.


## 2026-11-09 — Kerning Proof Workbench review fixes

Fence the real editor and Sequence and clear the Apply callback before any
fallible direct release cleanup, including refusal and interruption. Retained
owners remain available for cleanup retry. Capture the actual empty-key inspect
branch before its update callback can change the controls, preventing a second
layout/read/publication pass. Keep inspect, public signatures, the original
selection identity loop and borrowed-font lifetime unchanged.

Seven new real-backend regressions first failed; the six release cases also
triggered the complete-font preservation oracle after prohibited writes. All
seven now pass. The affected 33-module cohort passes 1,894 tests with 24 existing
warnings and terminal exit 0. Whole-module combined coverage is 236/237 for
kerning, 249/249 for Sequence, 149/154 for the window and 9/9 for the App demo,
with zero exclusions; the unchanged menu retains its prior 9/9 evidence.
Pinned Ruff checks pass. An initial affected-cohort collection ordering conflict
was resolved by collecting its existing GUI fixture first, without editing
those tests. Independent re-review and controlled full App/isolated Scriptmix
verification remain pending. Earlier full-suite counts are historical evidence
for their recorded source bytes; the final prior App run's command/exit gap
remains disclosed. No artifact, installed, native, canonical or publication gate
is accepted. All 8,723 obligations and the 18-or-more workflow floor remain.

## 2026-11-09 — Kerning Proof Workbench source candidate

Add the retained App workbench, real direct-import demo and thin lazy Scriptmix
route over one captured borrowed font. Repair the reproduced R2 temporal gap by
invalidating proof before the first fallible read and preserving only the pending
selected occurrence. Keep the original selection identity loop, guarded writer,
readback and callback semantics. No R1 inspect repair or native defect is claimed.

The initial real-backend workflow checks recorded four temporal failures and
two passing sequential-empty cases; the absent window also failed as expected.
The repaired full App suite passes 10,158 tests with no failure or skip (100
existing warnings). The isolated Scriptmix finite cohort passes 58 tests with
one inherited optional-source skip; unchanged Fontport regressions pass 80.
Whole-module combined statement/branch coverage is 235/236 for kerning,
249/249 for Sequence, 146/152 for the new window and 9/9 for each entry script,
with zero excluded statements. Pinned Ruff checks pass. Full Scriptmix execution
and independent source review remain separate pending gates.
The menu count is now 195 additional records / 264 tools; frozen original
provenance remains unchanged. No artifact, installed, native, canonical or
publication acceptance follows. All 8,723 obligations and the 18-or-more workflow
floor remain required.


## 2026-11-09 — A0/I1 paired ordinary milestone and A1 preflight

The finite A0/I1 qualification is accepted: the fresh wheel and rebuilt-sdist
prefixes each passed 1,508 App/auxiliary tests with zero skips, plus 51 Scriptmix
checks and one exact inherited conditional skip. Genuine artifacts and complete
private source archives are accepted for that payload. The full source results
remain 10,089 App passes with no failure, error or skip and 4,562 isolated
Scriptmix passes with six inherited conditional skips; these were not rerun for
the preflight. Containing commits, truthful immutable links, native workflows,
canonical promotion and publication remain open.

Prepared a contract-only proposal for the next A1 Kerning Proof Workbench,
reusing the integrated editor, exact borrowed-font route and retained window
ownership. Source inspection identified possible stale-preview boundaries for
owned reproduction; no runtime defect, shared repair or upstream defect is
claimed. No new product implementation or test acceptance follows from the
preflight. Four source compositions exist; fourteen remain, with all 8,723
obligations and the 18-or-more workflow floor unchanged.

## 2026-11-09 — Complete source consumer verification

Verify the audit and ownership repair with the complete isolated Scriptmix
source suite: 4,562 passed and six inherited skips. Original source and Git
endpoints remain unchanged, and generated catalogue files stay in the test clone.
Runtime, tests and dependencies are unchanged by the subsequent progress notes;
App's 10,089-test result and coverage remain applicable to those exact bytes.
Independent review, genuine immutable provenance, fresh ordinary artifacts and
native qualification remain separate gates.

## 2026-11-09 — Catalogue provenance defect recorded

The catalogue generator selects the last Scripts commit without verifying that
it contains each current menu and matching bytes. Four Font UI Lab menus are
absent from that revision and current HEAD, so their generated immutable links
are false. A separate planned fix will validate committed paths and bytes and
cover dirty/untracked menus. The generator is unchanged in this audit work;
isolated generated pages remain test evidence, not delivered documentation.

## 2026-11-09 — Existing lint baseline discrepancy

The exact Ruff 0.14.10 guide scope reports 420 existing findings, compared with
87 recorded in the guide. The six changed Scriptmix Python paths pass the
corresponding scoped lint check. No historical script was changed to hide or
remove unrelated findings; exact-scope reconciliation remains planned work.

## 2026-11-09 — Audit recovery qualification

Verify the audit menu against the provider's retained constructor cleanup and
preserve pending immutable provenance. Archive and recover generated pages whose
commit links do not contain the new menus; truthful regeneration remains pending
reviewed containing commits. No new ordinary or native acceptance is claimed.

## 2026-11-09 — Tabular Width Audit menu candidate

Add one lazy Font UI Lab menu that constructs one FontWorld and returns the real
App audit controller. Add dispatch and real Fly import checks, an exact menu hash
and explicit pending App commit provenance. The catalogue now has 194 additional
tools and 263 menus; frozen earlier records and bodies remain exact. Native and
new-distribution qualification remain separate from this source candidate.


## 2026-11-07 — Font UI inspection source candidate

Add three read-only linked inspection compositions and their lazy menu routes:
glyph metrics, anchors/components and Unicode/glyph order. Reuse existing
Browser/Preview, Sequence and exact selected-width comparison APIs. Add optional
selection/update callbacks with host-refresh/error clearing. A paired App demo
opens all three over a detached in-memory font. Preserve borrowed
fonts, historical menu payloads and recovery owners; native acceptance and the
known partial base-close repair remain open.


## 2026-11-10 — install.vfpy always reinstalls scripts and dependencies

- Every install copies all files from `Scripts/` afresh and replaces any file
  already at the same path. A symlinked script folder is replaced by a real
  folder; the link target is never written. A directory where a script file
  belongs is still refused.
- Required packages are installed on every run. Packages that no package
  index carries (the fontlab-* packages, pythonqtside) are installed from
  checkouts beside this one through their own `install.vfpy`, once per run
  and safe against cycles. uv receives every other requirement, so version
  ranges, markers and extras are enforced. Without uv, sibling checkouts are
  still installed and only the remaining missing requirements are reported.
- The installer is byte-identical across all eleven installer repositories.

## 2026-11-10 — Correct the two window capability requirements

TMetrics Window requires an App build providing `fontlabapp.fontui.tmetrics`;
TGlyph Window requires `fontlabapp.fontui.tglyph`. Both retain the `fontport`
extra, Fly, FontLab9/Python3.11 and their unverified-native caveats. Removed
only these two unsupported1.2.0 metadata floors and refreshed their source hashes.
The existing missing-dependency messages name the respective module. Imports,
branches and calls are unchanged. README/install guidance now states the exception;
the older120 pinned numeric floors and all261 menus/350 classifications remain.

Regression: both old claims fail; corrected focused suite24passes. The first full
prepared-cohort run retains4547passes/6unchangedskips/11missing-sibling-fixture
setup errors. The initial docs run has42methods:41pass and one history method
with two failed subtests because its origin was shallow. Those failures remain.

An independently reviewed named, full-history source cohort corrects setup only.
The two previously affected test files pass all15tests, including the11 earlier
setup-error cases. The complete corrected source run passes4558tests with six
unchanged skips in104.97seconds, using the verified read-only arm64Python3.11
prepared ordinary cohort and matching Fly source. Its installed App is the dated
d82 build; this is not new normal-prepush/current-peer-install acceptance.
Both complete changed scripts cover11/11statements+2/2branches,100%,zero exclusions.
The locked31-packagePython3.13 strict build and all42pipeline tests pass;
legacy notice/source-snapshot checks pass separately. Changed-file Ruff passes.

The initial shallow preview used25c86 links. The named full-history preview
uses the earlier Scripts commit1fddaa75b7e6 while its window hashes describe
current uncommitted bytes; both previews remain unqualified.
Review/source-only localX1, actualX1-bound regeneration/localX2, the unchanged
normal full gate, reviewed main delivery and exact newCI/artifact/HTTP/browser
remain separate. No native/owner install, numeric release-floor proof, commit,
push or POST follows from these candidate checks. No existing floor/hash oracle
was relaxed; all120 older named floors and261menus/350classifications remain.

## 2026-11-08 — Version-floor note for the Issue 241 windows

- Recorded in PLAN and TODO that the TMetrics and TGlyph scripts need App after v1.2.7 while `app_minimum` stays "1.2.0". Generated `docs/` was not regenerated: the locked docs environment needs network access.

## 2026-11-08 — TMetrics and TGlyph windows (Issue 241)

Added two menu tools that open the new App windows: Metrics > TMetrics Window
(`fly.ap.fontui.tmetrics.show_tmetrics`) sets text in the current font and
writes the sidebearings, widths and pair kerning you change; Contours > TGlyph
Window (`fly.ap.fontui.tglyph.show_tglyph`) shows and edits one glyph on an
explicit layer. Both import App lazily and print an install hint instead of a
traceback when App or Fly is missing; App reports a missing Fontport or font
itself. Two `additional-tools.json` rows pin the exact script bytes with
native acceptance pending. The catalogue grows from 190 to 192 additional tools
and from 259 to 261 menus; the README, site index, generated category pages
and count tests follow. New tests stub the App entry points and check the
install hints, lazy imports, rows and App entry names. Live FontLab behaviour
of both windows is not verified.

## 2026-11-07 — public site review corrections

Both catalogue workflow jobs now fetch full history where catalogue generation needs the last Scripts commit. Genuine depth-one/depth-two checkouts with docs-only children reproduce the previous error and recover all immutable catalogue links after fetching history. The explicit English build validates all 44 historical vendor hashes and references before omitting exactly 35 unused language helpers. The remaining nine vendor assets retain their original bytes. The current component manifest binds primary package notices, embedded preferred sources and CSS/icon provenance; all 36 notice files from 31 locked Python distributions remain. Historical incomplete inventory records remain historical.

The revised pipeline passes 41 tests. Eleven focused English-hook tests cover the whole new module at 100% combined coverage without exclusions. Fresh isolated Chrome 153 desktop/mobile ordinary-word searches navigate real results using the bundled English worker with no omitted-helper request. Runtime/Script bodies and destination pins remain unchanged; previous runtime evidence is reused, not presented as a new runtime run. Independent review and actual source/output/CI/live qualification remain pending.

## 2026-11-07 — public catalogue site candidate

Implemented the full authored site on the exact documentation hash lock, light fltheme26, metadata/hash/immutable-source catalogues and the two-job immutable output publisher. Retained legal/source history and moved authored output-folder guides to `source_guides/` where applicable. Git attributes preserve exact legal/output bytes through index, checkout and archive, including CRLF payloads. All 26 pipeline tests pass per site, including actual local Git publisher boundaries, epoch/parity, links, content and privacy. Independent exact-lock rebuilds match every generated byte and mode. Fresh isolated Chrome 153 desktop/mobile ordinary-word search, result navigation, Escape and mobile drawer checks pass. Outside-click focus on BODY remains a known limit.

Scriptmix: 4546 runtime tests pass with two existing opt-in skips; all 69 frozen original-source hashes pass. Current Scripts and destination hashes remain unchanged.

The scoped licence inventory does not close historical embedded-dependency/source-availability findings. Source/main/output/Pages/live qualification and independent approval are still required; this entry does not claim publication or native acceptance.


## 2026-11-05 — independently approved documentation applied

[Task 2 final review](../verification/issue-230/task-2-fix2-review.md) records
SPEC PASS / QUALITY APPROVED. The [78-file application receipt](../verification/issue-230/task-2-apply.json)
includes this repository's six guides and preserves all 21 repository heads,
branches, indexes and non-selected diffs. This is applied documentation evidence,
not a new product test, installed artifact, native result or publication.

The complete earlier handoff/history below retains its proposal-stage statements
and dated source pins. Later review, application and delivery status belong in the
[live workspace ledger](../verification/issue-230/progress.md). Original future,
native, artifact and preservation contracts remain binding.

## 2026-11-05 — documentation reconciliation proposal

Prepared repository-specific organization, test and MVP/delivery guidance from current source/test configuration and retained Issue 207–211 evidence. Distinguished current canonical layout from qualified candidates, future plugin ownership and unfinished native/artifact gates. Preserved all prior work and changelog evidence; no runtime completion, installation or publication is claimed. Completed historical task rows were removed from the active checklist and consolidated below from existing local CHANGELOG/WORK receipts. Unfinished native, artifact and integration checks remain open.

## Retained scoped completion receipts — corrected evidence map

These are dated results at the stated source/version and acceptance surface. They do not establish current integrated, installed, native or published acceptance. Full receipts and hashes are indexed in the workspace Issue 230 task-2 manifest. Canonical-preimage line ranges below refer to the unchanged historical documents, before these new entries.

- First3reports FontLab9.0.9784:26original scenario checks;11host-free;reviewed screens/cleanup.
  Historical receipt: CHANGELOG.md:1103–1106; WORK.md:1301–1310.

- Issue122zones final fix4:source port and production App route-A writer;Scriptmix4366passes/6skips,3modules100%;App6584passes with outline_extent/zone_native100% and dialog99.47%. Native checks remain open; earlier failing stage retained.
  Historical receipt: CHANGELOG.md:333–358; workspace verification/issue-122/sdd/final/port-zones-report.md, final fix4 gates (lines1–58).

- Mark labels now reserve1000–1255 for grey;361–999/above1255 read Mark N;source/pin update only.
  Historical receipt: CHANGELOG.md:417–419.

- Read-only Anchors App512/Scriptmix684+1skip;195tests per wheel/sdist;72runtime bytes;source/controller review and artifacts pass.
  Historical receipt: WORK.md:2982–3008.

- Anchors FontLab9784 original3scenarios=20workflow/6preservation/Close3;exactH/Lightpostseed;paint/fault/hash/lifetime checks pass.
  Historical receipt: WORK.md:2992–3008.

- Anchors release App0.2.14/Scriptmix1.0.10:prior54samebyte;downloadedR05320workflows/6preservation/Close3;57released historical.
  Historical receipt: WORK.md:3015–3048.

- Unreferenced/Interpolation final fix1:source/fault/independent395glyph oracle;root176/Ruff;10original native workflows+4preservation/Close2;prior57pass.
  Historical receipt: WORK.md:3105–3151.

- Two-review artifact audit:App533;Scriptmix707+1skip;Gitfree706+2skips;216perwheel/sdist;76runtime bytes;82/130payloads/privacy pass.
  Historical receipt: WORK.md:3129–3151.

- Two-review FontLab9784:10original/4preservation/Close2;paint/fault/safety;prior57pass;86hashes/restored paths.
  Historical receipt: WORK.md:3117–3151.

- Reviews release App0.2.15/Scriptmix1.0.11:downloaded R05310original/4preservation/Close2;59original pairs;prior57;historical59released.
  Historical receipt: WORK.md:3153–3187.

- NodeCoordinates release App0.2.16/Scriptmix1.0.12:downloadedR053;timer/Copy/fault/source/original/native/prior59 receipts;historical60released.
  Historical receipt: WORK.md:3241–3261.

- MasterSwitcher release App0.2.17/Scriptmix1.0.13:downloadedR0535original/2preservation/43controls/Close1;prior60pass;61released;selected-bold-text image differences retained; cause not established; no image equality claimed.
  Historical receipt: WORK.md:3313–3333.

- GuidePanels release App0.2.18/Scriptmix1.0.14:downloadedR05327original/21history/167controls/Close3;prior61pass;64released.
  Historical receipt: WORK.md:3407–3422.

- GuideRewriters release App0.2.19/Scriptmix1.0.15:downloadedR05319original/21postseedhistory/162controls/Close3;prior64pass.
  Historical receipt: WORK.md:3491–3507.

- CopyAnchors replacement App0.2.21/Scriptmix1.0.17:downloadedR05311original/7history/133controls/Close1;prior67pass;rejected0.2.20/1.0.16retained.
  Historical receipt: WORK.md:3609–3626.

## 2026-11-05 — planning chronology reconciliation

Dated41/45/49/54/57/59/60/61/64/67/68release and pending-candidate paragraphs are successive historical states. Exact release/R053 receipts supersede earlier pending wording for those same stages only. Preserve all130stems, other collections, seven Names editors and current unmet tool/native contracts. ForthcomingApp0.2.11 and old base-only branch commands are obsolete operating instructions; qualify actual matching providers/lineage instead. Historical passing results retain their dated source and acceptance scope in the entries above and original history below. This documentation change creates no new runtime acceptance.

---
this_file: CHANGELOG.md
---

## Unreleased — Issue 208 tools for App features the menu did not reach

- Add eight tools that write no font data and open shared App panels through Fly, so 259 menu
  tools now ship (69 samples, 190 additional): Anchors > Duplicate Anchor
  Rings; Components > Component Graph; Metrics >
  Sidebearing Offset Preview; Names > Glyph Metadata Tree and Glyph Name Completion;
  Proof > Character Map; Utilities > Find Font Files and
  Reference Image Viewer. Character Map writes the clipboard only when its Copy
  button is pressed; Find Font Files opens a result only on an explicit
  activation; Reference Image Viewer prints only on an explicit Print, and Qt's
  print dialog can write a PDF to any path the user picks.
- Skipped: the three anchor coordinate panels (Center Horizontally, Round To
  Grid and Snap To Metrics define their own panels with the titles and keys of
  the App panels, so a new tool would collide on the window key).
- Not already reached: Character Map and Glyph Name Completion were added
  because Waterfall (it uses the proof inspect model) and Vertical Metrics
  Diagram (it uses core.completion) do not reach those App panels.
- Native FontLab acceptance is pending for all eight tools; the offline tests
  read each script's own `fly.ap` calls and check by AST that every entry point
  they name exists in the resolved App source. Pinned counts in the
  delivery tests and README change 182/251 to 190/259; every new row in
  additional-tools.json carries the hash of the final script bytes.

## 2026-11-03 — PythonQt QPolygonF access

- Auto Cursive Attachment Get Sample/Add Anchors and Optical Center read outline
  polygons with size()/at(); FontLab's PythonQt QPolygonF is neither iterable nor
  subscriptable. Revision edits, current hashes and doc source links updated; test
  doubles model the native polygon.

## 2026-11-03 — Native sweep fix

- Unbundle Punctuation Kerning reads code points from flGlyph.fgGlyph.unicodes;
  flGlyph has no unicodes in FontLab 9. Revision edit, current hash and doc
  source link updated; test doubles model the native glyph.

## 2026-11-03 — App 1.2.0 minimum

- Require App 1.2.0 for its domain module layout; update current metadata,
  script notes, tests and installation guidance, with exact script revision
  edits and matching current hashes. Preserve past release and native evidence.

## 2026-11-03 — Issue 205 App domain imports

- Migrate all 249 menu scripts and their tests/docs to canonical App domain
  paths. Retain `tools/migrate_app_paths.py`, a deterministic stdlib rewriter
  driven by the sibling App alias oracle, with identifier-boundary checks.
- Resolve real test helpers by canonical module and file path, preserving
  identity and provenance assertions. Mirror the domain tree in owned doubles.
- Refresh 180 additional-tool and three menu-move current pins. Extend 68
  revision rows and add 181, recording 613 exact import edits. Frozen release
  bytes and native-evidence fields remain unchanged and recoverable.
- Verification: 4479 passed, 15 skipped; all 249 changed scripts pass the 80%
  coverage gate. Docs tests: 10 passed. All scripts compile; current pins match
  and all 69 historical migration payloads recover exactly. Native FontLab
  acceptance was not rerun.

## 2026-11-03 — Event Log and Live Glyph Info context

- New Reports > Event Log: a small panel that prints to Output each switch of the
  active font, window/tab, glyph, layer, master and glyph/node selection, plus tool
  changes, undo/redo, saves, kerning, features, metrics, font info and clipboard
  notifications. It listens to 29 FontLab notifications (31 connections with the
  panel's own); closing the panel releases them all. Verified live in FontLab 9
  with a buffer sink (not Output).
- Live Glyph Info shows "Font · Glyph · Layer" under the glyph name. The change is
  recorded in `menu-revisions.json`, so the released bytes can still be recovered.
- Tests: 4468 passed, 19 skipped.

<!-- workspace-handoff:2026-11-03 -->
## 2026-11-03 — installer options, licence and cleanup

- Added `install.vfpy`: copies `Scripts/` into FontLab's Scripts folder, merging with
  other extensions; scripts only, no package. Verified inside FontLab 9.

## 2026-11-03 — documentation handoff for November 2–3

Accepted feature faed9163 restores three original node actions. Local ABannotates49 nonreserved terminal controls and preserves two refused chooser owners.

Task 2records605 affected passes plus one current-source pin failure; complete ABsuite/coverage/artifact acceptance is pending.

Observed canonical checkout: `main` at `3acfce2ea893`. No source integration is performed by this update.

Updated the requested AGENTS/TODO/PLAN/CHANGELOG/README documentation and
recorded the paused state. Existing project text, examples and history remain;
no runtime source, installation, native session, branch/ref, release or site was
changed by this documentation maintenance. Source/archive/ordinary/native and
promotion acceptance remain separate claims. Detailed workspace evidence is
recorded in the root CHANGELOG and retained verification reports.
<!-- /workspace-handoff -->
## Duplicate Anchor Rings removed — issue 201

`Reports/Duplicate Anchor Rings.py` is gone; the feature now lives in fontlab-python-plugmix as the `duplicate_anchors` reporter.
## Three original Node Duplicator actions verified — 2026-11-02

All-foreground, current-first-layer and two-handle actions call the guarded App
entry point from genuine0.2.26.dev333+g362e36bf1. Fifteen new owned integration
cases cover real capture/planning/staging/write/readback, file entry points,
copy metadata/fractions, repeated parents, duplicate auxiliary names, first-only
scope, missing/empty selection and refusal of older rescued adapters.

Normal4496pass/1existing Spacing Preview skip; all3new modules100% combined coverage.
Both ordinary direct/rebuilt-wheel tuples pass7485App/4496Scriptmix(+1oldskip)/
600Echo and4new guide experiments;46installed dependencies are compatible and
990provider/RECORD hashes stay unchanged per suite. App's complete764-source
sdist reproduces the whole wheel. Standalone Qt proof is separate from FontLab.

All248old menu bodies,179prior provenance-row values, frozen migration/menu-move/
rescue records and111unchanged inherited test paths are exact. Four inherited
inventory tests change only179->182/248->251 and matching diagnostic strings.
Menu total251=69samples+182additional. Three provenance rows retain independent
source/licence/copyright identities without redistributing original bodies.

Commands: rtk proxy /bin/sh .metaswarm/quality.sh coverage <this-checkout>
fontlab-python-scriptmix, exit0; exact environment/argv and80%gate receipts are in
external original-workflows-20261102/scriptmix-final-normal-quality. Ordinary
commands are recorded in wheel-ordinary-scriptmix-serial-command.json and
sdist-ordinary-scriptmix-command.json, both exit0. The initial parallel wheel
catalogue collision is retained; serialize tests that rebuild this shared tree.
No product/test change was needed to resolve that runner error.

Native four-font full preservation/history/Undo/Redo/save-reopen, actual TypeRig
window priority/lifetime, original Transform and release/promotion remain open.

## External original-source lookup repaired — 2026-11-01

The historical inspector helper now honors FONTLAB_PRESERVED_ROOT before other
copies and verifies the recorded SHA256 for every lookup route. Missing or
corrupt explicitly selected archives fail instead of silently falling back.
Only the shared test helper and its regression tests changed; frozen migration
records, menu pins and production scripts remain unchanged.

Full suite: 4404 passed, 56 failed, 6 skipped; exact failure IDs unchanged
from latest-cohort baseline. Full command/exit1 recorded in commands.json.

Seven regression cases: before fix 4 failed/3 passed; after fix 7 passed.
Five real archive audits: 4 passed, 1 retained provenance failure in reports.
All 69 recorded Scriptmix preserved sources match the external archive hashes.
Original bodies were read/parsed only, never executed. Ruff checks passed.
Evidence and exact audit/full-suite commands: original-byte-audit-20261101/
commands.json under the external issue123 evidence root.
Regression command (exit 0): rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
/Volumes/Falstaff4T/fontlab-scripting-data/issue123/latest-cohort-20261101/env/bin/python
-I -B -m pytest -o pythonpath=. -p no:cacheprovider -q tests/test_migration_history_sources.py
Lint command (exit 0): rtk proxy ruff check --no-cache tests/test_migration_history_sources.py tests/_migration_history.py

Native acceptance, provenance repair and zone integration remain open.

## 2026-11-01 — Reset source dispositions

Correct18Reset backlog rows against the retained2026-10-22 full22-source review.
Keep every original identity/hash and candidate menu link. Partial and unported
statuses replace unsupported Ported/Duplicate/Retired claims; notes expose the
specific missing behavior. Newer candidate changes still require evidence to
clear those dated findings. No source bodies, menu scripts or manifest pins change.

Verification: rehashed all18originals; row comparison preserves identity/hash/menu
columns and all other table rows. Initial count19assertion failed before writes;
correct count18(four audited originals have no backlog row). Exact test command:
rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1
/Volumes/Falstaff4T/fontlab-scripting-data/issue123/current-cohort-20261101/env/bin/python
-I -B -m pytest -o pythonpath=. -p no:cacheprovider -q
tests/test_curated_delivery.py -k backlog:exit0,2passed6deselected.
Initial pythonpath= command failed collection because menu_layout is root-local;
no product failure inferred. git diff --check:exit0. Full source/native gates
remain open; this is a backlog correction, not port completion.

## 2026-11-01 — figure window geometry and completion

The isolated figure panel saves/restores geometry in its own settings store.
Restore runs after full construction and keeps malformed settings usable with a
diagnostic. Close records save failures and always runs owned cleanup. Reuse
App script_completion for reject/Escape and duplicate-launch closure; no custom
reject recursion. Family/unrelated keys remain, contour replacement resets.
Existing larger preview layout and stay-open Apply behavior remain explicit
adaptation differences; automatic alignment and native preservation are open.

Seven new full-selection-base fakeQt regressions failed before implementation.
Final focused checks:311passed against each ordinary App wheel/sdist. Nine realQt
subprocess cases pass on Qt5.15.19 and Qt6.12.0 using the production subclass,
minimal QDialog selection base and actual App completion/cleanup/launcher helpers.
They cover Close/button/reject/Escape/replacement, parent/flags/modality, geometry
roundtrip, repeated completion, destruction, malformed data and write/sync/save
failures. Qt5 uses source App; Qt6 uses installed App. No font/preferences touched.
Close errors are retained in slot_error, not promised as user-visible feedback.

Full configured gate x6Yymo:58failed4403passed17skipped, exit1; exact58failed-node
set unchanged. Nine extra skips are the realQt tests absent from the minimal gate;
they pass separately. All14modules exceed80%; figure module88.22%. Docs10pass,
173current pins match, scoped Ruff/diff check pass. Independent source review
finds no blocking issue. No push while the full gate fails; native remains open.

Commands through rtk proxy:
- Candidate: env PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue123/standard-message-priority-20261101/ordinary-artifacts/wheel-env/bin/python -B -m pytest -q -p no:cacheprovider tests/test_default_figure_geometry.py (before production:exit1,7failed).
- Same environment: tests/test_default_figure_geometry.py tests/test_default_figure_geometry_runtime.py tests/test_default_figure_settings.py tests/test_default_figure_settings_runtime.py tests/test_issue122_G2.py tests/test_cov_a_writers.py:exit0,311passed; repeat sdist-env/bin/python:exit0,311passed.
- Candidate: env PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 FONTLABAPP_TEST_QT5=1 PYTHONPATH=/Volumes/Falstaff4T/fontlab-scripting-data/issue123/standard-message-priority-20261101/fontlab-fontlabapp/src:/Users/adam/Developer/vcs3/github.fontlabcom/fontlab-scripting/fontlab-fly/src /Volumes/Falstaff4T/fontlab-scripting-data/verification/issue-120/typed-date-z11/qt5-env/bin/python -B -m pytest -q -p no:cacheprovider tests/test_default_figure_geometry_runtime.py:exit0,9passed.
- Workspace: .metaswarm/quality.sh coverage /Volumes/Falstaff4T/fontlab-scripting-data/issue123/menu-message-priority-20261101/fontlab-python-scriptmix fontlab-python-scriptmix:exit1.
- Candidate: env PATH=/opt/homebrew/bin:/Users/adam/.local/bin:/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 UV_CACHE_DIR=/Volumes/Falstaff4T/fontlab-scripting-data/uv-cache TMPDIR=/Volumes/Falstaff4T/fontlab-scripting-data/tmp uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest --with mkdocs-codeinclude-plugin==0.3.1 --with PyYAML python -B -m pytest -q -p no:cacheprovider tests_docs:exit0,10passed.
- Candidate: ruff check 'Scripts/Components/Set Default Figures.py' tests/test_default_figure_geometry.py tests/test_default_figure_geometry_runtime.py; git diff --check:each exit0.

Wait, but: real standalone Qt is not native FontLab. Dedicated-host positioning,
full native cleanup, Apply/history/save and original-domain acceptance remain.
External evidence uses menu-message-priority-20261101/figure-geometry-*.

## 2026-11-01 — recover from figure preference read failures

Independent review found213d687 could fail during partial panel construction,
before launcher registry ownership. Match the original's usable-default behavior:
finish construction at lining0 and display the read error after initial refresh.
Do not overwrite saved data during fallback. A later choice can save normally;
close still disconnects all owned signals. Family0 regression now makes an actual
selection change instead of relying on the fake combo's unchanged-index signal.

Three new panel-level regression cases failed before repair and pass afterward.
Both ordinary App wheel/sdist environments:295focused tests pass. Docs10pass;
all173current pins match; scoped Ruff and diff check pass. Configured full gate:
58failed4396passed8skipped; exact failed-node set unchanged; all14changed modules
exceed80%, Set Default Figures87.84%. Source re-review closes the finding.

Commands through rtk proxy:
- Candidate: env PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue123/standard-message-priority-20261101/ordinary-artifacts/wheel-env/bin/python -B -m pytest -q -p no:cacheprovider tests/test_default_figure_settings.py -k restore_fails (before repair:exit1,3failed25deselected).
- Same environment, tests/test_default_figure_settings.py tests/test_default_figure_settings_runtime.py tests/test_issue122_G2.py tests/test_cov_a_writers.py:exit0,295passed; repeat with sdist-env/bin/python:exit0,295passed.
- Workspace: .metaswarm/quality.sh coverage /Volumes/Falstaff4T/fontlab-scripting-data/issue123/menu-message-priority-20261101/fontlab-python-scriptmix fontlab-python-scriptmix:exit1,stAX1h.
- Candidate: env PATH=/opt/homebrew/bin:/Users/adam/.local/bin:/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 UV_CACHE_DIR=/Volumes/Falstaff4T/fontlab-scripting-data/uv-cache TMPDIR=/Volumes/Falstaff4T/fontlab-scripting-data/tmp uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest --with mkdocs-codeinclude-plugin==0.3.1 --with PyYAML python -B -m pytest -q -p no:cacheprovider tests_docs:exit0,10passed.
- Candidate: ruff check 'Scripts/Components/Set Default Figures.py'; ruff check tests/test_default_figure_settings.py; git diff --check: each exit0.

Wait, but: this is source/artifact evidence, not native acceptance. FontLab PID30373
exists, localhost47400 has no listener. No restart or owner-state mutation.
No push while full gate fails. Retained logs/review: external
menu-message-priority-20261101/family-read-recovery-*.

## 2026-11-01 — remembered figure-family choice (isolated candidate)

Set Default Figures now restores the four-way family choice before connecting
signals and saves it after refreshing the preview. Missing or invalid values
select lining. Only optionFigures is written; unrelated keys stay, settings
fallbacks are disabled, and Replace own contours remains unchecked on reopen.
Read/write failures are reported without a font write. Window geometry,
automatic alignment and native acceptance remain open.

Configured gate yKdxzx:58failed4393passed8skipped, exit1; exact failed-node set
unchanged from figures-default. Four additional skips are real-Qt tests in the
minimal gate environment; all four run and pass separately under both Qt5 and
Qt6. All14changed modules exceed80%; figure coverage87.43%. Command from workspace:
`rtk proxy .metaswarm/quality.sh coverage /Volumes/Falstaff4T/fontlab-scripting-data/issue123/menu-message-priority-20261101/fontlab-python-scriptmix fontlab-python-scriptmix`.

Tests-first: 25 intended failures before implementation; an earlier fixture
import error was corrected. Real Qt6 then caught instance-level NoError access;
using the class enum fixes it. Fresh-process isolated INI checks pass on Qt5
and Qt6 (four families each); no user preference domain was written by tests.
Both ordinary App wheel and sdist environments pass292 focused tests. Docs10
pass; all173current manifest pins match. New test files pass Ruff and diff check.

Commands (rtk proxy, candidate cwd; all final commands exit0):
- env PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue123/standard-message-priority-20261101/ordinary-artifacts/wheel-env/bin/python -B -m pytest -q -p no:cacheprovider tests/test_default_figure_settings.py tests/test_default_figure_settings_runtime.py tests/test_issue122_G2.py tests/test_cov_a_writers.py
- Same command with sdist-env/bin/python:292passed.
- env PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 FONTLABAPP_TEST_QT5=1 PYTHONPATH=/Volumes/Falstaff4T/fontlab-scripting-data/issue123/standard-message-priority-20261101/fontlab-fontlabapp/src:/Users/adam/Developer/vcs3/github.fontlabcom/fontlab-scripting/fontlab-fly/src /Volumes/Falstaff4T/fontlab-scripting-data/verification/issue-120/typed-date-z11/qt5-env/bin/python -B -m pytest -q -p no:cacheprovider tests/test_default_figure_settings_runtime.py
- env PATH=/opt/homebrew/bin:/Users/adam/.local/bin:/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 UV_CACHE_DIR=/Volumes/Falstaff4T/fontlab-scripting-data/uv-cache TMPDIR=/Volumes/Falstaff4T/fontlab-scripting-data/tmp uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest --with mkdocs-codeinclude-plugin==0.3.1 --with PyYAML python -B -m pytest -q -p no:cacheprovider tests_docs
- ruff check tests/_figure_settings_support.py tests/test_default_figure_settings.py tests/test_default_figure_settings_runtime.py

Wait, but: standalone Qt and test doubles do not prove PythonQt/native panel
lifecycle. No live installation or owner font changed. Full gate evidence is
retained separately; no push while that gate fails.

## 2026-11-01 — Set Default Figures keeps own contours by default

UI, apply_pairs and write_components now default to keeping existing contours.
Explicit Replace own contours remains available. The script/doc page warn that
retained outlines can overlap the newly installed component; advances and kerning
memberships still follow the selected sources. Make Lower Unicase is byte-unchanged.
The figure source pin and generated page are current; all173current pins match.
Original source33dcbede... was read, not executed, and remains byte-unchanged.

Baseline167G2tests passed. Before the fix, five regression assertions failed and
eight explicit-option cases passed. Final183G2tests pass against each ordinary
App.153 wheel/sdist installation. New16-case matrix covers all4families,10digits,
2masters, public default/explicitFalse/explicitTrue plus raw writer omitted default.
It checks contour/node retention, anchors, components, fractional advances, class
membership, immutable Unicode snapshots and existing-target history enrollment.
Independent review's missing raw-writer test was added and re-reviewed clean.

Configured full gate:58failed/4368passed/4skipped; exact failed-node set equals the
prior58. All14changed modules pass80%; figure module86.32%. Docs10passed. No new
Ruff findings under identical filename/config comparisons; the first ad-hoc lint
comparison used different configuration and was discarded, with logs retained.

Commands through rtk proxy, cwd this isolated candidate:
- env PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 <ordinary-artifacts/wheel-env>/bin/python -B -m pytest -q -p no:cacheprovider tests/test_issue122_G2.py: exit0 baseline167/final183.
- Same command with -k 'contour_switch or contours_are_removed_only' before production edit: exit1,5failed8passed166deselected.
- Same final G2 command using <ordinary-artifacts/sdist-env>/bin/python: exit0,183passed.
- .metaswarm/quality.sh coverage <this-candidate> fontlab-python-scriptmix from workspace: exit1;1DbhPV retained in external figures-gate-evidence.
- env PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest --with mkdocs-codeinclude-plugin==0.3.1 --with PyYAML python -B -m pytest -q -p no:cacheprovider tests_docs: exit0,10passed.

Wait, but: these are source and installed-App checks. Automatic alignment,
persisted family/window choice, full source domain and native Apply/Undo/Redo/save
preservation remain open. No font or live installation changed; no full-gate push.
Exact external logs use figures-* under menu-message-priority-20261101.


## Unreleased — report test compatibility

G13 uses the real report signature for its autospecced double. Unsupported
arguments remain refused;106tests pass against both canonical and private App.
No runtime change. Whole-cohort and native gates remain open.


## Unreleased — retained encoding chooser priority

Paste Glyph Order Encoding reapplies priority on each show and retries safely
after a setter failure. All33 G8 tests pass. Native behavior remains unverified.


## Unreleased — anchor chooser priority

Two owned anchor file choosers retain their parent/type/filter and request
priority before execution. G11 source suite82passed; native acceptance pending.


## 2026-11-01 — owned menu warnings and confirmations

- Route eleven warnings and three confirmation questions through App's owned
  priority message helper; preserve parents, title/body, standard buttons,
  default No, Yes-only edits and post-confirmation recapture.
- Refresh eleven current menu hashes and generated pages without rewriting
  historical provenance. Source verification: 382 focused tests and 10 docs
  tests pass; full candidate results and inherited/cohort failures are in WORK.
- Native FontLab and matching installed-artifact acceptance remain open.

## 2026-10-22 - Alignment zone tools; Master Metrics Table on the master writer

- Metrics > Alignment Zones opens the shared App zone panel with the native
  zone backend: per-master zone table, add, remove and edit, Suggest from
  o / O, staging for all masters and one Undo step per Apply. Docstring lists
  what differs from the original sample (required unique names, whole-table
  refusal of a bad cell, Font window only, re-created zone guides, fl#8574).
- Guides > Suggest Zones From Overshoots previews baseline, x-height and caps
  zones from H/O and x/o for the current or all masters. A zone at the same
  position, else with the same name, is replaced and keeps its name, tags and
  lock. Apply measures again, refuses a stale preview and writes through the
  same backend as one Undo step. Refusals reach the status line.
- Font Info > Master Metrics Table writes through the App master-metrics
  writer (one Undo step, read-back, restore on failure) instead of the
  Font Info plan writer. It reads the same per-master properties that the
  writer reads back, refuses values that changed since the preview and shows
  the queued-glyph note. Docstring adds fl#8574.
- Records: two `additional-tools.json` rows (173 additional, 242 tools),
  PORTING-BACKLOG statuses, NOTICE section, Master Metrics Table revision
  edits and hash, docs pages. Offline tests: `tests/test_issue122_Z1.py` and
  the rewritten Master Metrics Table tests. Native verification pending.

## 2026-10-22 — Common Glyphs review fix2 test dependency

- Provision glyphsLib explicitly in test.sh so real production-metadata tests
  run with an ordinary App wheel. Document the prepared environment requirement.
  No App/menu/runtime requirement, assertion, hook or coverage change. Full
  App/Fontport artifact compatibility and native/writer acceptance remain open.

## 2026-10-22 — Common Glyphs review fix1

- Classify GlyphData's sanitized fallback as unknown when a nonfinal component
  production contains a dot or a component/base has no semantic production.
  Preserve genuine unchanged `f_i`, final-component dots and known-base suffixes.
  App source and all unrelated menu/provenance records stay unchanged. Full
  all-font charcoal action and installed/native acceptance remain incomplete.

## Common Glyphs report source repair (partial milestone)

- Add explicit literal Copy Characters/Copy Original Report source actions through
  existing App native MIME helpers; normalized human selection stays distinct.
  New callbacks/panel/OS clipboard handoff remain native acceptance gates.

- Replace the embedded comparison implementation with shared App capture,
  source-faithful reports and owned lifecycle; use actual GlyphData production
  metadata at this caller boundary with explicit unknowns. Restore first-open
  primary strings, family order, one-font glyph order and exact trailing spaces;
  retain alternative encodings and reusable slash-name text.
- Expose default-off charcoal marking as visibly unavailable under FontLab issue
  8564. The full all-open-font action remains unimplemented/unaccepted. This is a
  partial source milestone, not full original-scope/native completion.
- Change only the Common Glyphs menu/source pin and generated source page;
  migrate obsolete embedded-engine tests to expanded App coverage while retaining
  both menu files' original import/source contracts.

## 2026-10-22 — Master Text Comparison review fix1 pin

- Bind the shared App repair for native result-slot ownership, immediate-preset routing around unrelated custom holds, and cumulative bounded failed-panel recovery. Menu bytes are unchanged; native acceptance remains pending.


## 2026-10-22 — Master Text Comparison workflow repair

- Restore original blank custom/Side-by-side defaults, automatic optional local presets/four attributed fallback lists, Run/double-click precedence, full sanitation diagnostics and every final space/newline.
- Share bounded opening-font capture, exact named-symbol staging/readback and retained sender/shape cleanup; persist only owned source controls after proof and geometry on Close. Native model binding, special text/IME, rendering and complete preservation remain pending (FontLab #8576).


## 2026-10-22 — Case Coverage shared report fixes

- Bind the reviewed App fix for unknown uncased all-clear feedback and automatic Details after completed-analysis proof errors. Menu source bytes and controls are unchanged; native proof usability remains held.

## 2026-10-22 — Case Coverage candidate

- Add full original controls, persistent owned settings, current/all-font detached case reports, explicit aliases/Unicode alternatives/Math/Ligature/unknown findings and multi-character compatibility fixes.
- Add explicit exact-view target choices and source-backed proof mechanics with content verification and bounded retained cleanup. Native text-block binding and actual proof usability remain held; no native/full-port acceptance claimed.

## 2026-10-22 — Separate legacy lowercase coverage

- Report legacy lowercase-to-`.sc` gaps separately from modern `.sc`/`.smcp` acceptance; retain export filtering and font order. Correct the Scriptmix menu total to 241.

## 2026-10-22 — Smallcap Consistency

- Add complete modern/legacy smallcap reporting: export census, missing and orphan counterparts, capital/lowercase coverage and both kerning-group sides. Correct the original Boolean predicate and preserve Unicode/ligature/alternate names. Report unknown mappings and ambiguous groups.
- Use detached facts and bounded lazy native capture; explicit public.skipExportGlyphs compatibility policy, no font changes. Installed native qualification remains pending.

## 2026-10-22 - Undefined marks no longer read as negative greys

- Reports > Label Statistics and Names > Select by Mark label only marks 1000-1255 as greys, the range FontGate defines (`glyphs_write.cpp`). Marks 361-999 and above 1255 now read "Mark N" instead of "Grey -639". Revision records and docs pins are updated.

## 2026-10-22 - Coverage tests for 39 scripts

- `tests/test_cov_a_*.py` and `tests/test_cov_b_*.py` cover the Anchors, Components, Contours, Features, Font Info, Masters, Names, Kerning and Reports scripts below the 80% gate (now 98-100%). Script bytes and pins are unchanged; the fakes model PythonQt strictly.

## 2026-10-22 - Menu folder merge

- Merge the Cleaning menu into Cleanup and Reporters into Reports (owner decision).

## 2026-10-22 - Glyph-window Undo scope and Refresh fixes

- Selection To All Backgrounds: Refresh in a Glyph window reads the selection
  again; when it fails (nothing selected, a mask layer) the plan is cleared and
  Replace is off. Only outside a Glyph window does Refresh re-read the planned
  contours. A closed or changed font now says so instead of "Switch to the
  Font window". Docstring rewrapped and Refresh described.
- Set Component Locations: say that Apply refuses in a Glyph window when the
  edit includes glyphs the window does not show (App guard, FontLab issue
  8573): keep Selected components edits to the shown glyphs and apply All
  components from the Font window. Docs pages and destination hashes refreshed.

## 2026-10-22 - Selection To All Backgrounds: font-wide Undo

- Write only while the Font window is active. In a Glyph window FontLab
  records the step for the shown glyph only, so one Undo left the other
  backgrounds changed (measured on 9.0.9790). The refusal keeps the preview.
- Plan in the Glyph window, then re-read the planned contours by layer name
  and shape/contour index, with node coordinates and types in the signature.
  Selection is not read again: the Font window shows the layer through
  another wrapper without it. Refresh the docs page and destination hash.

## 2026-10-22 - Complete queued-update disclosure

- Complete default-writer status/console disclosure, including all custom
  master, cleanup and unicase paths. Show the figures warning once.
- Correct pending-update documentation and refresh generated pages and pins.

## 2026-10-22 - Pending native update disclosure

- Disclose pending native updates in writer results and status messages.
- Refresh destination hashes and cover queued writes and empty interpolation.

## Unreleased — Final script fixes (2026-10-22)

- Use the corrected App backup resolver, custom-suffix naming, default suffix
  and detached-shape repair APIs. Keep backup view state and now retain contour
  names. Remove the repeated empty-job guard.
- Reuse captured automatic-layer facts in six planning hooks; Tabular Figure
  Copies inherits the corrected App hook. Keep fresh facts at write time.
- Replace background shapes individually and retain component shape/data/builder
  history before detachment. Add ownership and clone-metadata regressions.
- Expand 79 short menu docstrings with What/How/Why/Usage/Benefit sections;
  retain source credits and licence text. Replace public acceptance-status and
  unmeasured Undo wording, normalize Fly module imports and type both remaining
  unannotated entry points.
- Refresh 76 additional-tool hashes, three moved-menu hashes and 68 reversible
  documentation overlays. Keep migration.json as the frozen v0.2.0 record;
  extend historical reconstruction to compose docstring edits with path moves.
- Regenerate source-backed catalogue pages. Record remaining shared App
  scaffolds and native milestone checks as open work in PLAN and TODO.
- Keep backup prefixes and the temporary-layer marker case-sensitive, with
  case-insensitive exclusion of master names; test case-twin master routing.
- Use one uniform indented house layout for the 79 expanded docstrings;
  remove residual qualification status, trailing spaces and long blank runs.
- Read back every replaced background for its planned contour count and no
  components. Report missing masks and silent native write mismatches with
  the Undo hint after closing history.
- Verification: requested runtime command, 3,812 passed / 6 skipped, exit 0;
  full arm64 runtime suite, 3,812 passed / 6 skipped, exit 0; documentation
  suite, 10 passed, exit 0; selected Ruff rules, 144 changed scripts clean,
  exit 0; strict site build, exit 0. Native FontLab qualification remains open.

## Unreleased — 2026-10-22 — Practical tools and shared helpers

- Expand the practical menu to 240 tools: 69 sample adaptations and 171
  additional tools, including Metrics, Names, Anchors, Components, Masters and
  Contours editors and independent Glyphs-script rewrites.
- Route common panels, edit guards, planners and history through App via Fly.
  Route feature-source access through Fontport. Use FontGate font identities
  for glyph-building and locking calls.
- Extend master backups, all-master layer copying and coordinate rounding;
  keep the shared backup recognition rule and explicit anchor refusals.
- Bind third-party source identities to SHA-256 records. Keep historical
  migration records and current destination hashes independently verifiable.
- Make default tests independent of external original folders. Add explicit
  source audits; a present partial or corrupt archive fails with all findings.
- Restore the explicit permission to adapt the author's own Apache-2.0 FontLab
  samples; keep the separate restriction on third-party original bodies.
- Require installed matching App and Fontport packages for the complete suite;
  keep only Fly on the sibling source path.
- Offline checks on Python 3.11 arm64: complete runtime suite 3,747 passed,
  6 skipped; documentation suite 10 passed. Both exit 0, with no failures.
  Ruff 0.14.10 reports 87 existing findings across
  Scripts, tests, documentation tests, menu_layout.py and src_docs/build.py.
- Retain full source/licence attribution and source-backed menu documentation.
  Earlier native receipts remain limited to their exact installed files;
  new ports still require native acceptance.

## Removal prep: review fixes, round 1 (2026-10-22)

- Document both source-audit flags; simplify seven historical Names headers and
  refresh their destination hashes and generated source includes.
- Collect every missing/mismatched archive file before failure; test a copied
  archive with one deletion and one corruption. Current-file checks stay intact.
- Record Scriptmix-first landing order, then Examples forward pins (all 24
  currently match). Prevent bytecode/pytest caches in gates; stage old caches
  locally because the sandbox rejected the requested external discard directory.
- Canonical suite: 3752 passed, 1 skipped; empty root: 3747 passed, 6 skipped;
  docs: 10 passed each. Corrupt-copy audit: exit 1 expected, both faults reported.
  Homebrew Ruff reproduces nine pre-existing findings; other edited files pass.


## Issue 122 Task 1: removal preparation (2026-10-22)

- Keep historical source path/hash checks independent of external rescued/ bytes;
  source-byte/interface audits are explicit and skip absent archives clearly.
  Current menu hashes, behaviour and release-byte checks remain mandatory.
- Explain external archives and both archive SHA-256 values in NOTICE; correct
  README/backlog/guide and historical Names source comments, retaining credits.
  Refresh only seven current destination hashes and their catalogue pages.
- Canonical suite: 3751 passed, 1 skipped; empty preserved root: 3746 passed,
  6 skipped; documentation tests: 10 passed in each. Original uvx Ruff returned 0;
  Homebrew Ruff 0.14.10 reports nine pre-existing findings (see fix round 1).
  Full commands and limitations: WORK.md and .build/removal-prep/report.md.


## Unreleased — 2026-10-22 — Backup, copy and rounding extensions

Extend seven existing tools; the menu and its counts do not change.

- Masters > Duplicate Current Layer backs up the current master layer or all
  master layers of the selected glyphs, with a custom suffix, and lists the
  existing backups (preview only). Each Apply is recorded as one Undo step.
- Backups are named `<master> backup <suffix>`; a taken name gets (2), (3).
  A name that equals a master, contains @, # or |temp|, or would read as
  another master is refused.
- Restore Backup Layer, Display Next Layer, Display Previous Layer and Layer
  Cleanup share one backup rule: new names, legacy @ names and any layer named
  `<master> <text>` (for example "Light Copy") resolve to the longest matching
  master. Such layers now take part in the Next/Previous cycle and are classed
  as backups in Layer Cleanup; nothing is ticked at the start, and "tick kind"
  can select them.
- Copy Layer Between Masters copies to the checked target masters in one Undo
  step. Changing the source checks all other masters again; the target list
  scrolls.
- Contours > Round Coordinates rounds nodes, anchors and component offsets in
  one Undo step. Anchors starts ticked; untick Anchors to round only nodes and
  offsets. A layer with duplicate anchor names or an anchor that would move to
  0, 0 is listed and kept.
- Vertical Metrics Diagram stays read-only. Font Info > Master Metrics Table
  edits the same four metrics with a selected-row diagram.
- PORTING-BACKLOG.md records Alignment Zones and Suggest Zones From Overshoots
  as duplicates of Font Info > Zones (Add and Remove zones; Auto-detect zones),
  which work per master. A scripted all-master zone port waits for an App zone
  writer. Back Up Master Layers is recorded as a duplicate of Duplicate Current
  Layer, which now covers all masters.

## Unreleased — 2026-10-22 — Contours tools and Glyphs-script rewrites

Add 73 tools; the active menu grows from 167 to 240 (171 additional tools).
57 of the 61 former archive launchers now have a port.

- Contours, from the author's own samples: Round Coordinates, Remove Overlap,
  Add Extremes, Correct Contour Direction, Straighten Short Curves, Optimize
  Start Points, Delete Small Contours, Fix Zero Handles, Delete Duplicate
  Contours, Transform and Slant, on the shared App outline panel and geometry
  history. Each change is recorded as one Undo step and read back. Direction
  follows same-shape nesting; open contours and reversed duplicates are kept.
- Contours generators and hint tools, from the author's own samples:
  Placeholder Glyphs, Shadow Copy, Tabular Figure Copies, Outline Effect,
  Superior & Inferior Figures, Small Caps From Capitals, Autohint Selected
  Layers and Remove PostScript Hints. Each Apply is recorded as one Undo step;
  each new glyph is recorded as its own Undo step, and the outlines as one
  more. Generators do not copy anchors.
- Independent rewrites of Glyphs scripts; no source code is copied:
  - after Pedro Arilla: Real English Text, Real Spanish Text, Delete Stickers,
    Start From Scratch, Decompose Serif Components, Make Lower Unicase, Set
    Default Figures, Retract Handles and Simplify Selected Nodes;
  - after Reset Type Studio: Smart Slant, Node Duplicator, Decompose Named
    Components, Set Component Locations and Trial Font Maker;
  - after Reza Bohloul: Magic Remover and Set Intermediate Layer;
  - after Alex Slobzheninov: Paste Glyph Order Encoding, Align And
    Distribute, Rotate Selection, Reflect Horizontally, Reflect Vertically,
    Overlap Nodes, Selection Layer Navigator, Delete Kerning Pair From All
    Masters, Kern To Max, Steal Kerning From Next Pair, Generate Random
    Alternates Feature, Reorder Shapes and Show All Layers;
  - after Resistenza Type: Master Twins, Deliver Glyphs and Style Linker;
  - after Luke Prowse: Master Text Comparison and Common Glyphs;
  - after Simon Cozens: seven Anchors tools, eight Contours tools, Kerning
    Energy Report, Unbundle Punctuation Kerning, Sansomatic, Myanmar Medial
    Ra Maker and Nastaliq Connection Editor.
- PORTING-BACKLOG.md has a new table with every third-party source and its
  disposition: ported, covered by a FontLab command or an existing tool, or
  without a FontLab counterpart.
- Build From Recipes and Unlock Lock address fonts by their FontGate id.
- Autohint Selected Layers and Remove PostScript Hints attribute the TrueType
  and guideline statements to FontLab's source.
- Trial Font Maker needs the public fontTools package (DEPENDENCIES.md).

## Unreleased — 2026-10-21 — Metrics, Components, Masters and Cleanup tools

Add 17 tools adapted from the author's own samples; the active menu grows from
150 to 167 (98 additional tools). 38 of the 61 former archive launchers now
have a port.

- Metrics: Equalize Sidebearings, Sidebearings Tuner and Copy Metrics From
  Reference, on the shared Metrics panel. Preview panels; Apply plans again
  from the live font; outlines move in place; bases of auto glyphs are refused
  unless overridden. Sidebearings Tuner opens on "Add 0", a preview that
  changes nothing.
- Metrics: Vertical Metrics Diagram, a read-only panel that draws H, x, b and p
  of every master against its own metric lines; edit the values in Font Info >
  Master Metrics Table. Alignment Zones stays unported until the App has a
  native zone writer.
- Components: Build From Recipes, Align By Anchor, Decompose, Replace
  Reference, Copy Offsets Between Masters, Unlock Lock and Nested Finder, on
  the App `component_writer` and `component_panel`. Edits are made in place,
  with no shape clones. Decompose and Nested Finder eject one level, restore
  raw flags, names and notes on the copies, and hand the removed components to
  FontLab in the one notification; Edit > Undo of removed components depends
  on FontLab (fl#7641). Shared element data and uncopyable bases are refused.
  Build From Recipes uses FontLab's own builder and always builds plain
  layers; Edit > Undo of a rebuilt existing layer depends on FontLab.
- Masters: Copy Outline To Mask, Copy Layer Between Masters, Restore Backup
  Layer, Layer Cleanup and Sync Sidebearings; Cleanup: Empty Layers (no
  dialog). Shape clones are repaired, backups use FontLab's "@" naming, shown
  and locked layers are kept, and an anchor move to 0, 0 skips the layer
  (fl#8527). Back Up Master Layers stays unported: Duplicate Current Layer
  backs up the current master. Suggest Zones From Overshoots waits for a
  native zone writer.
- Shared rules: every edit except Build From Recipes is recorded as one Undo
  step with one final notification; auto layers are never notified; auto
  owners and bases of auto composites are refused or listed and skipped;
  queued glyph updates are refused; no
  UpdateAll call (fl#8537); every write is read back.
- Wording: the new docstrings carry no acceptance-status lines; the
  Components docstrings use "is recorded as one Undo step".
- Tracking: 17 rows in additional-tools.json, three NOTICE sections, 20 rows
  in PORTING-BACKLOG.md, generated catalogue pages.

## Unreleased — 2026-10-21 — Anchors scripts on the App anchor writer and panel

- Anchors: Rename Bulk, Center Horizontally, Place From Bounds, Snap To
  Metrics, Round To Grid, Delete By Name and Mirror Across Masters no longer
  carry a private copy of the anchor kernel and the 291-line panel base. They
  use `fly.ap.anchor_writer` (plan, safety checks, one-step write, read-back)
  and `fly.ap.anchor_panel` (`panel_type()`, colour helpers); each keeps only
  its planner, its panel subclass and `main` (146 to 190 lines, was 727 to
  772). Changed behaviour: a "set" edit of a name that several anchors on the
  layer carry is also refused at Apply (the planners already blocked it).
  Destination hashes and scope texts of the seven rows are updated.
- App floors: Clear All Layer Backgrounds, Clear Master Backgrounds (were
  0.2.151.dev0) and Perpendicular Guides (was 0.2.154.dev0) now require
  0.2.150.dev0, the App this branch builds. A test keeps every floor at or
  below it.
- Tests: `tests/test_issue122_S5.py` runs the scripts against the real App
  `anchor_writer`, `anchor_panel` and `AnchorPanel`, and checks that no kernel
  or panel name is defined in a script.

## Unreleased — 2026-10-21 — scripts use the shared App and Fontport helpers

- Features: Build Suffix Substitution and Feature Code Viewer read and write
  feature source through `fly.fp.feature_blocks` (Fontport). The App functions
  they used were removed. `menu-revisions.json` records the exact import edits,
  so the released bytes stay verifiable. `test.sh` accepts
  `SCRIPTMIX_EXTRA_REQUIREMENTS` (space-separated) to supply Fontport.
- Metrics: the six advance editors use the App panel, plan model and one-step
  write (`fly.ap.metrics_panel`, `fly.ap.history`); each script keeps only its
  maths, planner and controls (122 to 218 lines, was 657 to 750). Changed
  behaviour: a glyph that owns an auto layer is skipped as a whole; bases of
  auto glyphs are also found through other composites; Apply is refused while
  native glyph updates are pending (the earlier entry said Metrics had no such
  check, which is no longer true); a failure after the write started reports
  "use Edit > Undo"; the status says "N layers skipped (auto)".
- Names: the seven editors scan, refuse and write through `fly.ap.names_edit`
  (on `fly.ap.history`); Suffix Tool and Unicode From Names use the public
  `fly.ap.edit_guards` instead of private App names. Changed behaviour: a base
  of an auto glyph is also found through other composites; after a failed
  write every planned glyph is still stamped and notified, and the message
  says "use Edit > Undo".
- Masters: Duplicate Current Layer, Use Layer As Master, Transform Background and
  Selection To All Backgrounds write through `fly.ap.history.commit`; the four
  layer scripts take the master name rule from `fly.ap.masters.associated_master`.
  The refusal policy is now the App one (a glyph that owns an auto layer, or is
  a base of one, also through other composites, is refused, or skipped by
  Selection To All Backgrounds). Changed behaviour: the refusal, pending-updates
  and failure messages are the App texts ("Refused. a: base of auto aacute.",
  "Native glyph updates are pending", "... did not finish: ... use Edit > Undo").
- Anchors: the seven anchor writers write through `fly.ap.history.commit`
  (operation "geometry", with read-back) and check queued updates with
  `fly.ap.edit_guards.require_settled`; the private history kernel, dependency
  reader and settle check are gone. Each script keeps its planner and its panel;
  the shared anchor panel base stays a private copy in each script (no App module
  fits it). Changed behaviour: blocked rows say "has auto layers" or "base of auto
  X"; the refusal, pending-updates and failure messages are the App texts.
- Provenance: the Metrics and Anchors rows now say `source_body_redistributed:
  true`, like the Names rows: these ports reuse parts of the author's own
  Apache-2.0 samples. The README limits "not copied" to third-party and
  Glyphs-corpus originals. The Anchors scope texts and docstrings say "adapted"
  instead of "independent rewrite"; the Masters rows stay independent rewrites.
  The Raise Ascender row's App floor is 0.2.150.dev0, like the 27 new rows. The
  backlog lists Duplicate Unicodes as a source candidate, no longer unported.
- Docstrings: 38 scripts lose process wording ("reviewed App", "reviewed
  unpublished App ... candidate", "App helper"); they now say "Requires
  App>=..." and "the shared module fly.ap...". The generated pages follow.

## Unreleased — 2026-10-21 — Metrics, Names, Anchors and Masters editors

Add 27 tools, 22 of them non-modal panels; the active menu grows from 123 to 150
(81 additional tools). All are source candidates with offline tests; native
FontLab acceptance is pending for every one.

- Metrics: Italic Sidebearings, Round Advances, Centre In Advance, Zero-Width
  Marks, Tabular Width and Scale Advances, adapted from the author's own
  samples. Preview panels; Apply plans again from the live font; outlines move
  in place; Scale Advances gives the odd unit to the right sidebearing.
- Names: Glyph Tags, Mark Color Palette, Suffix Tool, Batch Rename, Batch Glyph
  Notes, Glyph Notes and Unicode From Names, adapted from the author's own
  samples. Every write rescans the font, never reads the fgGlyph getter and
  reads each value back.
- Anchors: Rename Bulk, Center Horizontally, Place From Bounds, Snap To Metrics,
  Round To Grid, Delete By Name and Mirror Across Masters, adapted from the
  author's own samples. Origin moves and duplicate names are refused; new pins
  get the name-derived appearance.
- Masters: Display Next Layer, Display Previous Layer, Duplicate Current Layer,
  Use Layer As Master, Transform Background, Selection To All Backgrounds and
  Select Different Colour, independent rewrites after Pedro Arilla's Glyphs
  scripts (Apache-2.0). Transform Background and Selection To All Backgrounds
  are panels; the other five run once from the menu.
- Shared rules: one Undo step per font edit, auto layers never notified, bases
  of auto layers refused where the operation could re-resolve them, and no
  UpdateAll call (fl#8537). The Names, Anchors and Masters writers also refuse
  while native glyph updates are pending.
- Tracking: 27 rows in additional-tools.json, four NOTICE sections, 20 rows in
  PORTING-BACKLOG.md marked as source candidates, and generated catalogue pages.

## Unreleased — Categories to XML Lib Key candidate

Add Simon Cozens' complete ordered Mark/base UFO lib fragment workflow using
the existing Glyport category policy through Fly and a shared read-only App
snapshot panel. Escape XML glyph names; reject observed source changes and
incomplete captures. Source/artifact controls are tracked separately from pending
native preservation, lifecycle and release acceptance.

## Unreleased — complete Italic Angle candidate

Add Masters > Italic Angle through the shared App editor. Retain ordered master
spins, original ranges/precision, staged gauge, pending counts and helper/class
interfaces. The candidate manifest has69rows; the preceding68rows and70existing
menu payloads remain unchanged. Released scope remains68/130 until final gates.
Known unsafe native blueScale history refuses changing batches before writes
(fl#8531); no-op batches and the original safe multi-master workflow remain.

## v1.0.18 — 2026-10-18 — two additional foreground reporters

Add Sidebearing Direction Marker and Duplicate Anchor Rings, requiring
fontlab-fontlabapp0.2.23 or newer. Retain the original68migration rows; the two
additional tools have separate provenance/native evidence and do not change
the130sample denominator. Downloaded-tag verification follows this release.

## Unreleased: additional foreground reporter candidates

- Add Sidebearing Direction Marker and Duplicate Anchor Rings through App's
  shared owned lifecycle. Retain explicit direction/handle and foreground scope.
- Track their exact provenance/native evidence separately from68/130sample
  migrations. Full775tests/1historicalskip and two-menu100%coverage pass.
- The prior68 regression passes after the shared App date correction:552original
  checks,196preservation/history and Close68, with extended safety/fault controls.
  Release/downloaded-tag verification remains pending;68/130 stays unchanged.

# Changelog

## 2026-11-10 — Issue 250 documentation round

- AGENTS.md describes the delegation, integration and release workflow.
- WORK.md reset to the current round; the earlier bytes are archived on the owner's workspace data volume, not public.

## v1.0.20 — 2026-10-18 — two additional read-only tools

Add Kerning > Persistence Audit and Reports > Compare Open Font Revisions,
requiring fontlab-fontlabapp0.2.25 or newer. All68original menus and the two
released reporters remain exact. Native result/lifecycle and full prior68 gates
pass; independent downloaded-tag acceptance follows release. Preserve the held
Italic Angle prerelease and its assets separately from this accepted runtime.

## .141 reviewed-source integration candidate

Combine complete typed Symmetry/Cutoff with the current numeric workflows and
the basic Character Map initial viewport. Preserve every prior runtime/menu and
all original filters, pair order, type identities and existing native holds.
Source/artifact evidence does not qualify native/font-history behavior.

## Unreleased — selection context test fixtures

- Model the verified regular Font-window ancestry in the two shared host-free
  fixtures. Exercise actual App selection refusal with an active Glyph window.
- Keep all68Scriptmix menus, runtime modules and migration records byte-exact.

## v1.0.17 — 2026-10-18 — anchor-copy refusal layout

- Fit the owned dialog when a refusal explanation appears; keep a short footer
  status. The anchor preview, explanation and Close controls remain separated.
- Retain the preceding tags unchanged: their numerical acceptance passed, but
  the visual gate rejected overlapping refusal text before canonical promotion.
  New native geometry checks and independent fresh-tag acceptance are required.

## v1.0.16 — 2026-10-18 — Copy Anchors From Glyph

- Retain full L1 source completion, merge/replace, width scaling and master scope.
  Preconstruct native values, preserve existing pins and stabilize new appearance.
  Bind raw coordinates, widths, expressions, selection and every option.
- Refuse automatic dependants before mutation (fl#8512), and existing-anchor
  origin moves that native Redo cannot restore (fl#8527). Keep original previews.
  Installed candidate passes11original/7complete persistence/130native controls
  and Close. Prior67 regression, App597, Scriptmix770+1skip and280installed
  tests per wheel/sdist pass. Downloaded-tag R053 follows release.

## v1.0.13 — 2026-10-18 — compact Master Switcher

- Add original ordered master/location buttons, exclusive current emphasis and
  first9shortcuts on the guarded owned Masters shell. Preserve all60released tools.
  Native original5/preservation2/additional43 pass on3/25masters, including
  actual key events and lifecycle/fault controls. Prior60same-runtime regression
  passes. Source and candidate acceptance reviewed; fresh-tag acceptance follows release.
  Preserve package-master semantics; no editor-layer switching claim.

## v1.0.12 — 2026-10-18 — live Node Coordinates

- Port complete selected-node coordinate/pair tables,400ms polling and Copy.
  Follow active glyph/master edits with guarded font binding and owned cleanup.
  Accept490combined native workflows/145preservation checks andClose60; retain24new timer/Copy/fault/font-boundary controls. Independent downloaded-tag R053 pending.

## v1.0.11 — 2026-10-18 — read-only glyph reviews

- Fix original native feature iteration: use fgOTLayout.keys() tags, not its
  sequence code values; eliminate392false candidates and retain exact395Rafi
  list/selection. New native-shaped tests and unchanged original oracle pass.
- Accept combined59native:483workflow/143preservation/407safety/294error plus
  22selection/layout andClose59; retain all originals and the full130scope.

- Add complete Select Unreferenced Glyphs and Interpolation Preview source tools.
  Preserve candidate/reference rules, all controls and full interpolation painting.
- Reuse guarded lifecycle, source snapshots and safe painters; retain previous57
  menus/rows exactly. Source/artifact/native/prior57 pass; release/R053 pending.

## v1.0.10 — 2026-10-18 — read-only Anchors

- Add complete Anchor Cloud, Anchor Compatibility and Mark Attachment Preview
  source tools with shared raw anchor snapshots and existing owned lifecycle/
  geometry/painter boundaries. Preserve original controls and all54prior mappings.
- Reject stale data without rejecting intended selector changes; retain exact
  None paint diagnostics, explicit current-glyph fallback and complete cleanup.
  Source/artifact/native/prior54 gates pass; integration/release/R053 pending.
- Fix late-binding tree columns after native image review: expose every master
  and missing-anchor cell, with source and native width/count regression checks.
- Accept combined57 native:473workflow/139preservation/368safety/261error plus
  16selection/layout andClose57. Preserve previous54menus and all original inputs.
- Correct the carried Components NOTICE status to its verified release receipts.

## v1.0.9 — 2026-10-18 — read-only Components

- Accept all five installed-wheel native workflows and prior49regression: combined54
  passes453workflow/133preservation/305safety/201error controls,6selection andClose54.
  Fix falsey-current fallback, retain exact empty Compatibility scope and safe painters.
  Source/artifact/privacy checks pass; downloaded-tag R053 is recorded separately.

- Fix the measured CountBadges empty-selection fallback for a valid falsey native
  CurrentGlyph. Resolve selected/current names with original is-not-None rules;
  keep Compatibility's exact selection and prior Proof/scripting helpers unchanged.
  Source proof: App506, Scriptmix620/1skip, Git-free619/2skips; fix2artifact/native
  confirmation remains parent-owned and pending.

- Fix source-review F1: Compatibility's selected scope keeps empty selection;
  CountBadges alone retains its original current-glyph fallback.
- Fix source-review F2: reuse ProofView painter activation/finalization containment,
  exact None success and explicit owned fallback cleanup/Close release. Source-only
  regression proof: App505, Scriptmix618/1skip, Git-free617/2skips; native/artifact
  re-review remains pending. Prior49menus and mappings stay exact.

- Add five complete L1 component inspectors, preserving original UI, ordering,
  selection, simulation, pure CSV oracle and complete native badge drawings.
- Share lazy calculations and existing owned Proof/Names lifecycle; guard exact
  font/master/membership/source drift, opening/paint errors and Close cleanup.
- Append five mappings (54 total) and immutable Git-free prior49 provenance/menu
  byte checks; preserve the prior45 invariant and all original sources.
- Source tests only; independent review, artifacts, native preservation/painting/
  safety/Close and prior49 regression remain pending. No release is claimed.

## v1.0.8 — 2026-10-18

- Fix the prior-45-menu invariant test after commit and in Git-free downloads.
  It now checks a literal canonical digest of immutable v1.0.6 provenance,
  all 49 current rows and the 45 released menu hashes without calling Git.
- Add rejection tests for changed source/destination provenance and menu bytes.
  Explicit arm64 Python 3.11 checks pass: source 504 tests/1 skip and a separate
  Git-free standalone copy 503 tests/2 skips, both against the stable App v0.2.12 wheel.
  No runtime helper, menu, migration or dependency changes. Keep v1.0.7 intact;
  the corrected standalone test distribution requires a new release tag.


## v1.0.7 — 2026-10-18

- Add complete Spacing String Preview, Width Table, Contour Order View and Node
  Statistics with original controls, defaults, class/key/helper interfaces and
  exact native scenario data. No original source is changed or removed.
- Reuse lazy App helpers, existing Proof/Names/Masters lifecycle, actual transformed
  outlines, raw node-polygon winding and contour/node counts. Preserve zero,
  missing and auto values and numeric width sorting.
- Guard initial scans, exact source/current-master/ordered-master domain and
  Whole-font membership. Failed reads/paints clear results and handles, retain
  Close and diagnosis, drain repaint queues and allow explicit same-font recovery.
- Append four provenance pairs (49 total); previous 45 menus/rows remain exact.
  Source/fix review, installed-wheel native acceptance and artifact audits pass:
  41 original workflows,8 complete preservation,10 paint,24 opening,59 safety,
  actualClose 4;70 source hashes and imports match. Node uses its fresh post-seed baseline.
- App 497/actual-wheel Scriptmix 501 passed, 1 skipped and180 installed tests each for wheel/sdist
  pass;66 production files,72 wheel/116 sdist entries and license/NOTICE/privacy match.
- Same-wheel45 prior-tool regression passes379 workflow/115 preservation/166 safety/
  116 error controls/Close 45,113hashes and import restoration. Combined 49 native:
  420 workflow/123 preservation/225 safety/150 error controls/Close 49. Historical 15 chooser
  receipts are retained; no new chooser run occurred. Full 130/archive/held 7 Names stay open.


## v1.0.6 — 2026-10-17

Fix2: native screenshot inspection exposed an inherited tick endpoint defect.
Shared nice_ticks now covers the native plotted range, including max713,
while preserving nice steps and bounded generation. Complete original chart
commands have axis-bounds regressions. Scoped source review and native screenshots pass.

Fix1: refresh scans the actual ordered master domain and refuses mid-scan changes;
Whole-font actions recheck complete ordered glyph membership; repeated failed
chart invalidation schedules at most one clear repaint. New regressions retain
explicit refresh recovery and captured Selected scope. README frontmatter fixed.
Independent fix review and the four-tool native/artifact gates pass.

- Add complete Overview, Width Chart, Glyph Weight Chart and Compatibility Check,
  retaining original controls/defaults/keys/classes, labelled lines and bars,
  structural tree, master-axis order, limits and native DRIVE interfaces.
- Share original twelve-step transformed contour areas/counter nesting, missing
  width/weight semantics and own-contour signatures through lazy App helpers.
  Reuse existing owned panel/signal registry/paint containment, with visible
  initial-read failures, exact source/master action guards and native-handle cleanup.
- Bound tick generation for equal huge ranges so tiny floating increments cannot
  loop forever; normal original chart ticks and numerical meaning remain.
- Keep all41previous menu bytes and provenance rows exact, append four new pairs,
  retain originals/dependencies and consolidate README within200lines.

Installed-artifact acceptance on FontLab9.0.9784 passes43original workflows,
8complete font/workspace/history checks,12real paint controls (axis coverage and
six-event settling),24opening faults,43safety and actualClose4/4. Fresh charts
confirm the clipping fix;67exercised hashes match. App480,actual-wheel Scriptmix413,
163installed wheel/163sdist tests and63production-file parity pass. All45mappings
pass with prior41rows/menu bytes exact. Separate chooser8+7checks use fix1
artifacts with unchanged chooser/common source. Same-fix2-wheel regression of
all41prior tools passes336workflows/107preservation/123safety/80error controls/Close41;
106source hashes verify and imports restore. Combined45:379workflows/115preservation/
166safety/116error controls/Close45.
Full Issue111/archive cleanup and held7Names editors remain separate.

## Unreleased — seven Names editors (source only)

- Preserve complete Batch Rename, Duplicate Unicodes, Glyph Notes, Glyph Tags,
  Mark Color Palette, Suffix Tool and Unicode From Names controls and actions.
- Share lazy App0.2.11 plans/reads/batch writes, complete snapshots, safe opening
  reads, whole-batch preflight, no-op skips and honest partial/post-write errors.
- Retain auto-layer rename refusals, plain component updates, original warnings
  and explicit Reload/Rescan rebinding. Source-only tests; native/artifact gates
  remain pending. Previous41menus/rows and archived originals stay unchanged.

## v1.0.5 — 2026-10-17

Native installed acceptance: all41core tools pass336workflow/107preservation,
123safety,80writer/error controls andClose41; separate15chooser checks pass.
All41hash mappings and60Appsource bytes pass. Full archive migration staysactive.

- Retain complete Glyph Grid, Text By Master, Waterfall and Word Finder tools,
  sharing real transformed paths, exact advance-only runs, original word data,
  filters and guarded owned UI through lazy App0.2.10 helpers.
- Fit Grid's common scale to wide overhangs and tall accents/components; preserve
  deliberate Reload font/selection adoption and refuse automatic stale refresh.
- Clear failed previews, contain painter/callback/finalization errors and retain
  original controls/keys/scenario globals. Copy has host-free coverage; native
  clipboard remains excluded. Installed native/artifact acceptance passes.

### Task3j fix1 — contain all opening font reads

- Build empty controls/status/Close before binding/id/selection/maps/characters/
  master reads; diagnose early failures in a closable invalid panel.
- Retry initial loads through existing guarded controls without adopting a
  different known font. Preserve explicit Grid Reload adoption and Waterfall's
  initial active-master choice with signal state restored in finally.
- Add23actual constructor/recovery/failed-state Close/stale-binding regressions;
  independent source review and installed native/artifact reacceptance pass.

## v1.0.4 — 2026-10-17

Review fix: retain a completed batch's applied outcome, original cause and
Undo/Refresh guidance across all later display/preview failures. Preflight and
partial-write diagnostics stay distinct. Both selected editors reuse the shared
preview-table builder while retaining exact headers and checkbox callbacks.

Add complete Exceptions Finder and Pairs From Text menu workflows. Share original
class precedence, word parsing, explicit/effective previews and ticked plans in
lazy App0.2.9 helpers. Reuse complete snapshot-bound preflight/history writing,
including zero/absence and native save/reopen range refusal; retain all controls,
manual checkboxes, Refresh and owned Close. Failed reads clear pair/value previews.
Append two exact provenance mappings without changing prior35. Host-free tests
pass; all37native tools pass301workflow/99preservation checks,94safety,32writer
and12postwrite controls,15chooser checks andClose37. Full archive migration
and cleanup remain active.

## v1.0.3 — 2026-10-17

Refuse changing batches whose final pairs on any master exceed twice the font's
positive finite units per em: FontLab's load pipeline otherwise clamps them and
adds a mark. Signed32/history validation remains; no values are silently clamped.
Valid corrections/deletions of existing extremes work; true no-op stays untouched.

Add Copy Between Masters, Pair Editor, Scale Values, Round Values and Remove
Small Pairs through shared lazy App plans, snapshots and native batch writing.
Preflight all masters/classes/glyphs and whole-unit history before any mutation;
retain explicit zero, unrelated pairs and active master. Failed reads/stale
previews disable Apply and offer Refresh. Invalid cell text never enters the
staged map; other valid edits remain. All35tools pass280native workflows,85
preservation/history checks,82safety checks,32writer controls,7actual-export
checks andClose35/35. Archived sources stay unchanged; full issue111 stays open.


## v1.0.2 — 2026-10-17

Add Classes Browser, Compare Masters, Pair List Browser, Missing Pairs and Text
Preview under Kerning. Require App0.2.7 helpers. All30tools pass247native workflows,
50preservation/history,52safety,7actual-save-dialog checks and nativeClose.
Host-free171tests and30provenance pairs pass. Remaining editors/archive migration,
new tools/reporters and final cleanup remain open; original inputs stay retained.


## v1.0.1 — 2026-10-17

Add Case Pairs, Character Info, Character Set Compare, Glyph Finder and Select by
Mark. The live outline specimen fits tall accents and side overhangs. Require
App 0.2.6 helpers; tests accept an explicit tag-built wheel without assuming index
publication. All 25 tools pass 216 native workflows, 40 preservation/history checks,
44 safety checks and native Close destruction. Host-free tests: 151 passed.
The full archive migration, new scripts/reporters and final cleanup remain open.


## Unreleased — Names inspection tools

- Share lazy Names panel/table/lifecycle and complete-refresh selection guards.
- Preserve five original tools, Unicode/language data, live outline proof,
  copy, keyboard and row actions; keep/add selection validates all names first.
- Retain all source originals; native verification of this batch is pending.


## v1.0.0 — 2026-10-17

First 20 practical tools: eight Reports, six Font Info panels and six Features
panels. Install current Fontlabapp helpers and fly in FontLab 9's Python 3.11.
The five editors pass complete preservation, Undo/Redo and saved-font reopening.
All 20 tools pass 183 native workflow checks and native Close destruction.
Host-free tests are portable: 113 pass from an isolated archive with the actual
App v0.2.5 wheel; original-source auditing is explicit and fails closed.
This release is a verified migration milestone. The remaining archive migration,
additional tools/reporters and workspace-wide cleanup are still in progress.


## Unreleased

- Five more complete Reports tools pass original native scenarios on9784:
  Live Glyph Info, Glyph Table CSV, Label Statistics, Nodes Near Zones and
  Unicode Coverage.42independent checks, screenshots and cleanup pass; full
  Python3.11 test suite47passes. Source provenance remains recorded.

- Migrate Empty Glyphs, Open Contours and Font Overview with original tables,
  filters, multi-master calculations and persistent modeless lifecycle.
- Clear stale display data on no-font refresh and bind selection to scanned id.
- Record source hashes/license and add host-free behavior tests.

## Issue 111 review round 1

Fixed failed-refresh selection: invalidate the prior snapshot before native
access, scan into local rows, populate the full table, then publish rows/id. Any
scan or display exception clears partial table data, keeps selection disabled,
and rejects direct select_rows calls. Four regression cases first failed against
the old code (genuine RED retained), then passed after this fix.

Controller native acceptance: all three reports pass their original scenarios
on FontLab9.0.9784 through the installed helper wheel, with26independent checks,
reviewed screenshots and complete owned font/dialog cleanup.11host-free tests
pass on Python3.11. This is the first issue111 batch; broader work remains open.

## Issue 111 second Reports batch

- Migrate Live Glyph Info, Glyph Table CSV, Label Statistics, Nodes Near Zones
  and Unicode Coverage with original UI, scans, scope, timer and CSV behavior.
- Invalidate snapshots before host access and publish only after full display;
  reject selection after a font switch or failed refresh. Preserve Add selection.
- Retain originals and record hashes/provenance; add owned-data behavior tests.
- Native acceptance remains pending for these five scripts.


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

## Unreleased — six Features tools

Migrate the six complete feature tools with original controls and Apache-2.0
provenance. Reuse the App panel lifecycle and Fontport's ordered feature writer
for actual suffix appends. Bind Apply to the complete source snapshot and glyph
references; preserve unrelated source/order/prefix/classes, reject stale plans
and contain proof painter errors. Native acceptance remains pending.

Task3d review fixes: share host-free suffix/FEA calculations, document concrete
row contracts, and load the Feature Code Viewer from exact ordered VFJ source
instead of native index iteration/synthesized prefix. Native rerun pending.


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

## Issue 111: portable host-free checks

Resolve actual App helper sources from an explicit installed dependency or source
override. Distribution checks always cover 20 scripts; original-source hashes
are an explicit fail-closed workspace audit. Document wheel-based uv testing.

## Issue 111 Names review fix 1

Fit complete Character Info outlines including tall accents and side overhangs
inside the padded proof area while keeping baseline/labels/system proof.
Centralize exact Font window selection reads and correct character-list docs.
Host-free geometry regression passes; native fix rerun remains pending.

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

## Issue 111 Names dependency guidance fix 2

Require App0.2.6 in test-runner guidance and document tag-built wheels separately
from package-index availability. Refuse resolved helper trees missing the Names
panel. The installed final-wheel suite passes151tests with25provenance pairs;
product scripts and manifest are unchanged.

## Issue 111 read-only kerning implementation (native acceptance pending)

Add Classes Browser, Compare Masters, Pair List Browser, Missing Pairs and Text
Preview with every original control and original registry/class interfaces.
Share the lazy panel shell, guarded callbacks, validated selection, all-master
explicit pair/class reads and effective native kerning layout through App.
Preserve explicit zero versus missing pairs, numeric sorting and shown-order
UTF-8 CSV. The owned modeless chooser reports pair count and basename in a
wrapping status label. Proof fits complete transformed ink with actual advances
and native class fallback; paint and cleanup failures are contained. Invalid
or switched-font snapshots refuse selection, export and Copy. These five are
read-only; Exceptions Finder and Pairs From Text remain later editor work.
No native acceptance, publication or archive-removal claim in this milestone.

## Issue 111 Kerning review polish

Clarify Missing Pairs data types/coverage and Text Preview empty-state docs without
changing behavior. Make the new public work-log commands portable and retain exact
private receipts separately. App source remains identical to the native-tested wheel.

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

## v1.0.14 — 2026-10-18 — complete guide panels

- Add complete Font Guides Panel, Grid Generator and Metric
  Reference Lines on the shared owned UI. Refuse unsafe automatic dependants
  before history. Safe edits restore complete fonts and prior Undo state.
  Native27original/21persistence/167controls/Close3 pass; all61prior tools pass
  on the same installed runtime. Artifact/source acceptance reviewed; fresh-tag
  acceptance follows release. Retain every original and the full Issue111 scope.

## v1.0.15 — 2026-10-18 — complete guide rewrite editors

- Add complete Clear Glyph Guides, Copy Guides Between
  Masters and Guide List Editor. Preserve retained native guide properties/hints,
  preconstruct whole batches and refuse unsafe dependencies/nonfinite cells.
  Native19original/21persistence/162controls/Close3 and prior64same-runtime
  regression pass. Current580App/756Scriptmix/263installed per artifact pass.
  Source/artifact/native acceptance reviewed; independent fresh-tag R053 follows
  release. Retain every original and the full Issue111 scope.

## Unreleased: two additional read-only tools

Add Kerning Persistence Audit and Compare Open Font Revisions as thin fly.ap
menus backed by shared Fontlabapp implementations. Include source/identity guards,
local result details and owned callback teardown. Preserve the68 original menus
and the two released reporter records. Native candidate checks are retained;
isolated artifact/regression/release acceptance remains pending.


## Unreleased — issue120 tabular width report

Add a practical Apache-2.0 Pedro Arilla tabular-width report through shared App
and Fly. Compare actual selected active-master advances exactly; retain original
row statuses, counts and time heading. Use a modeless read-only snapshot with
Refresh and owned Close; diagnose empty, missing or changed sources. Preserve
owner Output content. Source/consumer/artifact checks pass; native acceptance
and release remain pending. This is additional to the130sample inventory.


## Unreleased — component recipe report candidate

Adapt Simon Cozens' MIT Recipe Dumper into shared App logic and a typed lazy
Fly menu. Preserve ordered/duplicate layer and component records, mixed layers
and original line endings; do not synthesize offsets or transforms. Native
capture currently binds Font-window selection on the active master, with stale
source/carrier/deadline guards. The owned modeless report supports Refresh,
clear failure diagnosis and Close. Original editor-tab/repeated/multi-master
selection and native acceptance remain open; the130sample count is unchanged.
Angularizzle remains an explicitly unfinished named priority requirement.


## Unreleased — Angularizzle workflow candidate

- Add the original Min plane/Keep detail/Process/Cancel workflow with ordered
  repeated selections, first-master targets, saved defaults and bound previews.
- Refuse stale or unsupported source plans before history; retain diagnosed
  recovery state after late native failures. Native acceptance remains pending.
- Restore actual overwritten target paths on Cancel, repairing the original
  cross-layer restoration defect. Closing keeps Process results.


## Unreleased — Recipe Dumper selected-layer adapter

Read actual ordered Font/Glyph-window layers through App’s shared selection
provider, retaining repeated editor slots and their layer choices. Compare
component reads and fence final selection/context before publishing. Native
qualification and complete font preservation remain pending.


## Unreleased — Tabular Width Checker selected layers

Use the shared Font/Glyph-window selection reader. Preserve editor repeats and
each slot’s layer choice; compare exact actual advances against the first
occurrence. Fence source/selection/context under one deadline before reporting.
Native selected-layer order/focus/preservation qualification remains pending.


## Issue120 M1 candidate

- Add licensed Slobzheninov Point Counter with complete foreground-layer/repeated-selection reports and explicit quadratic counting repair. Native acceptance remains pending.
- Expose the report through a typed Fly menu; original69 migration records remain unchanged.


Issue120 Q1 candidate: add all-open-font/all-master Vertical Metrics Reporter, eight exact stored values, unset/zero distinction, complete-source fences and owned Refresh/Close text panel. Native acceptance pending.

Issue120 R1 candidate: seven complete random-proof generation/tab workflows; preserve all4,991dictionary entries, draw order, casing and whitespace. Explicit current-font repair; native acceptance pending.

Issue120 T1 candidate: eight selected-glyph context proofs with exact order/repeats/contexts/blank lines, explicit native named symbols and a fresh-tab writer fence. Native qualification pending.

Issue120 W1 integration candidate: 93 practical and 61 preserved-source menu facades consolidated without copying/executing archive bodies. Native and distribution acceptance remain pending.

Issue120 Y2: verify current App completion hooks with accurate dialog-signal
doubles and real host-free helper loading; four actual Proof completion controls.
All practical/archive menus and provenance unchanged; no new native acceptance.

Issue120 Z1: complete Text Simplifier candidate with regex-class filtering,
input/read-only output/character fields, autosave/reopen, selective Reset,
original-font optional proof tab, resizing/geometry and owned completion.
Native PythonQt/settings/tab/whole-font-history qualification remains pending.

Issue120 Z2: complete selected-master Tallest and Shortest and all-foreground
Highest & Lowest Glyphs candidates share exact extrema/native capture and new
per-symbol layer tabs. Stable ties/repeated winners/zero/large coordinates are
preserved; missing layers are never created. All-layer coordinate results use an
owned panel with Run Again and survive a diagnosed tab failure. Shared NamesDialog
subtitle colour now follows palette changes. Native qualification remains pending.


Issue120 Z4: complete Why You Not Compatible? report candidate compares every
adjacent foreground-layer pair for each selected occurrence: ordered path/node
counts/types plus anchor/component name sets. Keep repeated groups, master-first/
auxiliary order and source messages; fix foreign first-glyph labels and global
path suppression, and sort displayed name sets. Owned Refresh/Close replaces
Output writes. These source checks are not an export-compatibility certificate.
Actual native topology/order/read/cache/font/history/reopen acceptance is pending.


## Issue120 current documentation Z5

A source-backed catalogue documents all158 current menu scripts without importing them. Hash-named build snapshots retain complete sources even when filenames contain parentheses, accents or apostrophes. Runtime menu bytes are unchanged.


## Issue120 documentation quality Z7

Documentation SDK tests now live under tests_docs and run in the locked documentation environment. Runtime tests stay on Python3.11. The real push gate combines both measurements without exclusions or a reduced threshold. No runtime menu body changes. All1070runtime/root tests pass with1existing skip, plus4SDK tests. The fixed coverage scope now includes the complete src_docs production root and all prior Scripts; the accepted baseline commit is unchanged.

These local gates do not establish native/font/history/reopen or site-publication acceptance. Exact commands and retained failures are in the parent verification/issue-120/docs-quality-z7/.


## Issue120 Z9 — bracket-layer report and proof candidates

Both Reset Type Studio source workflows now scan the complete current font's
foreground layer names and transitive component dependencies. Shared App core,
full-source observations and report/tab routes preserve both original groups.
The report explains overlap and counts a distinct total; the proof sorts names
and uses explicit glyph symbols, avoiding orphan slashes. Apache attribution
and the full licence are retained. Source originals are never executed.

Owned Qt6 controls and host-shaped boundary tests are offline evidence only.
Native PythonQt, dependency/cache/read preservation, complete saved-font/history
and actual symbol/layer mapping remain pending under D25. No native acceptance,
canonical merge, live install, tag, release or site publication is claimed.

## Issue120 Z24 — browser notices

Add source-bound full texts and provenance for named frontend components, including transitive JavaScript dependencies, icons, shared theme inputs and external font responses. Keep the full transitive/publication review explicitly open; runtime assets and retained archives are unchanged.

Z24 preservation found that the previous docs output path cleaned the authored integration guide in the isolated worktree. Restored the exact tracked guide, retained the earlier generated output in private evidence, and changed output to `.build/site/`. A tests-first regression rejects overlapping authored/output directories. No canonical source was changed. Fresh strict-build/preservation evidence is required below.

## Issue120 Z26

Preserve exact upstream notice bytes through Git filters, fresh checkout and archives; add a CRLF distribution regression. Source manifests and pending publication scope remain unchanged.

## Unreleased — isolate temporary notice repositories

- Clear Git's documented repository-local environment for temporary notice
  distribution commands and bound each child call to10seconds.
- Exercise inherited hook context with both default and alternate parent indexes;
  require byte-exact preservation of parent config, refs, index, objects, files
  and caller environment. Keep every notice/filter/checkout/archive assertion.
- Preserve all upstream notice payloads and existing attributes/manifests.
  Source-only correction awaits fresh independent review; no new commit/push.


## 2026-10-20 — curated active menu

Keep 99 practical tools in one-level Title Case menus. Retire 61 archive
dispatchers from active Scripts; preserve every unfinished tool and source hash
in the visible porting backlog. Prevent stale sibling bytecode in active menus.
Regenerate the catalogue from actual menu sources. Native acceptance for new
candidates, the original 130-sample migration and the broader scope remain open.


Known already-current migration rows now resolve idempotently through the same
reviewed move overlay as historical rows. Preserve manifest bytes and source
metadata. Unknown or ambiguous routes and changed hashes/bodies are refused.


## N48 — anchor-copy helper typing

Declare the existing rounded integer-point and optional native-glyph types in
Copy Anchors From Glyph. Add short purpose docstrings without changing executable
statements or imports. The glyph annotation is quoted and uses the existing
Fly-backed fontlab alias. Record the two exact source edits in menu-revisions.json;
current menu hashes and exact historical release bytes remain independently
verifiable. Historical migration rows and original-source hashes are unchanged.

## 2026-10-21 — three contour tools in the curated menu candidate

Add only the reviewed Select Contours, Select Small Contours and Select Partial
Contours facades and their exact independent Pedro Arilla provenance. The
curated source menu grows from99to102; its original99files remain byte-exact and
all61archived dispatchers remain excluded. Preserve menu_layout.current_rows,
owner-compatible manifest representations and every existing frontend notice.
Native acceptance and the full retained Issue120 requirements remain pending.


## N51 — combine reviewed contour menus and anchor typing

Combine source-reviewed and independently pushed N39 contour menus with N48
anchor helper annotations/docstrings. Retain the exact 99 N48 menu bytes and add
exactly 3 N39 menus, with their existing attribution and pending-native scope.
The source union introduces no additional runtime edits. The original 127 active
origins remain retained; all sample/archive backlogs and native gates stay open.

Full installed App0.2.73/Fly source checks pass 982 tests/one explicit skip plus
10 documentation SDK tests. The unchanged quality gate reports 94.95% aggregate
changed-production coverage above all configured 80% floors. A private owner
overlay rehearsal retains the raw manifest, 13 literal files and 2 bounded historical/
current-view test adapters plus 7 merged owner docs; it repeats 982/1 + 10 tests and
the strict offline build. Canonical application and native acceptance remain
controller-owned and pending. Exact receipts live outside the public tree.

## Unreleased — complete reporting pair candidate
Add first-master node compatibility counts/first differences and own-path SVG
commands with shared Refresh/Close panels. Fix original false-compatible cases;
retain unconditional Z policy and refuse unsupported whole reports. Native pending.


## N68 Same Kerning Groups proof candidate

Implement the complete first-selected-glyph left/right peer proof, independent class maps, font order, explicit named peers, literal labels and original empty/singleton diagnosis. Native acceptance pending.


N68 repair round1 (.82): preserve first selected parent only, without layer or later slot/block-ID reads. Peer-side resolution is conditional on current groups; no-group diagnosis skips the peer inventory. Prior .79/N75 failures retained; 53 focused controls pass. Whole ordinary artifact/native qualification receipts: verification/issue-120/kerning-group-proof-z31/repair-round1/. Native acceptance remains pending.


## N105 Close But No Cigar (.93 source candidate)

Complete ordered all-selected-parent/first-layer near-angle, horizontal/vertical
stem and six node-position checks, with explicit associated-master data and
strict original boundaries/exclusions. Shared modeless Refresh/Close report;
no Output/font/selection writers. Numeric cubic angle repaired; original curve
sampling/open wrap preserved. Tests, source/API calibration and ordinary
archive verification: workspace verification/issue-120/near-miss-z35/.
Native acceptance, root review and delivery remain pending.

## Issue120 N119 — complete duplicate-anchor source candidate

Retain the complete original all-master duplicate removal workflow, exact first-in-layer/name-family/coincident policies, opening-selection scope and auto-layer skips. Direct original pin removals use preflight and one final layer/glyph notification; partial failures remain explicit for Undo. Native one-Undo, whole-font/history/dirty/save/reopen and lifetime acceptance remain pending. No native/live/canonical operation occurred.


N97 Text Holder candidate (.91): full editable/resizable floating window; literal
Find first/highlight; UTF16-correct selected-or-whole replacement; Save stays
open, Save & Close, Ignore & Close; owned-path UTF8 persistence and window size.
Source/licence disposition retained; no original body is copied or executed.
No native calls or user-store validation. Native acceptance remains pending.

N97 geometry repair: preserve initial content500×400 separately from source
NS frame min500×400/max1200×800. Persist decorated frame sizes, restore client
sizes by measured chrome and map literal Cocoa origin(0,500) through complete
primary logical screen geometry/current frame height after first show; no
availableGeometry, DPR scaling or silent clamp. Prior .91 commits/artifacts
are retained in attempt2; no immutable final .91 freeze existed before repair.
27 focused actualQt5 controls pass; independent geometry controls pass bothQt5
andQt6. Native qualification remains pending on root final combined .92.

N97 final source fidelity: use normal Qt.Window with stays-on-top and explicit
title/system/close/minmax hints, matching original Vanilla Window/NSWindow
role rather than Tool/NSPanel hide-on-deactivation behavior. Preserve literal
button ampersands, full frame constraints, Cocoa origin and saved frame sizes.
Producer28 actualQt5 controls and independent32controls perQt5/Qt6 pass;
ordinary final .91 artifacts and full declared147/42 gates are bound separately.
Native acceptance remains pending on root combined .92, never claimed for .91.

N97 literal-Unicode repair revision4: frozen8433...candidate retained as failed
source attempt after independent NBSP/LS/PS Find/Save counterexamples. Added
text_holder_editor with undo-aware native block separator provenance; literal
block.text reads preserve NBSP/LS and distinguish PS/LF. Controlled text ingress,
local mime copy/paste, native Return, IME, selection merge and Undo/Redo preserve
literal text; original disk universal-newline read remains unchanged. Four
owned modules; complete App milestone scope grows148, Scriptmix stays42, no
sample denominator changes. Qt5/Qt6 focused51controls each pass at this stage.
Native acceptance remains pending on root combined.96 onto.94; .92 prep is
historical and .91 remains a private source candidate, never native acceptance.

N97 ownership repair revision5: independent pinned PythonQt virtual-return source
identified an ownerless Python-QMimeData lifetime seam (host binary equivalence
unproven). The copy factory now returns the explicit nativebase Qt-owned object;
its lazy source fragment is materialized before clear/setText, preventing a
later default MIME read from overwriting the literal payload. Constructor-route
tripwire is RED on revision4 source/GREEN now.52producer Qt5/Qt6 controls pass.
Revision4 ordinary archives eef6ac94.../305df303... and full148/42 gates remain
retained as a prior source attempt, with no immutable candidate promotion.
Fresh revision5 ordinary artifacts/full unchanged gates bind this repair.

## N145 .118 Point Counter literal selection repair

Import complete Reza master-layer report on reviewed .106, preserving its prior workflows.
Reuse unchanged Text Holder literal editor read-only; preserve NBSP/LS/PS and UTF16 selections.
F1 RED, complete artifacts/consumer/coverage results are recorded after verification. Native pending.

N145 final .118 source/artifact gates:27focused controls pass source Qt5/Qt6
and all4installed Qt/archive lanes;4actual public Fly/menu literal-MIME controls pass.
Both complete7consumer graphs pass13752tests/3existing skips. Original whole scopes
182App/45Scriptmix/70Examples pass80statement AND80branch perfile, zeroexclusions.
Scriptmix15SDK/docs tests and strictbuild pass; unchanged .106 Examples docs coverage
is reused byte-exact with explicit attribution, no write to that frozen tree.
F1selection RED and readonly IME REDs retained. Literal helper byte-exact to .106;
report-local IME ignores all preedit/commit. New report PythonQt/native probe pending.
Exact commands/exits/archives/receipts: verification/issue-120/point-counter-repair-z43.
No native/canonical/push/user-store/clipboard changes. Independent review required.

Added complete Dangerous Offcurves full-font probe action and exact-layer proof tab; explicit fontTools analytic ordering adaptation.


N157 finite-probe numerical repair (.120): exact control-hull exclusion prevents
rounded solver hits for curves strictly beyond either finite probe endpoint.
Exact endpoint coordinates replace rounded backend endpoint hits only when
source fixed-coordinate equality and finite bounds prove the hit. All four
probes, strict0.05 predicate, traversal, owned result and real-layer tab workflow
remain. Ascending curve-time ordering stays an explicit adaptation; Glyphs
engine equivalence and complete FontLab native acceptance remain pending.

N160 retained first .120 artifacts as a failed attempt: an outside exact endpoint
can round onto a finite probe even with overlapping hulls. Drop numerical t0/t1
hits before restoring only valid exact source endpoints; interior roots survive.


N162 combined source candidate: The combined App0.2.122.dev0 source candidate adds Reports > Point Counter (Master Layers) and Dangerous Offcurves, preserving all prior109menus and both complete original workflows. Dangerous Offcurves uses explicitly adapted ascending fontTools curve-time intersection order; opaque Glyphs engine equivalence remains unproved. Literal text is checked after publication; a lossy literal NUL is refused and remains a native host hold. Source/artifact verification does not complete native/font-history preservation acceptance.

## Duplicate Unicodes .121 candidate

Complete whole-font checkbox cleanup editor through shared App/Fly, preserving primary-owner defaults and ordered surviving assignments. Adds stale/preflight/partial-write handling and single final history notification; original native getter/UpdateAll paths are not used. Native qualification remains pending.



N185 private source candidate: complete all-master Kerning Cutoff action retains inclusive[-250,100], explicit pair kinds and per-master counts; repairs earlier-master-only notification with the qualified batch writer. Native qualification pending.


N193 test compatibility: the owned kerning fixture exposes the resolved package search path instead of preventing genuine shared helper imports. All menu bodies and runtime requirements unchanged.


## Unreleased .137 — Complete typed kerning symmetry

Add the complete Science Gothic 28-target/378-comparison Symmetry writer with lossless explicit glyph/group identities, sequential class aliases and zero deletion. Preserve original # and case-sensitive Ctr master exclusion. Cutoff retains its distinct all-native-master policy. Native qualification pending.

N226: private .145 coherent union on reviewed .141; complete admitted CopyAnchors/shared scalar-style reader .144 and TextHolder/literal helper .139revision3 retained. Fresh artifacts/full consumer/Qt/whole-original coverage verification pending; full native qualification remains separate. No host/canonical/live install writes.

N235: integrate complete reviewed literal TextHolder/anchor tools, both literal Find Files profiles and generic Qt table items without replacing prior workflows; host acceptance remains pending.

## N236 — complete four kerning proofs

Add Hoefler Lowercase, Hoefler Uppercase, KernKing and KernSym through shared App/Fly. Keep all five exact licensed texts and KernKing two-tab order. Preserve Output. Ordinary artifact/current consumer/whole-module verification follows; full native tabs/font/history acceptance remains pending.

### N228 — paired whole-font background cleaning candidate

- Add distinct all-layer and declared-master background removal tools through Fly/App.
- Remove original whole mask objects; reject ambiguous mapping and automatic dependencies before history.
- Contain partial native failures with one final notification and explicit Undo diagnosis. Native acceptance pending.

### N239 — background failure and active-state repair candidate

- Always attempt one final notification after attempted removal, aggregate individual pre/post stamp and notification errors.
- Use nonassigning active resolver; active/locked backgrounds remain explicitly unsupported original-domain gates.
- Prepare survivor identities in checked per-glyph passes before history, and fence final staged sources/queue.
- No native acceptance or reconstructed background rollback.

N248 complete .153 union retains reviewed .148 and all four .149 proof workflows/five licensed texts, both complete .151 background cleaners and final admitted .152 Character Map contrast. Preserve full original workflow/coverage denominators and all prior menus. Active/locked backgrounds remain UNACCEPTED; all native font/history/reopen gates stay open. No canonical/native/live installation/push.

- Private .159 integrates complete Raise Ascender with reviewed .157 failed-Close lifetime repair; all original font/history domains remain pending.

- Private .159 includes complete reviewed Perpendicular Guides: selected nodes and component centre guides, first-selected-layer scope, transformed geometry and retained carriers; native full-font/history acceptance remains pending.

## Unreleased — Cursive sample window ownership

Parent the sample chooser and warning to FontLab and preserve window flags while requesting panel priority. Retain owned cleanup on configuration failure; sampler and exclusive-create semantics unchanged. Qt test doubles now model priority flags. Full gate retains independently reproduced baseline provenance failures; no native or publication acceptance.

## 2026-11-01 — background menus installed integration and scope wording

Both actual background menu entry points pass11standalone integration cases through
installed Fly0.2.2.dev7+g78cc4b348 and App0.2.26.dev158+g55fc09868. The installed
backend and planner remain real; native objects/context use owned doubles. Qt6
panels are actual widgets: priority flag, nonmodal visibility, preview before
history, two scopes, no-op, stale/partial failure, warning once and owned deletion.
Shared master/auxiliary masks pass all-layer mode and refuse master-only mode.
Correct the all-layer menu docstring to match that measured source contract;
refresh its additional-tools hash and generated catalogue page. No runtime change.
New source SHA256 a4b1cb0bbfe4df66545bc282b9d85bdc4f97a979c24c5d726ab7d971e094b676.
Historical hashes above remain historical evidence.

All173additional pins and242archived Python menus match. Installed366App and1Fly
runtime files match source bytes. Ten documentation tests pass. Independent
read-only review finds no blockers. Native stacking/full-font history/reopen and
full-cohort acceptance remain open. Existing58full-suite failures are not cleared;
no full-suite rerun for docstring-only change, no push, publication or promotion.

Evidence: external issue123/background-menu-20261101.
Commands from that directory:
- `rtk proxy env PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 QT_QPA_PLATFORM=offscreen ./env/bin/python -I -B -m pytest -q -p no:cacheprovider tests/test_menus.py`: exit0,11passed.
- `rtk proxy ./env/bin/python -I -B verify_bytes.py`: exit0.
Candidate cwd:
- `rtk proxy env UV_CACHE_DIR=/Volumes/Falstaff4T/fontlab-scripting-data/uv-cache TMPDIR=/Volumes/Falstaff4T/fontlab-scripting-data/tmp PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --python /opt/homebrew/bin/python3.11 --with pytest --with mkdocs-codeinclude-plugin==0.3.1 --with PyYAML python -B -m pytest -q -p no:cacheprovider tests_docs`: exit0,10passed.
The first archive check assumed242total files but found5extra historical .DS_Store
entries. The final menus-final.tar includes exactly242Python menus and no others;
no .DS_Store copied into the executed bundle. Failed setup logs retained.

## 2026-11-01 — Integrate reviewed Master Text menu

The App159 candidate already contains the reviewed MasterBlaster workflow, but
this Scriptmix branch still launched its old standalone implementation. Restored
the exact reviewed a549976b menu and its focused routing test, corresponding G10
test migration and documentation. All surviving G10 test functions have identical
ASTs; former local-panel behavior is covered by73fresh shared App tests.
Updated only its additional-tools row, preserving all172other rows; menu hash and
docstring/source link match. Corrected backlog acceptance to native-pending.

Evidence: external issue123/master-text-reconcile-20261101/. Initial routing test
failed against the old menu (menu-red.log, exit1); final20scoped tests pass
(menu-final.log, exit0). App73tests pass with standalone PySide6 (tests-qt.log,
exit0); initial reused environment lacked PySide6 (tests.log, collection exit2).
AST-only original-source extraction confirms all four fallback values exactly,
without executing original code.

Full Scriptmix current gate:57failed4381passed19skipped; preserve failures and
compare the unchanged base in the same environment before promotion. No native
acceptance, canonical promotion, push, site build or publication. A trial isolated
App-minimum correction exposed the whole-cohort assertion, so the existing
provisional0.2.150.dev0 field is retained unchanged and remains a release blocker.
The tested installed dependency is genuine App0.2.26.dev159+gb1e905b61.

Same-environment baseline6a769d2e:57failed4402passed19skipped; all57failure IDs match candidate exactly (failure-comparison.json). The21net fewer passing cases follow removal of22obsolete standalone-panel cases and addition of one shared-controller routing case; shared App retains73passing workflow tests. Neither full gate passes.

## 2026-11-01 — Genuine App source baseline

Replaced139active provisional App minima with conservative0.2.26.dev159. This
is a current source baseline, not a claim of earliest historical per-tool support
or whole-menu compatibility. App159 still lacks the pending zone handoff.
Updated42menu docstrings, destination pins and mirrored source pages; executable
ASTs remain identical. Frozen migration.json and original-source hashes unchanged.
Removed the pretend-version testing recipe, supplied genuine wheel examples,
updated test.sh guidance and qualified historical dependency/setup notes.

The former branch-constant test passed against invented metadata. Its replacement
compares every recorded floor with actual installed fontlab-fontlabapp metadata:
RED1failed before repair (red.log, exit1), GREEN2floor checks (floor.log, exit0)
using genuine0.2.26.dev159+gb1e905b61. Exact test command from this checkout:
`rtk proxy sh -c 'PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Volumes/Falstaff4T/fontlab-scripting-data/issue123/current-cohort-20261101/env/bin/python -B -m pytest -q -p no:cacheprovider tests/test_curated_delivery.py -k app_floor'`.
Full suite uses the same command with `tests` instead of the file/filter.
Evidence root: external issue123/scriptmix-real-floor-20261101/.

Invariants:242menus compile;173additional pins exact;139floor fields and42hash
fields are the only manifest deltas;42page docstrings/source hashes match; all42
runtime ASTs unchanged. Independent read-only review approved with no blockers,
limited to source/metadata consistency. `rtk proxy /opt/homebrew/bin/git diff
--check` exits0. No runtime dependency is added to the docs-only pyproject.
Native proof, complete cohort integration, promotion and publication stay open.

Full suite exit1:57failed4381passed19skipped; counts and all57failure IDs match base aa6740e in the same environment (failure-comparison.json). The full gate is still failing; matching IDs do not qualify its affected workflows.

## 2026-11-01 — Complete retained selection integration

Integrated the retained Select Different Colour fix: empty Font-window selection
returns before CurrentFont/mark reads and selection/history writes. The original
only adds selection when selected colour indices exist. Whole-font scope remains
different from the original displayed-cell domain and is explicitly unqualified.
Updated the additive-selection assertion to App159's no-clear contract, retaining
selected-name, unknown-name and stale-package checks.

Fresh RED:3colour cases fail before the menu fix. GREEN:181G1/Names tests pass.
Command from this checkout: `rtk proxy sh -c 'PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
/Volumes/Falstaff4T/fontlab-scripting-data/issue123/current-cohort-20261101/env/bin/python
-B -m pytest -q -p no:cacheprovider tests/test_issue122_G1.py tests/test_names.py'`
(exit0; focused.log). RED uses G1 with `-k different_colour` (exit1; red.log).
Full command substitutes `tests` and is retained as full.log. Evidence directory:
external issue123/selection-integration-20261101/.

Independent bounded review approves source/test-contract changes with no blockers.
All173additional pins verify; only this menu's hash changes, all139genuine floors
and every other manifest field are unchanged. Docstring/source-page link matches.
Diff check exit0. Original source only read/hashed, never executed.
No canonical edits, native calls, promotion or publication. Native filtered-view
selection, complete preservation and full cohort acceptance remain open.

Full exit1:56failed4384passed19skipped. The obsolete Names expectation is the sole removed failure; no new failure IDs. Remaining39zone and17provenance failures are unchanged. The full gate remains failing and cannot authorize promotion.

Private .161 adds complete Jens Kutilek composite-difference and all-other-font glyph-set reports with source-defined reference/target/order/filepath policies and owned selectable output.

Private .154: add complete first-selected-layer Perpendicular Guides action, including selected controls and transformed component centres; existing guide objects retained and one final history notification. Native qualification pending.


- N240 private .150: complete original Raise Ascender controls and ordered node planner, staged native writer and per-occurrence history. Explicit unsupported native boundaries remain pending; no native acceptance.

- N257 repair .155: stop retained error callbacks accessing deleted Raise Ascender controls after successful normal Close; preserve live failed-Close diagnostics/retry. Shared completion and original actions/native limits unchanged.

- N263 repair .157: restore owned destruction tracking after a failed Close helper stopped completion, preserving live diagnosis/retry and inert late callbacks after parent death.


N188: independent complete cross-font Copy Anchors candidate on reviewed.122.
Source-boundary and realQt controls in progress; no native acceptance yet.
Exact commands/receipts: verification/issue-120/crossfont-anchors-z48 (workspace).

N208 (.140 private): repair integer advance fidelity, preserve exact native-derived caret cloud/mark expectations, and stage complete native insertion-name normalization with owned detached cleanup. Original variants and all options retained. RED-first failures and focused repairs retained; final artifacts/native calibration remain pending. Prior .134 revision2 is unchanged.

N208 .144 shared native-style repair: root9787calibration measured pin.style="FreePosition". Preserve its actualscalar in shared anchor_duplicates_capture.pin_value; both AnchorDuplicates and Crossfont use the same correctedreader. Prior .140 remainsimmutable/held. Explicit single priorruntime exception; all otherpriorbytes retained. Six stringstyle/stale controls are RED against ordinary .140 then GREEN on sharedrepair; legacyintegercontrol also retained. Full .144 artifacts/gates and remainingnative naming/fullfont qualification pending.


N186: add complete Science Gothic Kerning Symmetry writer, all configured pairs/non-Ctr masters, exact native zero deletion and class-order diagnostics. Shared whole-batch history repairs final-master-only notification. Native qualification pending.

## .114 — master-layer Point Counter

Independent complete Reza report: every selected occurrence, stored master layers, empty masters, own contour totals and fixed400×300 read-only window. Quadratic endpoints are included, correcting the original omission. Native qualification remains pending.

- N128/.110: complete Show All Layers proof candidate, preserving repeated selected parents, stored foreground layer order and trailing newlines. Native acceptance pending.


## N55 original colour-selection candidate

Add the complete Pedro additive different-colour Font-window selection workflow. Preserve initial colours and selection; delegate filtered cell mapping to native GID lookup. Native acceptance pending.

## 2026-10-20 — contour selection candidate (native pending)

Independent Pedro Arilla adaptations add Select Contours, Select Small Contours and Select Partial Contours through shared App immutable plans and lazy selection-only transport. Preserve original path/node order, offcurve inclusion, cross-contour toggles and strict unsigned analytic area. Owned input UI diagnoses invalid/nonfinite/stale sources without clearing selection. Full original/native acceptance, including mixed selection transport outside a single displayed glyph, remains open. Apache attribution and complete terms retained.

## 2026-11-01 — additive selection consumer contract

Update Names consumer regression to require zero selection clears from App
add=True while retaining result order and invalid/stale-input preservation.
Menu bytes and pins unchanged. Native filtered-view and colour mapping remain open.

Matching ordinary Appwheel/sdist0.2.26.dev159+gb1e905b61 each pass all39Names
consumer tests (89combined). Full configured gate4SbhxE:58failed4403passed17skipped,
exit1; exact58failed IDs equal retainedx6Yymo. No production script changed, no
new coverage claim and no cohort acceptance. Evidence retained externally in
issue123/additive-selection-20261101.

## 2026-11-01 — different-colour empty-selection repair

Restore source no-op for empty selection: no CurrentFont getter, glyph-mark reads,
selection writes or history. Selected behavior stays additive. Pure comparison
returns no additions without any selected colour. Source doc and generated page
now qualify the captured API boundary instead of asserting universal inability.
Additional-tools destination pin updated; all173pins,242archived menu scripts and
generated source snapshot match. Scoped review clear.

Focused baseline140passed after adding the missing Fly artifact to the isolated
environment (initial2failed138passed). Four revised/new behavior cases failed
before repair. Final181passed including39Names tests, also181from extracted menu
archive with ordinary installed App0.2.26.dev159+gb1e905b61/Fly0.2.2.dev7. Full
configured gatexxTuhA:58failed4405passed17skipped; all58failed node IDs equal4SbhxE.
Complete changed menu95.56%combined coverage, unchanged80%gate. No native proof.

Commands through rtk proxy (candidate cwd; extracted bundle for archive check):
Set ISSUE123_EVIDENCE to the private evidence root; exact local commands remain
in the controller receipt.
env -u PYTHONPATH -u SCRIPTMIX_APP_SOURCE PYTHONDONTWRITEBYTECODE=1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$ISSUE123_EVIDENCE/colour-selection-20261101/env/bin/python"
-I -B -m pytest -q -p no:cacheprovider tests/test_issue122_G1.py tests/test_names.py
(exit0); root .metaswarm/quality.sh coverage candidate fontlab-python-scriptmix
with normal PATH (exit1). Logs and exact archive hashes retained externally.

Wait, but: the original uses displayed filtered cells. This candidate still uses
all font glyphs for nonempty selection. No verified displayed-list binding was
found in inspected C++/captured PythonQt/legacy FL/MCP interfaces; no substitute
is declared equivalent. Mark mapping and complete native preservation stay open.

### 2026-11-01 — Reconcile Common Glyphs status after consolidation

Retained the pending status correction's essential finding: Common Glyphs is
a partial candidate, not an accepted complete port. The consolidated code now
contains the production-name and first-open-font text repairs that were absent
from that earlier status worktree. The backlog therefore records the current
remaining charcoal, native rendering, clipboard and preservation holds without
reintroducing the stale missing-feature claims. No script, source identity or
provenance hash changed. The original worktree and its historical notes remain
untouched. Validation: exact source identity and one-row status check passed;
the normal pre-push suite also runs for this documentation update.


## 2026-11-07 — current icon path-tuple inventory correction

Correct the current icon metadata to 45 observed ordered SVG path tuples: 43 exact installed MaterialX icon path-tuple matches and two unmatched Lucide tuples attributed by the existing pinned SCSS references. The additional installed match is Font Awesome's version caret-down. Its unchanged CSS header identifies Font Awesome Free 7.1.0, Fonticons and CC-BY-4.0 icon terms; the full notice already exists. The official NPM caret SVG has different raw path bytes, so no unmodified-primary SVG, whole-geometry or optimizer-recipe equivalence is claimed. The old known-candidate 42-match review remains historical.

A new regression derives the tuple set from actual HTML/CSS, scans the four installed icon families, checks the unmatched CSS references and caret header, and compares source/generated inventories. It failed against the prior 44 count, then passed with the corrected metadata. All 42 current pipeline tests and complete strict/independent exact-lock output byte/mode checks pass. No runtime, menu hash, generator, dependency, vendor asset, full notice or historical source pin changed. Normal delivery hooks, independent review, actual source/main/output CI and eligible live publication remain separate; no native or installed-product acceptance is added.

Regenerate the committed `docs/` site and its `src_docs/md` source-link pins with the locked docs environment so it includes the TMetrics Window and TGlyph Window pages, and update the pinned counts in `tests_docs` (261 menus and pages, 401 generated-site files, two new search locations). All 42 pipeline tests pass.
