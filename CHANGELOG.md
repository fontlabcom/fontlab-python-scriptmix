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
the old code (genuine RED retained), then passed after this fix. No native run.
