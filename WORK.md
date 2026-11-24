---
this_file: WORK.md
---

## Current state

Scriptmix distributes FontLab menu scripts and publishes documentation through GitHub Pages. It has no PyPI upload workflow.

The latest merged-source runtime run passed 5,282 tests with six skips. The strict documentation build stopped on `fly.css` and `fly-tokens.css`. The lock and installed theme are at 0.2.1, but the committed inventories still describe 0.1.1. The corresponding docs run had 49 passes and 13 failures. Reconcile the inventories and rebuild before qualifying the 0.2.1 output.

The planning audit verified the rendered source links and hashes for all 197 current menu scripts. The source-snapshot and batch-recipe checks passed all 13 tests. The installer matches the reviewed Instamix 1.0.18 template (`dd47ed44`). Consumer CI, released archives and native execution remain open.

PLAN and TODO retain the installed, history, save/reopen and delivery checks. D43 native admission and private Pages remain held. Issue 123 remains paused. The previous round log is available at `5d066804:WORK.md`.
