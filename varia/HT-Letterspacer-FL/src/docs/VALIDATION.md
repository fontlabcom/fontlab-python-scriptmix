# Validation — 29 October 2026

Runtime: installed FontLab 9 on macOS, embedded CPython 3.11.6 and PythonQt. Upstream revision: `b4ad60bd36284f87edf9f2145d38bbf87b2e9909`.

## Completed

- 18 host-independent unit tests: analytic line/cubic intersections (including tangency and horizontal extrema), golden rectangle spacing, UPM scaling, rule specificity, master overrides, percent scaling, fixed widths, side switches, metrics-key/empty skips, private imports, Unicode/classification mapping and invalid input rejection.
- Full upstream `ExampleFont-Glyphs3.glyphs` with `LetterspacerTestFont_Export.json`: 239 glyphs × 3 masters = 717 layers. **714 computed; 3 empty space layers skipped; no engine exceptions.** Tested in 24-glyph batches because FontLab MCP limits each Python execution to five seconds. Batch run took 13.64 seconds including calls and font-state construction.
- All three real masters returned expected sample values: Regular H 109/109, o 50/50, c 50/31 and Aacute 37/37, using the upstream setup.
- Native writes read back the requested sidebearings and advance widths.
- Synthetic scaled/sheared live component remains at the same coordinates when its base is spaced, within 1e-7 units, including with an active Glyph window and grid rounding enabled. The original rounding preference is restored.
- Italic sign conversion and slanted sidebearings, ordinary pen stroke expansion, fixed advance widths, independent side switches, empty skips, and FontLab history registration.
- Embedded configuration reload and complete native save/reopen in both VFJ and VFC.
- Script UI constructed in FontLab: four tabs, preview rendering, selection and current-tab scope, and native painter registration/removal. The generated UI and Glyph-window overlays were rendered to images and inspected.
- Normal tool-window close leaves FontLab running. Reporter timer and painter are removed on close.
- The upstream checkout remains clean; none of its tracked files were edited.

## Tests to rerun

```
python3 -m unittest discover -s tests -v
```

Run `tests/fontlab_smoke.py` in FontLab's Scripting panel. It creates and closes a dedicated font and temporary VFJ/VFC copies; it does not modify existing fonts.

## Scope of the evidence

The original engine is executed unchanged, but the subsequent native Glyphs 3 comparison is now documented in [PARITY.md](PARITY.md). Ordinary Qt pen stroke extraction passed the live smoke test; complex FontLab brush/effect and Glyphs-specific callback equivalence remains unverified. Alternate/intermediate layers are intentionally excluded. Native history registration was verified; automated end-user Edit → Undo/Redo menu interaction was not performed. See README for the remaining host/UI differences.

## Compact default UI revision

The default launchers now open a 360 × 178 palette matching the original manual tool. The full window is accessible separately as HTLS Manager. Added an explicit tabular advance width and tested it with 595 units. All 19 unit tests and the updated disposable FontLab smoke suite pass. The installed compact launcher was opened and rendered in FontLab for visual inspection; existing user font content was not changed during UI validation.

## Native parity follow-up

21 unit tests and the native FontLab smoke suite pass after fixing scanline endpoints, legacy-name classification and fixed-width result reporting. The detailed cross-host results and historical v1 differences are in [PARITY.md](PARITY.md).
