---
this_file: src_docs/md/near-miss-report.md
---

# Close But No Cigar

Select glyphs in a Font or Glyph window, then choose **Scripts → Reports → Close But No Cigar**. The modeless report has selectable text, **Refresh**, and **Close**. It reports suspicions; it does not move nodes or change stem values. It preserves the Output panel.

The complete [menu source](scripts/reports/close-but-no-cigar.md) delegates lazily through `fly.ap.near_miss` to App 0.2.93.dev0 or later. Native FontLab qualification remains pending. Python 3.11 source, ordinary archive installations, independent original-contract controls and standalone Qt checks are separate evidence.

## Selection and master scope

Every selected occurrence is processed in order, including repeated parents. Each parent contributes its literal **first layer**, even when another layer is selected or active. No current-glyph fallback is used. The report resolves that layer's associated named font master and reads that master's PostScript horizontal/vertical stems, ascender, cap height, x height and descender. It never substitutes the active master's data or calls a master/selection writer.

FontLab associates a named layer by the part before `:`, `#` or `@`, as in its `FontMetrics` source. The report requires that name to match exactly one serialized master. Unknown or ambiguous associations refuse the whole report, rather than using FontLab's implicit key-master fallback. Components are omitted, matching the original own-path scope. Own affine element transforms map nodes into layer coordinates.

## Complete original checks

For every own path, segment checks precede node checks, preserving original order:

- Angles strictly within two degrees of 0, 180, 90 or -90 are reported, except exact values. The original asymmetric treatment of negative 180 degrees is retained; no angle normalization is added.
- Horizontal-direction segments near 0/180 compare against every horizontal stem. Vertical-direction segments near ±90 compare against every vertical stem. A length must be strictly between 95% and 105% of a target, and unequal to it. An exact length match to **any** stem suppresses every near-stem message for that orientation. Duplicate stem targets retain duplicate messages.
- Every node, including off-curve handles, receives six position checks: x near zero; y near zero, ascender, cap height, x height and descender. Each test is strictly within two units and excludes exact values. Equal metric targets retain their separate labelled messages.

Line length is the endpoint distance; angle is the endpoint `atan2` in degrees. Cubic length retains glyphmonkey's 50-step repeated `t += 0.02` sampling, including its last sample below 1.0 and exact floating-point arithmetic association. That matters because exact-stem suppression is part of the contract. It is not an analytic curve length.

## Explicit source repairs and refusals

Simon Cozens' helper overrides a cubic's inherited `angle` property with an undecorated method. The original script reads it as a number and can fail on curves. This adaptation repairs that mismatch using the helper's intended endpoint angle. Empty contours safely contribute no segment. The helper's last-to-first starting edge is retained **even on open contours**; the closing-edge suspicion therefore remains visible.

TrueType contours with off-curve controls and malformed non-line/non-cubic runs refuse the complete report. Two quadratic controls must never be interpreted as cubic handles. Generated shapes, projective transforms, unreadable numbers, missing first layers, unknown master association, stale source changes and expired scans also refuse the complete report. No report prefix survives a failed Refresh; restore the source and Refresh again.

## Source and licence

Adapted from Simon Cozens' [GlyphsScripts](https://github.com/simoncozens/GlyphsScripts), `Close But No Cigar.py` and `glyphmonkey.py`, under MIT. Both original hashes and the complete original copyright/permission notice are in `NOTICE` and `additional-tools.json`. The original scripts are not executed or redistributed. The sample migration denominator remains 130; this additional tool is not a native acceptance increment.

[Complete Simon Cozens MIT licence and copyright notice](licenses/simon-cozens-mit.txt).
