---
this_file: CHANGELOG.md
---

# Changelog

## Unreleased

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
